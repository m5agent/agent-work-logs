// M5Unified PR #449 probe: LSM6DS3TR-C boot wait moved to the power-on site.
// Measures M5.begin() duration and the cost of LSM6DS3TRC_Class::begin() when no
// device answers, on the virtual boards that have no LSM6DS3TR-C.
#include <M5Unified.h>
#include "utility/imu/LSM6DS3TRC_Class.hpp"

#include <cstdio>
#include <cstdint>
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

static inline int64_t now_us(void) { return esp_timer_get_time(); }

static void scan_bus(m5::I2C_Class& bus, const char* tag)
{
  printf("I2C_SCAN_%s", tag);
  if (!bus.isEnabled())
  {
    printf(" disabled\n");
    fflush(stdout);
    return;
  }
  int found = 0;
  for (uint8_t addr = 0x08; addr < 0x78; ++addr)
  {
    std::uint8_t value = 0;
    if (bus.readRegister(addr, 0x00, &value, 1, 100000))
    {
      printf(" 0x%02X", addr);
      ++found;
    }
  }
  printf(" total=%d\n", found);
  fflush(stdout);
}

extern "C" void app_main(void)
{
  printf("PR449_PROBE_BOOT\n");
  fflush(stdout);

  int64_t t0 = now_us();
  auto cfg = M5.config();
  M5.begin(cfg);
  int64_t t1 = now_us();

  printf("M5_BEGIN_US %lld\n", (long long)(t1 - t0));
  printf("BOARD %d IMU_TYPE %d IMU_ENABLED %d EX_I2C %d IN_I2C %d\n",
         (int)M5.getBoard(), (int)M5.Imu.getType(), (int)M5.Imu.isEnabled(),
         (int)M5.Ex_I2C.isEnabled(), (int)M5.In_I2C.isEnabled());
  fflush(stdout);

  scan_bus(M5.In_I2C, "IN");
  scan_bus(M5.Ex_I2C, "EX");

  // One direct driver begin() per address, exactly what IMU detection calls.
  // develop: 15 ms + 1 tick before the first register read on every address.
  // PR:     first read is a probe, so an absent device costs only the bus read.
  for (int round = 0; round < 3; ++round)
  {
    for (int pass = 0; pass < 2; ++pass)
    {
      std::uint8_t addr = pass == 0 ? m5::LSM6DS3TRC_Class::DEFAULT_ADDRESS
                                    : m5::LSM6DS3TRC_Class::SECONDARY_ADDRESS;
      m5::LSM6DS3TRC_Class lsm(addr);
      int64_t a = now_us();
      auto spec = lsm.begin(&M5.In_I2C);
      int64_t b = now_us();
      printf("LSM_BEGIN r%d addr=0x%02X us=%lld spec=%d who=0x%02X\n",
             round, addr, (long long)(b - a), (int)spec, (unsigned)lsm.whoAmI());
      fflush(stdout);
    }
  }

  // Full IMU detection sequence (MPU6886 -> BMI270 x2 -> LSM6DS3TR-C x2 -> SH200Q).
  for (int round = 0; round < 3; ++round)
  {
    int64_t a = now_us();
    auto spec = M5.Imu.begin(&M5.In_I2C, M5.getBoard());
    int64_t b = now_us();
    printf("IMU_DETECT r%d us=%lld spec=%d type=%d\n",
           round, (long long)(b - a), (int)spec, (int)M5.Imu.getType());
    fflush(stdout);
    vTaskDelay(pdMS_TO_TICKS(20));
  }

  printf("PR449_PROBE_DONE\n");
  fflush(stdout);
  for (;;) { vTaskDelay(pdMS_TO_TICKS(1000)); }
}
