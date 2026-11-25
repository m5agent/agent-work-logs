// StickS3 M5PM1 GPIO_FUNC0 (0x16) two-boot probe.
//
// Boot 1: seed 0x16 with function bits the way an application could leave them
// (gpio0..gpio2 = 0b11 special, so gpio2 / LCD power is not GPIO), store a NVS
// marker and reset the ESP32. The PM1 keeps its registers across an ESP reset.
// Boot 2: run the M5GFX StickS3 board startup and report 0x16 afterwards.
// M5GFX is not touched before init() on boot 2 so its I2C setup is not pre-empted.
#include <cstdio>
#include <cstdint>

#include <M5GFX.h>
#include "esp_log.h"
#include "esp_system.h"
#include "driver/i2c_master.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static constexpr int kPm1Port  = 1;
static constexpr int kPm1Sda   = 47;
static constexpr int kPm1Scl   = 48;
static constexpr int kPm1Addr  = 0x6E;
static constexpr int kFunc0Reg = 0x16;

static bool pm1Read(uint8_t* value)
{
  auto r = lgfx::i2c::readRegister8(kPm1Port, kPm1Addr, kFunc0Reg, 100000);
  if (r.has_error()) { return false; }
  *value = r.value();
  return true;
}

static bool pm1Write(uint8_t value)
{
  return !lgfx::i2c::writeRegister8(kPm1Port, kPm1Addr, kFunc0Reg, value, 0, 100000).has_error();
}

// Seed 0x16 through the IDF driver and release the bus before M5GFX starts, so
// M5GFX can own I2C port 1 the way it does on a normal boot.
static bool seedFunc0(uint8_t value, uint8_t* readback)
{
  i2c_master_bus_config_t bus_cfg = {};
  bus_cfg.i2c_port = static_cast<i2c_port_num_t>(kPm1Port);
  bus_cfg.sda_io_num = static_cast<gpio_num_t>(kPm1Sda);
  bus_cfg.scl_io_num = static_cast<gpio_num_t>(kPm1Scl);
  bus_cfg.clk_source = I2C_CLK_SRC_DEFAULT;
  bus_cfg.glitch_ignore_cnt = 7;
  bus_cfg.flags.enable_internal_pullup = true;
  i2c_master_bus_handle_t bus = nullptr;
  if (i2c_new_master_bus(&bus_cfg, &bus) != ESP_OK) { return false; }

  i2c_device_config_t dev_cfg = {};
  dev_cfg.dev_addr_length = I2C_ADDR_BIT_LEN_7;
  dev_cfg.device_address = kPm1Addr;
  dev_cfg.scl_speed_hz = 100000;
  i2c_master_dev_handle_t dev = nullptr;
  bool ok = i2c_master_bus_add_device(bus, &dev_cfg, &dev) == ESP_OK;
  if (ok)
  {
    const uint8_t out[2] = { static_cast<uint8_t>(kFunc0Reg), value };
    ok = i2c_master_transmit(dev, out, sizeof(out), 100) == ESP_OK;
    const uint8_t reg = static_cast<uint8_t>(kFunc0Reg);
    ok = ok && i2c_master_transmit_receive(dev, &reg, 1, readback, 1, 100) == ESP_OK;
    i2c_master_bus_rm_device(dev);
  }
  i2c_del_master_bus(bus);
  return ok;
}

extern "C" void app_main(void)
{
  printf("PROBE start build=" PROBE_BUILD_TAG "\n");

  // Fixed board selection runs the same descriptor and PM1 power sequence as an
  // autodetected StickS3, without touching I2C before init().
  m5gfx::detect_config_t cfg;
  cfg.fixed_board = m5gfx::board_t::board_M5StickS3;
  M5GFX display;
  display.setDetectConfig(cfg);
  bool init_ok = display.init();
  printf("PROBE init fixed_init=%d board=%d fixed=%d display=%dx%d\n",
         init_ok ? 1 : 0, (int)display.getBoard(), (int)display.getFixedBoard(),
         (int)display.width(), (int)display.height());

  lgfx::i2c::init(kPm1Port, kPm1Sda, kPm1Scl);
  uint8_t after = 0xFF;
  bool after_ok = pm1Read(&after);
  printf("PROBE func0_after_init=%s0x%02X gpio2_func=%d gpio1_func=%d\n",
         after_ok ? "" : "ERR", after_ok ? after : 0,
         after_ok ? ((after >> 4) & 0x03) : -1,
         after_ok ? ((after >> 2) & 0x03) : -1);

  if (display.width() > 0)
  {
    display.fillScreen(TFT_BLACK);
    display.fillRect(0, 0, display.width(), 40, TFT_RED);
    display.setTextColor(TFT_WHITE, TFT_BLACK);
    display.setCursor(4, 60);
    display.printf("func0 after: 0x%02X", after);
    display.setCursor(4, 90);
    display.printf("board=%d %dx%d", (int)display.getBoard(),
                   (int)display.width(), (int)display.height());
    printf("PROBE draw_done\n");
  }

  for (int i = 0; i < 40; ++i)
  {
    printf("PROBE alive=%d\n", i);
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}
