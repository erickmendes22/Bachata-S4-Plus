// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <array>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <span>
#include <vector>

namespace Vulkan::DriverCacheFile {
constexpr std::size_t MaxBytes = 128u << 20;
struct Identity {
    std::uint32_t vendor{}, device{}, driver{};
    std::array<std::uint8_t, 16> uuid{};
};
inline std::uint64_t Checksum(std::span<const std::uint8_t> data) {
    std::uint64_t hash = 14695981039346656037ull;
    for (auto byte : data) { hash ^= byte; hash *= 1099511628211ull; }
    return hash;
}
inline bool ValidPayload(std::span<const std::uint8_t> data, const Identity& id) {
    if (data.size() < 32 || data.size() > MaxBytes) return false;
    std::array<std::uint32_t, 4> header{};
    std::memcpy(header.data(), data.data(), 16);
    return header[0] >= 32 && header[0] <= data.size() && header[1] == 1 &&
           header[2] == id.vendor && header[3] == id.device &&
           std::memcmp(data.data() + 16, id.uuid.data(), 16) == 0;
}
inline std::vector<std::uint8_t> Encode(std::span<const std::uint8_t> data, const Identity& id) {
    if (!ValidPayload(data, id)) return {};
    std::vector<std::uint8_t> out;
    const auto append = [&](auto value) {
        auto* bytes = reinterpret_cast<const std::uint8_t*>(&value);
        out.insert(out.end(), bytes, bytes + sizeof(value));
    };
    append(std::uint32_t{0x31434447}); // GDC1
    append(id.vendor); append(id.device); append(id.driver);
    out.insert(out.end(), id.uuid.begin(), id.uuid.end());
    append(std::uint64_t(data.size())); append(Checksum(data));
    out.insert(out.end(), data.begin(), data.end());
    return out;
}
inline std::vector<std::uint8_t> Decode(std::span<const std::uint8_t> file, const Identity& id) {
    if (file.size() < 80 || file.size() > MaxBytes + 48) return {};
    std::array<std::uint32_t, 4> header{};
    std::uint64_t size{}, hash{};
    std::memcpy(header.data(), file.data(), 16);
    std::memcpy(&size, file.data() + 32, 8); std::memcpy(&hash, file.data() + 40, 8);
    if (header != std::array<std::uint32_t, 4>{0x31434447, id.vendor, id.device, id.driver} ||
        std::memcmp(file.data() + 16, id.uuid.data(), 16) || size != file.size() - 48) return {};
    const auto data = file.subspan(48);
    if (!ValidPayload(data, id) || Checksum(data) != hash) return {};
    return {data.begin(), data.end()};
}
inline std::vector<std::uint8_t> Load(const std::filesystem::path& path, const Identity& id) {
    std::ifstream file(path, std::ios::binary | std::ios::ate);
    if (!file) return {};
    const auto size = file.tellg();
    if (size < 80 || size > std::streamoff(MaxBytes + 48)) return {};
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(size));
    file.seekg(0);
    if (!file.read(reinterpret_cast<char*>(bytes.data()), std::streamsize(bytes.size()))) return {};
    return Decode(bytes, id);
}
inline bool Save(const std::filesystem::path& path, std::span<const std::uint8_t> data,
                 const Identity& id) {
    const auto bytes = Encode(data, id);
    if (bytes.empty()) return false;
    std::error_code error;
    std::filesystem::create_directories(path.parent_path(), error);
    if (error) return false;
    auto temporary = path; temporary += ".tmp";
    {
        std::ofstream file(temporary, std::ios::binary | std::ios::trunc);
        if (!file.write(reinterpret_cast<const char*>(bytes.data()), std::streamsize(bytes.size())) ||
            !(file.flush())) return false;
    }
    std::filesystem::rename(temporary, path, error);
    if (error) { std::error_code ignored; std::filesystem::remove(temporary, ignored); }
    return !error;
}
} // namespace Vulkan::DriverCacheFile
