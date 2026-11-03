#include "../gamehub_sync_renderpass_cache_accessor_verified.hpp"
#include <array>
#include <cassert>
#include <cstdint>

using namespace gamehub::a830;

int main() {
    static_assert(sync_renderpass_cache_option_offset == 0x4c);
    static_assert(advertise_wave32_option_offset == 0x4b);
    std::array<uint8_t, 0x60> options{};
    assert(!*read_sync_renderpass_cache(options));
    options[0x4b] = 1; // Wave32 compatibility only.
    assert(!*read_sync_renderpass_cache(options));
    options[0x4c] = 1; // Real sync cache flag.
    assert(*read_sync_renderpass_cache(options));
    options[0x4c] = 0;
    assert(!*read_sync_renderpass_cache(options));
    std::array<uint8_t, 0x4c> truncated{};
    assert(!read_sync_renderpass_cache(truncated).has_value());
}
