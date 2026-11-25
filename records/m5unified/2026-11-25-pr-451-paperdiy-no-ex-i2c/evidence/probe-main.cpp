// Minimal M5Unified runtime probe for m5stack/M5Unified#451 (PaperDIY Ex_I2C removal).
// Built with ESP-IDF; prints the resolved pin/port table and probes the internal
// PM1 (0x6E) through In_I2C before and after a manual Ex_I2C.begin().
#include <cstdio>
#include <M5Unified.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static bool pm1_read(const char* tag)
{
  std::uint8_t id[2] = {};
  const bool ok = M5.In_I2C.readRegister(0x6E, 0x00, id, sizeof(id), 100000);
  printf("[451] pm1 %s ok=%d id=%02x%02x\n", tag, (int)ok, id[1], id[0]);
  return ok;
}

static void dump(const char* tag)
{
  printf("[451] %s board=%d in_port=%d in_sda=%d in_scl=%d ex_enabled=%d ex_port=%d ex_sda=%d ex_scl=%d"
         " pa_sda=%d pa_scl=%d pa_scl_alias=%d\n",
         tag,
         (int)M5.getBoard(),
         (int)M5.In_I2C.getPort(), (int)M5.In_I2C.getSDA(), (int)M5.In_I2C.getSCL(),
         (int)M5.Ex_I2C.isEnabled(), (int)M5.Ex_I2C.getPort(),
         (int)M5.Ex_I2C.getSDA(), (int)M5.Ex_I2C.getSCL(),
         (int)M5.getPin(m5::pin_name_t::port_a_sda),
         (int)M5.getPin(m5::pin_name_t::port_a_scl),
         (int)M5.getPin(m5::pin_name_t::ex_i2c_scl));
  fflush(stdout);
}

extern "C" void app_main(void)
{
  auto cfg = M5.config();
  cfg.external_rtc = true;  // exercise the _begin_rtc_imu path
  cfg.external_imu = true;
  M5.begin(cfg);

  dump("after_begin");
  printf("[451] i2c_init port0=%d port1=%d soft_enabled=%d\n", (int)m5gfx::i2c::isInitialized(0), (int)m5gfx::i2c::isInitialized(1), (int)m5gfx::i2c::isInitialized(-1));
  fflush(stdout);
  printf("[451] display=%dx%d\n", (int)M5.Display.width(), (int)M5.Display.height());
  fflush(stdout);
  pm1_read("before_manual_ex_begin");

  // A sketch that opens Port A itself: on a board without a Grove port this must
  // not be able to touch the internal bus.
  const bool ex_begun = M5.Ex_I2C.begin();
  printf("[451] manual_ex_begin ret=%d\n", (int)ex_begun);
  fflush(stdout);
  pm1_read("after_manual_ex_begin");

  M5.Display.fillScreen(TFT_WHITE);
  M5.Display.setTextColor(TFT_BLACK, TFT_WHITE);
  M5.Display.setCursor(20, 20);
  M5.Display.setTextSize(3);
  M5.Display.printf("M5Unified #451\nboard=%d\nin_port=%d ex_en=%d\npa_sda=%d",
                    (int)M5.getBoard(), (int)M5.In_I2C.getPort(),
                    (int)M5.Ex_I2C.isEnabled(),
                    (int)M5.getPin(m5::pin_name_t::port_a_sda));
  M5.Display.display();
  printf("[451] display drawn\n");
  fflush(stdout);

  while (true) { vTaskDelay(pdMS_TO_TICKS(1000)); }
}
