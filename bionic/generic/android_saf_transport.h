#pragma once
#include <cstdint>
#include <string>
#include <string_view>
#include <vector>
namespace BachataSaf::Protocol {
struct Reply { int status = -1; int fd = -1; std::vector<std::uint8_t> bytes; };
Reply Request(const std::string& socket, const std::string& token, int operation,
              std::string_view relative);
std::uint16_t Read16(const std::uint8_t* p);
std::uint32_t Read32(const std::uint8_t* p);
std::uint64_t Read64(const std::uint8_t* p);
}
