// PCF8563 begin() / disableIRQ() behaviour probe for M5Unified PR #447.
// Target: M5Dial (ESP32-S3) virtual device with the QEMU PCF8563 I2C model.
#include <M5Unified.h>
#include <M5GFX.h>
#include <cstdio>
#include <cstdint>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <esp_timer.h>

static constexpr int kRtcAddr = 0x51;
static constexpr int kInPort  = 1;
static constexpr int kInSda   = 11;
static constexpr int kInScl   = 12;

static int rawRead(uint8_t reg)
{
  return (int)m5::In_I2C.readRegister8(kRtcAddr, reg, 400000);
}
static bool rawWrite(uint8_t reg, uint8_t value)
{
  return m5::In_I2C.writeRegister8(kRtcAddr, reg, value, 400000);
}

static const char* hex(uint8_t v, char* buf)
{
  snprintf(buf, 8, "0x%02X", v);
  return buf;
}

// Poll Control_status_2 (0x01) bit2 = TF (timer flag). Return ms until set, or -1.
static int waitTF(int timeout_ms, const char* tag)
{
  int64_t start = esp_timer_get_time();
  while ((esp_timer_get_time() - start) < (int64_t)timeout_ms * 1000LL)
  {
    uint8_t c2 = (uint8_t)rawRead(0x01);
    if (c2 & 0x04)
    {
      int elapsed = (int)((esp_timer_get_time() - start) / 1000);
      printf("%s within_ms=%d\n", tag, elapsed);
      fflush(stdout);
      return elapsed;
    }
    vTaskDelay(pdMS_TO_TICKS(20));
  }
  printf("%s within_ms=-1\n", tag);
  fflush(stdout);
  return -1;
}

static void dump(const char* tag)
{
  char a[8], b[8], c[8];
  printf("%s TC=%s C2=%s CNT=%s\n", tag,
         hex((uint8_t)rawRead(0x0E), a),
         hex((uint8_t)rawRead(0x01), b),
         hex((uint8_t)rawRead(0x0F), c));
  fflush(stdout);
}

extern "C" void app_main(void)
{
  printf("PCF8563_447_BOOT\n");
  fflush(stdout);

  // Pre-boot PCF8563 state: timer armed with a 2 s countdown, TF cleared.
  // The RTC keeps running across an MCU reset, so this is the state a reboot sees.
  auto init = m5gfx::i2c::init(kInPort, kInSda, kInScl);
  bool pre_ok = init.has_value();
  if (pre_ok)
  {
    pre_ok = m5gfx::i2c::writeRegister8(kInPort, kRtcAddr, 0x01, 0x00).has_value();
    pre_ok = m5gfx::i2c::writeRegister8(kInPort, kRtcAddr, 0x0F, 2).has_value() && pre_ok;
    pre_ok = m5gfx::i2c::writeRegister8(kInPort, kRtcAddr, 0x0E, 0x82).has_value() && pre_ok;
    auto rd = m5gfx::i2c::readRegister8(kInPort, kRtcAddr, 0x0E);
    printf("PRE_ARM ok=%d TC=0x%02X\n", pre_ok, rd.has_value() ? rd.value() : 0xFF);
    m5gfx::i2c::release(kInPort);
  }
  else
  {
    printf("PRE_ARM ok=0 TC=0xFF\n");
  }
  fflush(stdout);

  auto cfg = M5.config();
  cfg.internal_rtc = true;
  cfg.disable_rtc_irq = false;   // the opt-out this PR makes effective
  cfg.internal_imu = false;
  cfg.internal_mic = false;
  cfg.internal_spk = false;
  cfg.clear_display = false;
  M5.begin(cfg);
  printf("M5_BEGIN board=%d rtc=%d\n", (int)M5.getBoard(), (int)M5.Rtc.isEnabled());
  fflush(stdout);
  dump("POST_BEGIN");
  waitTF(8000, "TF_AFTER_BEGIN");

  // Re-running the exact call M5.begin() makes must keep a running timer alive.
  bool rb = M5.Rtc.begin(&m5::In_I2C);
  printf("REBEGIN_RUNNING ok=%d\n", (int)rb);
  dump("AFTER_REBEGIN_RUNNING");

  // Same check with a timer armed through the public API.
  uint32_t applied = 0;
  bool armed = M5.Rtc.setTimerIRQ(3000, &applied);
  printf("ARM_LIB ok=%d applied=%u\n", (int)armed, (unsigned)applied);
  dump("AFTER_ARM_LIB");
  bool rb2 = M5.Rtc.begin(&m5::In_I2C);
  printf("REBEGIN_ARMED ok=%d\n", (int)rb2);
  dump("AFTER_REBEGIN_ARMED");
  waitTF(9000, "TF_AFTER_REBEGIN");

  // disableIRQ() must stop the timer; TD should become 1/60 Hz (0x03).
  bool dis = M5.Rtc.disableIRQ();
  printf("DISABLE_IRQ ok=%d\n", (int)dis);
  dump("AFTER_DISABLE_IRQ");

  // A stopped timer (TE=0, TD=00) must be normalised to 0x03 by begin().
  bool stopped_wr = rawWrite(0x0E, 0x00);
  printf("STOPPED_SET ok=%d\n", (int)stopped_wr);
  dump("BEFORE_REBEGIN_STOPPED");
  bool rb3 = M5.Rtc.begin(&m5::In_I2C);
  printf("REBEGIN_STOPPED ok=%d\n", (int)rb3);
  dump("AFTER_REBEGIN_STOPPED");

  // Default cfg (disable_rtc_irq = true): M5.begin() runs begin() then
  // disableIRQ(). Reproduce that exact pair with a timer already running.
  bool def_wr = rawWrite(0x01, 0x00) && rawWrite(0x0F, 2) && rawWrite(0x0E, 0x82);
  printf("DEFAULT_PATH_ARM ok=%d\n", (int)def_wr);
  bool rb4 = M5.Rtc.begin(&m5::In_I2C);
  bool dis2 = M5.Rtc.disableIRQ();
  printf("DEFAULT_PATH begin=%d disable=%d\n", (int)rb4, (int)dis2);
  dump("AFTER_DEFAULT_PATH");
  waitTF(4000, "TF_AFTER_DEFAULT");

  // setTimerIRQ(0) is the documented way to stop the timer.
  bool z = M5.Rtc.setTimerIRQ(0);
  printf("SETTIMER0 ok=%d\n", (int)z);
  dump("AFTER_SETTIMER0");

  // A running timer with TD=1/60 Hz must also be preserved bit-for-bit.
  bool p_wr = rawWrite(0x01, 0x00) && rawWrite(0x0F, 2) && rawWrite(0x0E, 0x83);
  bool rb5 = M5.Rtc.begin(&m5::In_I2C);
  printf("PRESERVE_TD60 write=%d begin=%d\n", (int)p_wr, (int)rb5);
  dump("AFTER_PRESERVE_TD60");
  M5.Rtc.setTimerIRQ(0);

  printf("PCF8563_447_DONE\n");
  fflush(stdout);
  for (;;) { vTaskDelay(pdMS_TO_TICKS(1000)); }
}
