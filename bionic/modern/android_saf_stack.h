// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
// shadPS4 0.21.1 moved all game-file operations onto IBackend. The original
// SafFsBackend predates that migration and only provided Resolve/Iterate.
// Retain the real BSF1 broker and independent SCM_RIGHTS file descriptors;
// adapt the broker to the modern mount stack, without staging whole games.
#include <cstdint>
#include <filesystem>
#include <limits>
#include <memory>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include "core/file_sys/backends/host_fs.h"
#include "core/file_sys/ifile.h"
#include "core/file_sys/saf_fs_backend.h"

namespace Core::FileSys {

class SafStackDirectory final : public IDirectory {
public:
    explicit SafStackDirectory(std::vector<DirEntry> entries)
        : entries_(std::move(entries)) {}

    bool Next(DirEntry& out) override {
        if (cursor_ >= entries_.size()) return false;
        out = entries_[cursor_++];
        return true;
    }
    void Rewind() override { cursor_ = 0; }

private:
    std::vector<DirEntry> entries_;
    std::size_t cursor_{};
};

class SafStackBackend final : public IBackend {
public:
    SafStackBackend(std::shared_ptr<SafFsBackend> broker, std::string mount_root)
        : broker_(std::move(broker)), mount_root_(std::move(mount_root)) {}

    bool Exists(std::string_view relative) override {
        const auto guest = GuestPath(relative);
        if (guest.empty()) return false;
        SafEntry entry;
        if (broker_->StatEntry(guest, entry)) return true;
        const auto resolved = broker_->Resolve(guest);
        std::error_code ec;
        return !resolved.empty() && std::filesystem::exists(resolved, ec);
    }

    bool IsDirectory(std::string_view relative) override {
        const auto guest = GuestPath(relative);
        if (guest.empty()) return false;
        SafEntry entry;
        if (broker_->StatEntry(guest, entry)) return entry.is_directory;
        const auto resolved = broker_->Resolve(guest);
        std::error_code ec;
        return !resolved.empty() && std::filesystem::is_directory(resolved, ec);
    }

    bool Stat(std::string_view relative, FileStat& out) override {
        const auto guest = GuestPath(relative);
        if (guest.empty()) return false;
        SafEntry entry{};
        if (!broker_->StatEntry(guest, entry)) {
            const auto resolved = broker_->Resolve(guest);
            if (resolved.empty()) return false;
            std::error_code ec;
            if (!std::filesystem::exists(resolved, ec) || ec) return false;
            entry.is_directory = std::filesystem::is_directory(resolved, ec);
            entry.size = entry.is_directory ? 0 : std::filesystem::file_size(resolved, ec);
            if (ec) return false;
        }
        out = FileStat{};
        out.size = entry.size;
        out.is_directory = entry.is_directory;
        // Stable guest-local inode for broker-backed entries. No host inode
        // is assumed for DocumentsProvider paths.
        std::uint32_t h = 2166136261u;
        for (const unsigned char c : guest) {
            h ^= c;
            h *= 16777619u;
        }
        out.inode = h ? h : 1;
        out.mtime_sec = static_cast<s64>(entry.mtime / 1000);
        out.mtime_nsec = static_cast<s64>((entry.mtime % 1000) * 1000000);
        out.atime_sec = out.ctime_sec = out.mtime_sec;
        out.atime_nsec = out.ctime_nsec = out.mtime_nsec;
        return true;
    }

    std::unique_ptr<IFile> Open(std::string_view relative,
                                Common::FS::FileAccessMode mode) override {
        if (mode != Common::FS::FileAccessMode::Read) return nullptr;
        const auto guest = GuestPath(relative);
        if (guest.empty()) return nullptr;
        const auto host = broker_->Resolve(guest);
        if (host.empty()) return nullptr;
        std::error_code ec;
        if (!std::filesystem::is_regular_file(host, ec) || ec) return nullptr;
        // HostFile calls IOFile, which receives a NEW broker fd through
        // SetFdOpenHook. We never share read offsets between game handles.
        auto file = std::make_unique<HostFile>(host, mode, true);
        if (!file->IsOpen()) return nullptr;
        return file;
    }

    std::unique_ptr<IDirectory> OpenDir(std::string_view relative) override {
        const auto guest = GuestPath(relative);
        if (guest.empty()) return nullptr;
        std::vector<SafEntry> source;
        if (!broker_->ListEntries(guest, source)) return nullptr;
        std::vector<DirEntry> entries;
        entries.reserve(source.size());
        for (const auto& entry : source) {
            if (entry.name.empty() || entry.name == "." || entry.name == ".." ||
                entry.name.find('/') != std::string::npos ||
                entry.name.find('\\') != std::string::npos) continue;
            entries.push_back(DirEntry{.name = entry.name,
                                       .is_directory = entry.is_directory,
                                       .size = entry.size});
        }
        return std::make_unique<SafStackDirectory>(std::move(entries));
    }

    std::optional<std::vector<u8>> ReadFile(std::string_view relative) const override {
        const auto guest = GuestPath(relative);
        if (guest.empty()) return std::nullopt;
        const auto host = broker_->Resolve(guest);
        if (host.empty()) return std::nullopt;
        HostFile file(host, Common::FS::FileAccessMode::Read, true);
        if (!file.IsOpen()) return std::nullopt;
        const auto n = file.Size();
        if (n > std::numeric_limits<std::size_t>::max()) return std::nullopt;
        std::vector<u8> data(static_cast<std::size_t>(n));
        if (n && file.Read(data.data(), n) != static_cast<s64>(n))
            return std::nullopt;
        return data;
    }

    bool IsReadOnly() const override { return true; }
    std::filesystem::path RootPath() const override {
        return broker_->Resolve(mount_root_);
    }
    std::optional<std::filesystem::path> RootHostPath() const override {
        // A SAF mount is not a real host directory. Only Resolve() returns
        // an individual staging path; never expose the mirror as a game root.
        return std::nullopt;
    }
    void InvalidateCache(std::string_view = "") override {
        // No negative metadata cache. The Java broker is authoritative.
    }

private:
    std::string GuestPath(std::string_view relative) const {
        if (relative.empty() || relative == ".") return mount_root_;
        const std::filesystem::path fragment(relative);
        if (fragment.is_absolute()) return {};
        for (const auto& component : fragment) {
            if (component == "..") return {};
        }
        return mount_root_ + "/" + std::string(relative);
    }

    std::shared_ptr<SafFsBackend> broker_;
    std::string mount_root_;
};

} // namespace Core::FileSys
