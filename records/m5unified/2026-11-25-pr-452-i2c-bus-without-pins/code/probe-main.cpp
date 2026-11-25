#include <M5Unified.h>
#include <cstdio>
#include <cstring>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

static const char* BUILD_TAG = "pre";

static void dump_bus(const char* tag, m5::I2C_Class& bus)
{
  printf("P2 %s port=%d sda=%d scl=%d enabled=%d\n", tag,
         (int)bus.getPort(), (int)bus.getSDA(), (int)bus.getSCL(), (int)bus.isEnabled());
  bool begun = bus.begin();
  printf("P2 %s begin_ret=%d\n", tag, (int)begun);
  bool scan[128];
  memset(scan, 0, sizeof(scan));
  uint32_t t0 = m5gfx::millis();
  bus.scanID(scan);
  uint32_t dt = m5gfx::millis() - t0;
  int n = 0, first = -1;
  for (int i = 8; i < 0x78; ++i) { if (scan[i]) { ++n; if (first < 0) first = i; } }
  printf("P2 %s scan_count=%d first=%d scan_ms=%u\n", tag, n, first, (unsigned)dt);
  printf("P2 %s reg51_02=%02x\n", tag, (unsigned)bus.readRegister8(0x51, 0x02, 100000));
  bus.release();
}

static void run(void*)
{
  printf("\nP2 MARK_START tag=%s\n", BUILD_TAG);
  uint32_t t0 = m5gfx::millis();
  auto cfg = M5.config();
  M5.begin(cfg);
  uint32_t t1 = m5gfx::millis();
  printf("P2 M5_begin board=%d ms=%u displays=%d\n", (int)M5.getBoard(), (unsigned)(t1 - t0), (int)M5.getDisplayCount());
  printf("P2 flags In_enabled=%d Ex_enabled=%d rtc=%d imu=%d\n",
         (int)M5.In_I2C.isEnabled(), (int)M5.Ex_I2C.isEnabled(),
         (int)M5.Rtc.isEnabled(), (int)M5.Imu.isEnabled());
  dump_bus("Ex", M5.Ex_I2C);
  dump_bus("In", M5.In_I2C);
  m5::I2C_Class bare;
  dump_bus("Bare", bare);
  printf("P2 MARK_DONE tag=%s\n", BUILD_TAG);
  fflush(stdout);
  for (;;) { vTaskDelay(pdMS_TO_TICKS(1000)); }
}

extern "C" void app_main(void)
{
  xTaskCreatePinnedToCore(run, "probe", 16384, nullptr, 1, nullptr, 1);
}
