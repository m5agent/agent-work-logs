// Nesso N1 (ESP32-C6) reproduction: Arduino SPI clock source after M5GFX bus init.
// Reads the SPI2 clock-source mux (PCR) and the SPI2 divider register, then
// derives the effective SCLK from the register state. No measurement of the
// physical pin; this is a register-level reproduction on a virtual device.

#include <M5GFX.h>
#include <SPI.h>
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

void setup() {
  Serial.begin(115200);
  delay(2000);

  report("boot");

  // 1) Arduino-only baseline: SPI.begin() pins the mux to XTAL on this core.
  SPI.begin(20, 22, 21);
  SPI.beginTransaction(SPISettings(8000000, MSBFIRST, SPI_MODE0));
  report("arduino_only_8MHz");
  SPI.endTransaction();
  SPI.end();

  // 2) M5GFX SPI bus init: Arduino SPI.begin() + IDF spi_bus_initialize().
  static lgfx::Bus_SPI bus;
  auto bcfg = bus.config();
  bcfg.spi_host = SPI2_HOST;
  bcfg.spi_mode = 0;
  bcfg.freq_write = 40000000;
  bcfg.freq_read = 16000000;
  bcfg.spi_3wire = false;
  bcfg.use_lock = true;
  bcfg.dma_channel = SPI_DMA_CH_AUTO;
  bcfg.pin_sclk = 20;
  bcfg.pin_mosi = 21;
  bcfg.pin_miso = 22;
  bcfg.pin_dc = 16;
  bus.config(bcfg);
  bool ok = bus.init();
  Serial.printf("m5gfx_bus_init=%d\n", ok ? 1 : 0);
  report("after_m5gfx_bus_init");

  // 3) The same host through the Arduino SPI object, 8 MHz as the SX1262 asks.
  SPI.beginTransaction(SPISettings(8000000, MSBFIRST, SPI_MODE0));
  report("arduino_after_m5gfx_8MHz");
  SPI.transfer(0x00);
  SPI.endTransaction();

  // 4) Same with 2 MHz.
  SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE0));
  report("arduino_after_m5gfx_2MHz");
  SPI.transfer(0x00);
  SPI.endTransaction();

  Serial.println("done");
}

void loop() { delay(1000); }
