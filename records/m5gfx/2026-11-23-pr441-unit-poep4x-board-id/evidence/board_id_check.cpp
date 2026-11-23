#include <cstdint>
#include "lgfx/boards.hpp"

static_assert(static_cast<std::uint32_t>(lgfx::board_M5UnitPoEP4X) == 158u,
              "board id value must be 158");
static_assert(lgfx::board_M5UnitPoEP4X != lgfx::board_M5StampP4XHub,
              "must not collide with 157");
static_assert(lgfx::board_M5UnitPoEP4X != lgfx::board_M5UnitPoEP4,
              "must not collide with 148");
static_assert(lgfx::board_M5UnitPoEP4X != lgfx::board_M5UnitPoEP4DisplayOut,
              "must not collide with external-display id 201");
static_assert(lgfx::board_M5UnitPoEP4X < lgfx::board_M5AtomDisplay,
              "must stay in the non-display block below 192");

int main() { return 0; }
