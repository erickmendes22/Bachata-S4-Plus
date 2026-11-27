"""Port donor bounded host-bounce reads and atomic condvar wake publication.
ISS/TLOU runtime_file.c full_io and runtime_mutex.c host condvar semantics.
Preserve FEX memory invalidation, the guest mutex ABI and SAF file descriptors.
"""
from pathlib import Path

IO = r'''#pragma once
#include <algorithm>
#include <cstdint>
#include <cerrno>
#include <limits>
#include <vector>
namespace BachataDonorIO {
using Count = std::uint64_t;
using Result = std::int64_t;
constexpr Count Chunk = 4u << 20;
constexpr Count Max = std::numeric_limits<Result>::max();
template<class Read, class Copy, class Error>
Result FullRead(Count size, Read read, Copy copy, Error error) {
    if (size > Max) { error(EINVAL); return -1; }
    Count done = 0;
    unsigned retries = 0;
    while (done < size) {
        const Count want = std::min(Chunk, size - done);
        errno = 0;
        const Result got = read(want);
        const int e = errno;
        if (got < 0) {
            if ((e == EINTR || e == EFAULT) && ++retries < 64) continue;
            if (done) return static_cast<Result>(done);
            error(e ? e : EIO);
            return -1;
        }
        if (static_cast<Count>(got) > want) {
            if (done) return static_cast<Result>(done);
            error(EIO);
            return -1;
        }
        if (!got) return static_cast<Result>(done);
        copy(done, static_cast<Count>(got));
        done += static_cast<Count>(got);
        retries = 0;
    }
    return static_cast<Result>(done);
}
template<class Iov, class Read, class Error>
Result ReadVector(const Iov* iov, int count, Read read, Error error) {
    if (count < 0 || count > 1024 || (!iov && count)) {
        error(EINVAL); return -1;
    }
    Count total = 0;
    for (int i = 0; i < count; ++i) {
        if (iov[i].iov_len > Max - total) { error(EINVAL); return -1; }
        total += iov[i].iov_len;
    }
    Result done = 0;
    for (int i = 0; i < count; ++i) {
        const Count size = iov[i].iov_len;
        if (!size) continue;
        const Result got = read(iov[i].iov_base, size);
        if (got < 0) return done ? done : -1;
        done += got;
        if (static_cast<Count>(got) != size) break;
    }
    return done;
}
}
'''

