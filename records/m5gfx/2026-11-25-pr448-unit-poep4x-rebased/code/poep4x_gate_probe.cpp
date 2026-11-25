// Host probe for m5stack/M5GFX#448 (Unit PoE-P4X rebased #444).
//
// Not part of the M5GFX tree: compile against a checkout of the PR head.
// It drives unitpoep4_detector_t::confirm() with a bit-banged MDIO slave
// model and a per-case chip revision, which the in-tree fixtures do not do
// (test/board_detect/fixtures/p4.txt only dumps descriptors, so the 158 entry
// appears regardless of revision).
//
// build_and_run.sh <path-to-M5GFX-checkout>

#define CONFIG_IDF_TARGET_ESP32P4 1
#define CONFIG_IDF_TARGET "esp32p4"
#include <cassert>
#include <cstdio>
#include <initializer_list>
#include "support/runtime.hpp"
#include "support/probes.hpp"
#include "support/dsi_devices.hpp"
#include "board_detect/m5/esp32p4.inl"
#include "support/display_backend.hpp"

namespace m5gfx {
namespace board_detect {
namespace m5 {
construct_status_t construct_detected_board(const board_result_t &result, display_parts_t *parts) {
  return construct_board(esp32p4_boards, result, parts);
}
void destroy_display_parts(display_parts_t *parts) {
  assert(!parts->bus && !parts->panel && !parts->light && !parts->touch);
}
}
}
static unsigned get_pkg_ver() { return 0; }
static const char LIBRARY_NAME[] = "host";
static const int detection_i2c_port = -1;
using lgfx::board_t;
#include "board_detect/detection_package.inl"
#include "board_detect/detection_integration.inl"
} // namespace m5gfx
using namespace m5gfx::board_detect;
using namespace m5gfx::board_detect::m5;

namespace {
// Minimal MDIO slave for unitpoep4_detail::read_phy_register().
// Each register read performs 64 preamble + 2 ST + 5 PHYAD + 5 REGAD driven
// bits, then 19 pin_read(mdio) calls: TA Z, TA 0, 16 data bits (MSB first),
// one trailing bit. Register 2 is read first, then register 3.
struct mdio_phy_t {
  int reg2 = 0, reg3 = 0;
  int reads = 0;
  bool respond = true;
  const int mdio = unitpoep4_detail::mdio;

  bool operator()(int pin) {
    if (pin != mdio) { return true; }
    if (!respond) { return true; } // no slave: TA stays high
    const int slot = reads % 19;
    const int reg = (reads / 19) % 2 == 0 ? 2 : 3;
    const unsigned value = unsigned(reg == 2 ? reg2 : reg3);
    ++reads;
    if (slot == 1) { return false; } // TA low: slave responds
    if (slot >= 2 && slot < 18) {
      return ((value >> (15 - (slot - 2))) & 1u) != 0;
    }
    return true;
  }
  void reset() { reads = 0; }
};

// Confirms the Unit PoE-P4 detector with the given silicon revision and hint.
// Returns the reported board id; 0 when confirm() rejects the board.
board_id_t confirm_board(unsigned revision, board_id_t hint, bool phy_present,
                         unsigned *warnings)
{
  host_hardware::reset();
  host_probes::reset();
  host_chip::revision = static_cast<int>(revision);
  mdio_phy_t phy;
  phy.reg2 = 0x0243; // IP101 PHY ID, as on Unit PoE-P4
  phy.reg3 = 0x0C54;
  phy.respond = phy_present;
  host_hardware::input = [&](int pin, int, bool) { return phy(pin); };

  const std::int8_t watched[] = {unitpoep4_detail::mdc, unitpoep4_detail::mdio};
  detection_transaction_t transaction(pins(watched), no_pins(), false);
  probe_ctx_t ctx;
  ctx.transaction = &transaction;
  ctx.probe_port = -1;
  ctx.hint = hint;
  ctx.attempt = 0;
  board_result_t result;
  phy.reset(); // ignore transaction snapshot reads
  const bool matched = unitpoep4_detector.confirm(ctx, &result);
  assert(matched == phy_present);
  if (warnings != nullptr) { *warnings = host_hardware::warnings; }
  return matched ? result.def->id : board_id_unknown;
}
} // namespace

int main()
{
  using lgfx::board_t;
  const board_id_t poep4 = static_cast<board_id_t>(board_t::board_M5UnitPoEP4);
  const board_id_t poep4x = static_cast<board_id_t>(board_t::board_M5UnitPoEP4X);
  unsigned cases = 0;

  // 1) Revision gate: < 300 is PoE-P4, >= 300 is PoE-P4X.
  const struct { unsigned revision; board_id_t expected; } gate[] = {
    {0, poep4}, {100, poep4}, {200, poep4}, {299, poep4},
    {300, poep4x}, {301, poep4x}, {399, poep4x},
  };
  for (const auto &row : gate) {
    const board_id_t got = confirm_board(row.revision, board_id_unknown, true, nullptr);
    std::printf("revision %3u -> board %u\n", row.revision, unsigned(got));
    assert(got == row.expected);
    ++cases;
  }

  // 2) A disagreeing saved hint is overridden and warned once.
  {
    unsigned warnings = 0;
    const board_id_t got = confirm_board(300, poep4, true, &warnings);
    std::printf("hint %u on revision 300 -> board %u, warnings %u\n",
                unsigned(poep4), unsigned(got), warnings);
    assert(got == poep4x && warnings == 1);
    ++cases;
  }
  {
    unsigned warnings = 0;
    const board_id_t got = confirm_board(0, poep4x, true, &warnings);
    std::printf("hint %u on revision 0 -> board %u, warnings %u\n",
                unsigned(poep4x), unsigned(got), warnings);
    assert(got == poep4 && warnings == 1);
    ++cases;
  }

  // 3) An agreeing hint stays silent.
  {
    unsigned warnings = 0;
    const board_id_t got = confirm_board(300, poep4x, true, &warnings);
    std::printf("hint %u on revision 300 -> board %u, warnings %u\n",
                unsigned(poep4x), unsigned(got), warnings);
    assert(got == poep4x && warnings == 0);
    ++cases;
  }

  // 4) No PHY response is rejected for either revision.
  assert(confirm_board(0, board_id_unknown, false, nullptr) == board_id_unknown);
  assert(confirm_board(300, board_id_unknown, false, nullptr) == board_id_unknown);
  std::printf("no PHY response -> rejected for revision 0 and 300\n");
  cases += 2;

  std::printf("PoE-P4X gate probe: %u cases passed\n", cases);
  return 0;
}
