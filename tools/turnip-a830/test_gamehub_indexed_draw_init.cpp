// Self-contained ARM64 parity checks for 0x99bdc0..0x99be14.
// Build: c++ -std=c++17 -Wall -Wextra -Werror -Itools/turnip-a830 \
//    tools/turnip-a830/test_gamehub_indexed_draw_init.cpp -o /tmp/test-indexed && /tmp/test-indexed
#include "gamehub_indexed_draw_init_verified.hpp"
using gamehub::a8xx::reconstruct_indexed_draw_init;
static_assert(reconstruct_indexed_draw_init(0, 8, 1).limit == 0x600);
static_assert(reconstruct_indexed_draw_init(1, 8, 0).limit == 0x600);
static_assert(reconstruct_indexed_draw_init(1, 8, 1).limit == 0x1800);
static_assert(reconstruct_indexed_draw_init(1, 8, 1).enhanced_indexed_draws == 1);
static_assert(reconstruct_indexed_draw_init(1, 7, 1).limit == 0x1800);
static_assert(reconstruct_indexed_draw_init(1, 7, 1).enhanced_indexed_draws == 0);
static_assert(reconstruct_indexed_draw_init(1, 8, 2).enhanced_indexed_draws == 2);
int main() { return 0; }
