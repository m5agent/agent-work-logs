// Probe: is board_M5UnitPoEP4X selectable through fixed_board, and can
// auto-detection ever return it? Host-only, no hardware.
#define CONFIG_IDF_TARGET_ESP32P4 1
#define CONFIG_SPIRAM 1
#define CONFIG_IDF_TARGET "esp32p4"
#include <cassert>
#include <cstdio>
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
}
using namespace m5gfx;
using namespace m5gfx::board_detect;
using namespace m5gfx::board_detect::m5;

int main() {
  const auto *entry = select_fixed_board(lgfx::board_M5UnitPoEP4X);
  std::printf("fixed entry=%p\n", (const void *)entry);
  if (!entry) return 2;
  std::printf("fixed id=%u name=%s displayless=%d\n", unsigned(entry->desc->def.id),
              entry->desc->def.name, entry->construct == construct_displayless);
  bool in_detector_members = false;
  for (auto d = esp32p4_detectors; *d; ++d)
    if ((*d)->has_member(entry->desc->def.id)) in_detector_members = true;
  std::printf("in_detector_members=%d\n", in_detector_members);
  return 0;
}
