#include <M5Unified.h>
#include <M5GFX.h>
#include <cstdio>
#include <cstdint>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

static constexpr int kRtcAddr = 0x51;
static constexpr int kInPort  = 1;
static constexpr int kInSda   = 11;
static constexpr int kInScl   = 12;

static void dump(const char* tag, int port)
{
  // Use the library's I2C object once M5.begin() has brought it up.
  uint8_t tc  = m5::In_I2C.readRegister8(kRtcAddr, 0x0E, 400000);
  uint8_t c2  = m5::In_I2C.readRegister8(kRtcAddr, 0x01, 400000);
  uint8_t cnt = m5::In_I2C.readRegister8(kRtcAddr, 0x0F, 400000);
  printf("%s port=%d TC=0x%02X C2=0x%02X CNT=0x%02X\n", tag, port, tc, c2, cnt);
  fflush(stdout);
}

extern "C" void app_main(void)
{
  printf("PCF8563_446_BOOT\n");
  fflush(stdout);

  // Model a timer that was already armed before the library starts (the
  // PCF8563 keeps its registers across an MCU reset / deep-sleep wake).
  auto init = m5gfx::i2c::init(kInPort, kInSda, kInScl);
  bool pre_wr = false;
  uint8_t pre_tc = 0xFF;
  if (init.has_value())
  {
    pre_wr = m5gfx::i2c::writeRegister8(kInPort, kRtcAddr, 0x0E, 0x82).has_value();
    auto rd = m5gfx::i2c::readRegister8(kInPort, kRtcAddr, 0x0E);
    if (rd.has_value()) { pre_tc = rd.value(); }
    m5gfx::i2c::release(kInPort);
  }
  printf("PRE_ARM init=%d write=%d TC=0x%02X\n", init.has_value(), pre_wr, pre_tc);
  fflush(stdout);

  auto cfg = M5.config();
  cfg.internal_rtc = true;
  cfg.disable_rtc_irq = false;   // the option the reporter sets
  cfg.internal_imu = false;
  cfg.internal_mic = false;
  cfg.internal_spk = false;
  cfg.clear_display = false;
  M5.begin(cfg);
  printf("M5_BEGIN done board=%d rtc=%d\n", (int)M5.getBoard(), M5.Rtc.isEnabled());
  fflush(stdout);
  dump("POST_BEGIN", kInPort);

  uint32_t applied = 0;
  bool armed = M5.Rtc.setTimerIRQ(1000, &applied);
  printf("SET_TIMER ok=%d applied=%u\n", armed, (unsigned)applied);
  fflush(stdout);
  dump("ARMED", kInPort);

  // Re-run the exact function M5.begin() uses for the RTC. The PCF8563 is not
  // reset by an MCU reset, so this is the state the next boot starts from.
  bool rebegin = M5.Rtc.begin(&m5::In_I2C);
  printf("RTC_BEGIN_AGAIN ok=%d\n", rebegin);
  fflush(stdout);
  dump("AFTER_REBEGIN", kInPort);

  // App-side recovery: arm the timer again.
  uint32_t applied2 = 0;
  bool armed2 = M5.Rtc.setTimerIRQ(1000, &applied2);
  printf("REARM ok=%d applied=%u\n", armed2, (unsigned)applied2);
  fflush(stdout);
  dump("AFTER_REARM", kInPort);

  printf("PCF8563_446_DONE\n");
  fflush(stdout);
  for (;;) { vTaskDelay(pdMS_TO_TICKS(1000)); }
}
