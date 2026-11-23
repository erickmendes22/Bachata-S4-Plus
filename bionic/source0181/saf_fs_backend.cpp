// SPDX-FileCopyrightText: Copyright 2026 Bachata S4+ contributors
// SPDX-License-Identifier: GPL-2.0-or-later

#include "core/file_sys/backends/saf_fs_backend.h"
#include "android_saf_bridge.h"
#include <algorithm>
#include <cerrno>
#include <cstdint>
#include <limits>
#include <mutex>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include "common/logging/log.h"

namespace Core::FileSys {
namespace {

// A counterpart to Release 0.2.6/0.2.7 SafFsBackend::Open:
// - one broker-provided independent read-only descriptor for each guest open,
// - no synthesized /proc/self/fd symlink or reliance on a host filesystem,
// - positional reads and read-only copy-mmap via IFile,
// - fd lifetime tied to this IFile rather than a separate 512-entry cache.
//
// Multiple threads can read the same PS4 asset without sharing a file cursor.
class SafGuestFile final : public IFile {
public:
    explicit SafGuestFile(int owned_fd) : fd{owned_fd} {
        struct stat st{};
        if (fd >= 0 && ::fstat(fd, &st) == 0 && S_ISREG(st.st_mode) && st.st_size >= 0) {
            size = static_cast<u64>(st.st_size);
            valid = true;
        }
    }

    ~SafGuestFile() override {
        if (fd >= 0) ::close(fd);
    }

    s64 Read(void* dst, u64 bytes) override {
        if (!valid || (!dst && bytes != 0)) return -1;
        std::scoped_lock lock{cursor_mutex};
        if (cursor >= size || bytes == 0) return 0;
        const u64 length = std::min<u64>(
            std::min<u64>(bytes, size - cursor),
            static_cast<u64>(std::numeric_limits<ssize_t>::max()));
        if (cursor > static_cast<u64>(std::numeric_limits<off_t>::max())) return -1;
        ssize_t n;
        do {
            n = ::pread(fd, dst, static_cast<size_t>(length), static_cast<off_t>(cursor));
        } while (n < 0 && errno == EINTR);
        if (n > 0) cursor += static_cast<u64>(n);
        return static_cast<s64>(n);
    }

    s64 Write(const void*, u64) override { return -1; }

    bool Seek(s64 move, Common::FS::SeekOrigin origin) override {
        std::scoped_lock lock{cursor_mutex};
        const u64 origin_pos =
            origin == Common::FS::SeekOrigin::SetOrigin ? 0 :
            origin == Common::FS::SeekOrigin::CurrentPosition ? cursor : size;
        if (origin_pos > static_cast<u64>(std::numeric_limits<s64>::max()))
            return false;
        const s64 base = static_cast<s64>(origin_pos);
        if ((move > 0 && base > std::numeric_limits<s64>::max() - move) ||
            (move < 0 && base < std::numeric_limits<s64>::min() - move))
            return false;
        const s64 target = base + move;
        if (target < 0 || static_cast<u64>(target) > size) return false;
        cursor = static_cast<u64>(target);
        return true;
    }

    u64 Tell() const override {
        std::scoped_lock lock{cursor_mutex};
        return cursor;
    }

    u64 Size() const override { return size; }
    bool Flush() override { return valid; }
    bool IsOpen() const override { return valid; }

    MmapPolicy GetMmapPolicy() const override { return MmapPolicy::Copy; }

    bool Map(u8* addr, u64 count, u64 offset, u32 raw_prot,
             const FileMapContext& ctx) override {
        if (!valid || !addr || offset > size || count > size - offset ||
            offset > static_cast<u64>(std::numeric_limits<off_t>::max())) {
            return false;
        }
        ctx.map_anonymous(addr, count);
        u64 copied = 0;
        while (copied < count) {
            const u64 remaining = count - copied;
            const u64 part = std::min<u64>(remaining, 4u * 1024u * 1024u);
            const u64 pos = offset + copied;
            if (pos > static_cast<u64>(std::numeric_limits<off_t>::max())) return false;
            ssize_t got;
            do {
                got = ::pread(fd, addr + copied, static_cast<size_t>(part),
                              static_cast<off_t>(pos));
            } while (got < 0 && errno == EINTR);
            if (got <= 0) return false;
            copied += static_cast<u64>(got);
        }
        ctx.protect(addr, count, raw_prot);
        return true;
    }

    void Stat(FileStat& out) override {
        out = {};
        out.size = size;
        out.is_directory = false;
        struct stat st{};
        if (valid && ::fstat(fd, &st) == 0) {
            out.mtime_sec = st.st_mtim.tv_sec;
            out.mtime_nsec = st.st_mtim.tv_nsec;
            out.atime_sec = st.st_atim.tv_sec;
            out.atime_nsec = st.st_atim.tv_nsec;
            out.ctime_sec = st.st_ctim.tv_sec;
            out.ctime_nsec = st.st_ctim.tv_nsec;
        }
    }

    bool IsReadOnly() const override { return true; }
    bool IsWriteOnly() const override { return false; }

private:
    int fd{-1};
    u64 size{};
    bool valid{};
    mutable std::mutex cursor_mutex;
    u64 cursor{};
};
} // namespace

std::unique_ptr<IFile> OpenSafGuestFile(std::string_view guest_path) {
    const auto fd = BachataSaf::OpenFd(guest_path);
    if (!fd) return {};
    auto file = std::make_unique<SafGuestFile>(*fd);
    if (!file->IsOpen()) {
        LOG_WARNING(Kernel_Fs,
                    "BACHATA_RELEASE026_SAF_FD_INVALID guest='{}'", guest_path);
        return {};
    }
    LOG_TRACE(Kernel_Fs, "BACHATA_RELEASE026_SAF_FD_OPEN guest='{}' bytes={}",
              guest_path, file->Size());
    return file;
}
} // namespace Core::FileSys