def apply(root):
    src=Path(root)/'src'
    def edit(rel,a,b,n=1):
        p=src/rel;s=p.read_text()
        if s.count(a)!=n: raise RuntimeError(f'{rel}: expected {n} anchors, found {s.count(a)}: {a[:90]}')
        p.write_text(s.replace(a,b))
    k='core/libraries/kernel/'
    (src/(k+'bachata_donor_io.h')).write_text(IO)
    f=k+'file_system.cpp'
    edit(f,'#include <map>','''#include <map>
#include <cerrno>
#include <limits>
#include "common/elf_info.h"
#include "core/libraries/playgo/bachata_installed_package.h"
#include "core/libraries/kernel/bachata_donor_io.h"''')
    edit(f,'static thread_local std::vector<u8> file_buf{};','''static thread_local std::vector<u8> file_buf{};
static bool DonorRegularIO() {
    return BachataBoot::InstalledPackageTitle(Common::ElfInfo::Instance().GameSerial());
}''')
    edit(f,'''    const auto* memory = Core::Memory::Instance();
    // Invalidate up to the actual number of bytes that could be read.''','''    const auto* memory = Core::Memory::Instance();
    if (DonorRegularIO()) {
        if (!buf && nbytes) { *__Error() = POSIX_EFAULT; return -1; }
        if (nbytes && reinterpret_cast<VAddr>(buf) >
                         std::numeric_limits<VAddr>::max() - (nbytes - 1)) {
            *__Error() = POSIX_EFAULT;
            return -1;
        }
        return BachataDonorIO::FullRead(nbytes, [&](u64 want) {
            file_buf.resize(want);
            return file->Read(file_buf.data(), want);
        }, [&](u64 offset, u64 got) {
            auto* dst = static_cast<u8*>(buf) + offset;
            memory->InvalidateMemory(reinterpret_cast<VAddr>(dst), got);
            std::memcpy(dst, file_buf.data(), got);
        }, [](int e) { SetPosixErrno(e); });
    }
    // Invalidate up to the actual number of bytes that could be read.''')
    edit(f,'''    const auto remaining = file->GetSize() - file->Tell();
    memory->InvalidateMemory(reinterpret_cast<VAddr>(buf), std::min<u64>(nbytes, remaining));
    if (file_buf.capacity() < nbytes) {
        file_buf.reserve(nbytes);
    }''','''    const auto pos = file->Tell();
    if (pos < 0) { *__Error() = POSIX_EIO; return -1; }
    const auto size = file->GetSize();
    const auto remaining = static_cast<u64>(pos) < size ? size - pos : 0;
    memory->InvalidateMemory(reinterpret_cast<VAddr>(buf), std::min<u64>(nbytes, remaining));
    file_buf.resize(nbytes);''')
    edit(f,'''    s64 total_read = 0;
    for (s32 i = 0; i < iovcnt; i++) {
        total_read += ReadFile(file, iov[i].iov_base, iov[i].iov_len);
    }
    return total_read;''','''    return BachataDonorIO::ReadVector(iov, iovcnt,
        [&](void* dst, u64 bytes) { return ReadFile(file, dst, bytes); },
        [](int e) { SetPosixErrno(e); });''',2)
    edit(f,'''    const s64 pos = file->Tell();
    SCOPE_EXIT''','''    const s64 pos = file->Tell();
    if (pos < 0) { *__Error() = POSIX_EIO; return -1; }
    SCOPE_EXIT''')
    edit('core/file_sys/backends/saf_fs_backend.cpp',
         'if (target < 0 || static_cast<u64>(target) > size) return false;',
         'if (target < 0) { errno = EINVAL; return false; }')
    edit('core/file_sys/backends/saf_fs_backend.cpp',
         'if (!valid || (!dst && bytes != 0)) return -1;',
         'if (!valid) { errno = EBADF; return -1; }\n        if (!dst && bytes != 0) { errno = EFAULT; return -1; }')
    edit('common/io_file.h','    template <typename T>\n    size_t ReadRaw(void* data, size_t size) const {',
         '    bool HasReadError() const { return file && std::ferror(file); }\n    void ClearReadError() const { if (file) std::clearerr(file); }\n\n    template <typename T>\n    size_t ReadRaw(void* data, size_t size) const {')
    edit('core/file_sys/backends/host_fs.cpp',
         '    return static_cast<s64>(m_file.ReadRaw<u8>(dst, size));',
         '''    errno = 0;
    const auto got = m_file.ReadRaw<u8>(dst, size);
    if (!got && m_file.HasReadError()) {
        const int e = errno ? errno : EIO;
        m_file.ClearReadError();
        errno = e;
        return -1;
    }
    return static_cast<s64>(got);''')
    edit('core/file_sys/backends/host_fs.cpp','#include "core/file_sys/backends/host_fs.h"',
         '#include "core/file_sys/backends/host_fs.h"\n#include <cerrno>')
    c=k+'threads/condvar.cpp'
    edit(c,'#include <cstring>','''#include <cstring>
#include <algorithm>
#include "common/elf_info.h"
#include "core/libraries/playgo/bachata_installed_package.h"''')
    edit(c,'static std::mutex CondStaticLock;','''static std::mutex CondStaticLock;
static bool DonorCondWake() {
    return BachataBoot::InstalledPackageTitle(Common::ElfInfo::Instance().GameSerial());
}''')
    edit(c,'''        if (curthread->wchan == nullptr) {
            error = 0;''','''        if (curthread->wchan == nullptr) {
            // For immediate publication the token already exists under this lock.
            // A timeout racing a signal must not carry the token into another wait.
            if (DonorCondWake() && error == POSIX_ETIMEDOUT) curthread->ClearWake();
            error = 0;''')
    edit(c,'''    Pthread* td = thread ? thread : sq->sq_blocked.front();

    PthreadMutex* mp = td->mutex_obj;''','''    if (thread && std::find(sq->sq_blocked.begin(), sq->sq_blocked.end(), thread)
                      == sq->sq_blocked.end()) {
        SleepqUnlock(this);
        return 0;
    }
    Pthread* td = thread ? thread : sq->sq_blocked.front();
    if (DonorCondWake()) {
        has_user_waiters = SleepqRemove(sq, td);
        td->wake_sema.release();
        SleepqUnlock(this);
        return 0;
    }

    PthreadMutex* mp = td->mutex_obj;''')
    edit(c,'''    SleepqDrop(sq, drop_cb, &ba);
    has_user_waiters = false;''','''    if (DonorCondWake()) {
        SleepqDrop(sq, [](Pthread* td, void*) { td->wake_sema.release(); }, nullptr);
    } else {
        SleepqDrop(sq, drop_cb, &ba);
    }
    has_user_waiters = false;''')
