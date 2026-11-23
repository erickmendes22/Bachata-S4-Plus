#pragma once
#include <filesystem>
#include <optional>
#include <string>
#include <string_view>
#include <vector>
namespace BachataSaf {
struct Entry { std::string name; bool directory{}; unsigned long long size{}; long long modified{}; };
bool Configure(const std::string& socket, const std::string& token,
               const std::filesystem::path& game_root, const std::filesystem::path& storage_root);
bool Enabled();
// Preserve the working Release FIOS2 MountAlias names in Android SAF guest paths.
void RegisterGuestAlias(std::string_view source_guest, std::string_view alias_guest);
bool IsVirtualPath(const std::filesystem::path& path);
std::optional<std::filesystem::path> Resolve(std::string_view guest_path);
bool List(std::string_view guest_directory, std::vector<Entry>& entries);
// Lightweight broker STAT: no provider file descriptor or data copy.
bool StatPath(std::string_view guest_path, bool* is_directory = nullptr);
// Direct independent provider fd for 0.18.1 IFile, matching Release SafFsBackend.
std::optional<int> OpenFd(std::string_view guest_path);
std::optional<int> DuplicateFd(const std::filesystem::path& path);
void Shutdown();
}
