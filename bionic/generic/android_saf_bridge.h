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
bool IsVirtualPath(const std::filesystem::path& path);
std::optional<std::filesystem::path> Resolve(std::string_view guest_path);
bool List(std::string_view guest_directory, std::vector<Entry>& entries);
// Lightweight broker STAT: no provider file descriptor or data copy.
bool StatPath(std::string_view guest_path, bool* is_directory = nullptr);
std::optional<int> DuplicateFd(const std::filesystem::path& path);
void Shutdown();
}
