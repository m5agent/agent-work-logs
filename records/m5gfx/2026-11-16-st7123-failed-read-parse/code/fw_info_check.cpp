// Host check for the side note in m5stack/M5GFX#417: _read_fw_info() returns
// true when the chip does not answer.
//
// Body copied from M5GFX 28d47949bdc84f30881623476f555398e2194313
// src/lgfx/v1/platforms/esp32p4/Touch_ST7123.inl:47-71, with _readParams()
// mocked. Code-level verification only.
//
// Build: clang++ -std=c++17 -O0 fw_info_check.cpp -o fw_info_check

#include <cstdint>
#include <cstdio>
#include <cstring>

static int fail_all = 0;

bool _readParams(uint16_t, uint8_t *data, size_t len) {
  if (fail_all) return false;
  memset(data, 0, len); // chip answers, all zeros
  return true;
}

struct fw_info_t { uint8_t max_x_h, max_x_l, max_y_h, max_y_l, max_touches; };

bool _read_fw_info() {
  uint8_t version = 0;
  uint8_t revision[4] = { 0 };
  fw_info_t info;

  if (_readParams(0x0000, &version, 1)
   && _readParams(0x000C, revision, 4)
   && _readParams(0x0005, (uint8_t *)&info, sizeof(info)))
  {
    uint32_t sum = version + revision[0] + revision[1] + revision[2] + revision[3]
                + info.max_x_h + info.max_x_l + info.max_y_h + info.max_y_l + info.max_touches;
    if (sum == 0)
    {
      return false;
    }
  }
  return true;
}

int main() {
  printf("chip answers with all zeros : _read_fw_info()=%d (expect 0)\n", _read_fw_info());
  fail_all = 1;
  printf("chip never answers (3 fails): _read_fw_info()=%d (master: 1, so init() reports success)\n", _read_fw_info());
  return 0;
}
