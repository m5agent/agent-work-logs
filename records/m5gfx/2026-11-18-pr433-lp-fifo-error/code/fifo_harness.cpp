// Compiles the extracted isLpPort()/getFifoLen() against the macro sets that the real
// ESP-IDF headers define (see probe-lp-macros.sh) and checks the port -> depth mapping.
//
// Build selects the source with -DUSE_PR (PR head) or nothing (base develop).
//   -DHP_PORTS=n   number of high power ports
//   -DHAS_LP=1     the chip has a low power port at index HP_PORTS
//   -DEXP_HP=d     expected depth of every high power port
//   -DEXP_LP=d     expected depth of the low power port
//   -DLGFX_LP_I2C_NUM / -DLGFX_LP_I2C_PORT plus either SOC_* or I2C_LL_* as the headers say
#include <cstdint>
#include <cstdio>

namespace i2c {
#ifdef USE_PR
#include "pr_fn.inc"
#else
#include "base_fn.inc"
#endif
}

#ifndef HP_PORTS
#define HP_PORTS 1
#endif
#ifndef HAS_LP
#define HAS_LP 0
#endif

int main() {
  int bad = 0;
  for (int p = 0; p < HP_PORTS; ++p) {
    uint32_t v = i2c::getFifoLen(p);
    std::printf("  port %d -> %u (expect %d)\n", p, v, (int)EXP_HP);
    if (v != (uint32_t)EXP_HP) bad = 1;
  }
#if HAS_LP
  {
    uint32_t v = i2c::getFifoLen(HP_PORTS);
    std::printf("  lp port %d -> %u (expect %d)\n", HP_PORTS, v, (int)EXP_LP);
    if (v != (uint32_t)EXP_LP) bad = 1;
  }
#endif
  return bad;
}
