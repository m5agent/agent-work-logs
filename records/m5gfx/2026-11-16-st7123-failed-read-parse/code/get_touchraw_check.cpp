// Host-side reproduction for m5stack/M5GFX#417.
//
// The two structs and the getTouchRaw() body are copied verbatim from
// M5GFX 28d47949bdc84f30881623476f555398e2194313
// src/lgfx/v1/platforms/esp32p4/Touch_ST7123.inl:109-157.
// Only _readParams() is replaced by a mock that emulates the three register
// reads and can fail a chosen one. No I2C, controller timing or panel is
// involved; this is code-level verification, not device validation.
//
// Build: clang++ -std=c++17 -O0 -fno-inline get_touchraw_check.cpp -o get_touchraw_check

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstddef>

static constexpr uint16_t ST7123_MAX_TOUCHES_REG    = 0x0009;
static constexpr uint16_t ST7123_REPORT_COORD_0_REG = 0x0014;
static constexpr uint8_t  max_touch_points = 10;

struct touch_point_t { uint8_t id; uint16_t x, y; uint8_t size; };

struct touch_report_t {
  uint8_t x_h: 6;
  uint8_t reserved_6: 1;
  uint8_t valid: 1;
  uint8_t x_l;
  uint8_t y_h;
  uint8_t y_l;
  uint8_t area;
  uint8_t intensity;
  uint8_t reserved_49_55;
};
struct adv_info_t {
  uint8_t reserved_0_1: 2;
  uint8_t with_prox: 1;
  uint8_t with_coord: 1;
  uint8_t prox_status: 3;
  uint8_t rst_chip: 1;
};

// Mock chip. 1 = adv_info (0x0010), 2 = max touches (0x0009), 3 = report (0x0014).
// A failing read leaves the caller's buffer untouched, like an address NACK in
// lgfx::i2c::transactionWriteRead(); report_bytes controls a partial fill.
static int fail_stage = 0;
static int partial_bytes = 0;

bool _readParams(uint16_t reg, uint8_t *data, size_t len) {
  int stage = (reg == 0x0010) ? 1 : (reg == ST7123_MAX_TOUCHES_REG) ? 2 : 3;
  if (stage == fail_stage) {
    for (int i = 0; i < partial_bytes && i < (int)len; ++i) data[i] = 0x00;
    return false;
  }
  if (stage == 1 && len == 1) { data[0] = 0x08; return true; } // with_coord = 1
  if (stage == 2 && len == 1) { data[0] = 5; return true; }    // 5 active slots
  memset(data, 0, len);                                        // no touch
  return true;
}

// Fill the stack region the next call's locals will occupy with 0xFF, matching
// the pre-filled stack used in the report.
__attribute__((noinline)) void poison_stack() {
  volatile uint8_t buf[8192];
  memset((void *)buf, 0xFF, sizeof(buf));
  asm volatile("" :: "r"(buf) : "memory");
}

// ---- master 28d4794, verbatim logic ----
__attribute__((noinline)) size_t getTouchRaw_master(touch_point_t *tp, uint_fast8_t count) {
  size_t valid_count = 0;

  adv_info_t adv_info;
  _readParams(0x0010, (uint8_t *)&adv_info, 1);
  if (adv_info.with_coord) {
    uint8_t max_touches = 0;
    _readParams(ST7123_MAX_TOUCHES_REG, &max_touches, 1);
    if (max_touches > max_touch_points) {
      max_touches = max_touch_points;
    }
    touch_report_t touch_report[max_touch_points];
    _readParams(ST7123_REPORT_COORD_0_REG, (uint8_t *)&touch_report[0], sizeof(touch_report_t) * max_touches);

    for (size_t i = 0; i < max_touches; i++) {
      if (!touch_report[i].valid) { continue; }
      tp[valid_count].id = i;
      tp[valid_count].x = touch_report[i].x_h << 8 | touch_report[i].x_l;
      tp[valid_count].y = touch_report[i].y_h << 8 | touch_report[i].y_l;
      tp[valid_count].size = touch_report[i].area;
      valid_count++;
      if (valid_count >= count) break;
    }
  }
  return valid_count;
}

// ---- proposed fix, verbatim ----
__attribute__((noinline)) size_t getTouchRaw_fixed(touch_point_t *tp, uint_fast8_t count) {
  size_t valid_count = 0;

  adv_info_t adv_info = {};
  if (!_readParams(0x0010, (uint8_t *)&adv_info, 1)) { return 0; }
  if (adv_info.with_coord) {
    uint8_t max_touches = 0;
    if (!_readParams(ST7123_MAX_TOUCHES_REG, &max_touches, 1)) { return 0; }
    if (max_touches > max_touch_points) {
      max_touches = max_touch_points;
    }
    touch_report_t touch_report[max_touch_points] = {};
    if (!_readParams(ST7123_REPORT_COORD_0_REG, (uint8_t *)&touch_report[0], sizeof(touch_report_t) * max_touches)) { return 0; }

    for (size_t i = 0; i < max_touches; i++) {
      if (!touch_report[i].valid) { continue; }
      tp[valid_count].id = i;
      tp[valid_count].x = touch_report[i].x_h << 8 | touch_report[i].x_l;
      tp[valid_count].y = touch_report[i].y_h << 8 | touch_report[i].y_l;
      tp[valid_count].size = touch_report[i].area;
      valid_count++;
      if (valid_count >= count) break;
    }
  }
  return valid_count;
}

static void run(const char *label, int stage, int partial) {
  fail_stage = stage;
  partial_bytes = partial;

  touch_point_t tp[16] = {};
  poison_stack();
  size_t m = getTouchRaw_master(tp, 5);
  printf("%-40s master: %zu touch(es)", label, m);
  if (m) printf("  first: id=%u x=%u y=%u size=%u", tp[0].id, tp[0].x, tp[0].y, tp[0].size);
  printf("\n");

  touch_point_t tp2[16] = {};
  poison_stack();
  size_t f = getTouchRaw_fixed(tp2, 5);
  printf("%-40s fixed : %zu touch(es)\n", "", f);
}

int main() {
  printf("sizeof: touch_report_t=%zu adv_info_t=%zu, max_touch_points=%u, count=5\n",
         sizeof(touch_report_t), sizeof(adv_info_t), max_touch_points);
  run("no read fails", 0, 0);
  run("adv_info read fails", 1, 0);
  run("max_touches read fails", 2, 0);
  run("report read fails, untouched", 3, 0);
  run("report read fails, 3 bytes part-filled", 3, 3);
  return 0;
}
