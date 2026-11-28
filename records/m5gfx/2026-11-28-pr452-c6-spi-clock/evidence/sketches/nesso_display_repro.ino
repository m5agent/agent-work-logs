// Nesso N1 (ESP32-C6) display-path check for M5GFX PR #452.
// Runs the real Nesso N1 ST7789 panel through lgfx::Bus_SPI at the board's
// 40 MHz write / 16 MHz read settings, then checks that the Arduino SPI clock
// source survives the ESP-IDF master-driver initialization. Register-level
// reproduction on a virtual device; the physical SCLK pin is not measured.

#include <M5GFX.h>
#include <lgfx/v1/panel/Panel_ST7789.hpp>
#include <SPI.h>
#include <Wire.h>
#include "soc/pcr_reg.h"
#include "soc/spi_struct.h"

#define SPI2_HW ((spi_dev_t *)DR_REG_SPI2_BASE)

static const uint32_t XTAL_HZ = 40000000u;
static const uint32_t PLL80_HZ = 80000000u;

static void report(const char *tag) {
  uint32_t clkm = REG_READ(PCR_SPI2_CLKM_CONF_REG);
  uint32_t sel = (clkm >> PCR_SPI2_CLKM_SEL_S) & PCR_SPI2_CLKM_SEL_V;
  uint32_t div = (SPI2_HW->clock.clk_equ_sysclk)
                   ? 1u
                   : (uint32_t)(SPI2_HW->clock.clkdiv_pre + 1) * (SPI2_HW->clock.clkcnt_n + 1);
  uint32_t src = (sel == 0) ? XTAL_HZ : (sel == 1) ? PLL80_HZ : 0u;
  uint32_t sclk = src ? src / div : 0u;
  Serial.printf("%s pcr_clkm=0x%08x sel=%u clk_equ_sysclk=%u clkcnt_n=%u clkdiv_pre=%u div=%u src=%u sclk=%u\n",
                tag, clkm, sel, (unsigned)SPI2_HW->clock.clk_equ_sysclk,
                (unsigned)SPI2_HW->clock.clkcnt_n, (unsigned)SPI2_HW->clock.clkdiv_pre,
                div, src, sclk);
}

class LGFX : public lgfx::LGFX_Device {
  lgfx::Panel_ST7789 panel_;
  lgfx::Bus_SPI bus_;

public:
  LGFX() {
    {
      auto cfg = bus_.config();
      cfg.spi_host = SPI2_HOST;
      cfg.spi_mode = 0;
      cfg.freq_write = 40000000;
      cfg.freq_read = 16000000;
      cfg.spi_3wire = true;
      cfg.use_lock = true;
      cfg.dma_channel = SPI_DMA_CH_AUTO;
      cfg.pin_sclk = 20;
      cfg.pin_mosi = 21;
      cfg.pin_miso = 22;
      cfg.pin_dc = 16;
      bus_.config(cfg);
      panel_.setBus(&bus_);
    }
    {
      auto cfg = panel_.config();
      cfg.pin_cs = 17;
      cfg.pin_rst = -1;
      cfg.pin_busy = -1;
      cfg.memory_width = 135;
      cfg.memory_height = 240;
      cfg.panel_width = 135;
      cfg.panel_height = 240;
      cfg.offset_x = 52;
      cfg.offset_y = 40;
      cfg.offset_rotation = 0;
      cfg.readable = true;
      cfg.invert = true;
      cfg.rgb_order = false;
      cfg.dlen_16bit = false;
      cfg.bus_shared = false;
      panel_.config(cfg);
    }
    setPanel(&panel_);
  }
};

void setup() {
  Serial.begin(115200);
  delay(2000);

  report("boot");

  // Nesso N1 power/backlight are behind the PI4IOE at 0x44. The board model
  // gates panel commands and frame capture on LCD_READY (bit 1) and
  // BACKLIGHT (bit 6) of register 0x05, so set them before display init,
  // mirroring M5GFX's own nesson1_power_on plus Light setBrightness.
  Wire.begin(10, 8, 400000);
  auto ioe = [](uint8_t reg, uint8_t val) {
    Wire.beginTransmission(0x44);
    Wire.write(reg);
    Wire.write(val);
    return Wire.endTransmission();
  };
  int e1 = ioe(0x07, 0x18);
  int e2 = ioe(0x03, 0xC7);
  int e3 = ioe(0x05, 0xC2);
  Serial.printf("ioe_power=%d,%d,%d\n", e1, e2, e3);

  static LGFX display;
  bool ok = display.init();
  Serial.printf("display_init=%d width=%d height=%d\n", ok ? 1 : 0,
                (int)display.width(), (int)display.height());
  report("after_display_init");

  display.startWrite();
  display.fillScreen(display.color888(0, 0, 255));
  display.fillRect(10, 10, 50, 50, display.color888(255, 0, 0));
  display.fillRect(20, 20, 30, 30, display.color888(0, 255, 0));
  display.endWrite();

  uint16_t px[4] = {0, 0, 0, 0};
  display.readRect(25, 25, 2, 2, px);
  uint16_t expected = display.color888(0, 255, 0);
  Serial.printf("readback=%04x %04x %04x %04x expected=%04x match=%d\n",
                px[0], px[1], px[2], px[3], expected,
                (px[0] == expected && px[1] == expected && px[2] == expected && px[3] == expected) ? 1 : 0);
  report("after_display_push");

  // Same host through the Arduino SPI object, as the LoRa driver would use it.
  SPI.beginTransaction(SPISettings(8000000, MSBFIRST, SPI_MODE0));
  report("arduino_after_display_8MHz");
  SPI.transfer(0x00);
  SPI.endTransaction();

  SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE0));
  report("arduino_after_display_2MHz");
  SPI.transfer(0x00);
  SPI.endTransaction();

  Serial.println("done");
}

void loop() { delay(1000); }
