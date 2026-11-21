// Follow-up probe for m5stack/M5Unified#446 on the merged develop commit.
// Target: M5Dial (ESP32-S3) virtual device with the QEMU PCF8563 register model.
// It checks the post-merge contract described by the author:
//   1. disable_rtc_irq=false keeps a pre-armed timer across M5.begin()
//   2. clearIRQ() does not stop that timer
//   3. setTimerIRQ(0) / disableIRQ() stop it; disableIRQ() leaves 0x0E = 0x03
//   4. the default disable_rtc_irq=true path still stops it
#include <M5Unified.h>
#include <M5GFX.h>
#include <cstdio>
#include <cstdint>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

static constexpr int kRtcAddr = 0x51;

static int rawRead(uint8_t reg)
{
  return (int)m5::In_I2C.readRegister8(kRtcAddr, reg, 400000);
}
static bool rawWrite(uint8_t reg, uint8_t value)
{
  return m5::In_I2C.writeRegister8(kRtcAddr, reg, value, 400000);
}

static void dump(const char* tag)
{
  int tc = rawRead(0x0E);
  int c2 = rawRead(0x01);
  int cnt = rawRead(0x0F);
  printf("%s TC=0x%02X C2=0x%02X CNT=0x%02X TE=%d TD=%d TIE=%d\n",
         tag, tc, c2, cnt,
         (tc >> 7) & 1, tc & 3, c2 & 1);
  fflush(stdout);
}

extern "C" void app_main(void)
{
  printf("PCF8563_446_FOLLOW_BOOT\n");
  fflush(stdout);

  auto init = m5gfx::i2c::init(1, 11, 12);
  bool pre_ok = init.has_value();
  if (pre_ok)
  {
    // Running timer with TIE enabled: 2 s countdown, TD = 1 Hz, TE = 1.
    pre_ok = m5gfx::i2c::writeRegister8(1, kRtcAddr, 0x01, 0x01).has_value() && pre_ok;
    pre_ok = m5gfx::i2c::writeRegister8(1, kRtcAddr, 0x0F, 2).has_value() && pre_ok;
    pre_ok = m5gfx::i2c::writeRegister8(1, kRtcAddr, 0x0E, 0x82).has_value() && pre_ok;
    auto tc = m5gfx::i2c::readRegister8(1, kRtcAddr, 0x0E);
    auto c2 = m5gfx::i2c::readRegister8(1, kRtcAddr, 0x01);
    auto cnt = m5gfx::i2c::readRegister8(1, kRtcAddr, 0x0F);
    printf("PRE_ARM ok=%d TC=0x%02X C2=0x%02X CNT=0x%02X\n", (int)pre_ok,
           tc.has_value() ? tc.value() : 0xFF,
           c2.has_value() ? c2.value() : 0xFF,
           cnt.has_value() ? cnt.value() : 0xFF);
    m5gfx::i2c::release(1);
  }
  else
  {
    printf("PRE_ARM ok=0 TC=0xFF C2=0xFF CNT=0xFF\n");
  }

  auto cfg = M5.config();
  cfg.internal_rtc = true;
  cfg.disable_rtc_irq = false;
  cfg.internal_imu = false;
  cfg.internal_mic = false;
  cfg.internal_spk = false;
  cfg.clear_display = false;
  M5.begin(cfg);
  printf("M5_BEGIN board=%d rtc=%d\n", (int)M5.getBoard(), (int)M5.Rtc.isEnabled());
  fflush(stdout);
  dump("POST_BEGIN_FALSE");

  // clearIRQ() must only clear AF/TF; the running timer (TE/TD) must survive.
  bool clr = M5.Rtc.clearIRQ();
  printf("CLEAR_IRQ ok=%d\n", (int)clr);
  dump("AFTER_CLEAR_IRQ");

  // A later begin() (as M5.begin() would call again) must still keep it.
  bool rb = M5.Rtc.begin(&m5::In_I2C);
  printf("REBEGIN_AFTER_CLEAR ok=%d\n", (int)rb);
  dump("AFTER_REBEGIN_AFTER_CLEAR");

  // setTimerIRQ(0) is the documented stop path.
  bool z = M5.Rtc.setTimerIRQ(0);
  printf("SETTIMER0 ok=%d\n", (int)z);
  dump("AFTER_SETTIMER0");

  // Public API arm then disableIRQ(): timer stopped, TD left at 1/60 Hz.
  uint32_t applied = 0;
  bool arm = M5.Rtc.setTimerIRQ(3000, &applied);
  printf("ARM_LIB ok=%d applied=%u\n", (int)arm, (unsigned)applied);
  dump("AFTER_ARM_LIB");
  bool dis = M5.Rtc.disableIRQ();
  printf("DISABLE_IRQ ok=%d\n", (int)dis);
  dump("AFTER_DISABLE_IRQ");

  // Default configuration path: begin() preserves, disableIRQ() stops.
  bool def_wr = rawWrite(0x01, 0x01) && rawWrite(0x0F, 2) && rawWrite(0x0E, 0x82);
  printf("DEFAULT_PATH_ARM ok=%d\n", (int)def_wr);
  dump("BEFORE_DEFAULT_REBEGIN");
  bool rb2 = M5.Rtc.begin(&m5::In_I2C);
  printf("DEFAULT_REBEGIN ok=%d\n", (int)rb2);
  dump("AFTER_DEFAULT_REBEGIN");
  bool dis2 = M5.Rtc.disableIRQ();
  printf("DEFAULT_DISABLE ok=%d\n", (int)dis2);
  dump("AFTER_DEFAULT_PATH");

  printf("PCF8563_446_FOLLOW_DONE\n");
  fflush(stdout);
  for (;;) { vTaskDelay(pdMS_TO_TICKS(1000)); }
}
