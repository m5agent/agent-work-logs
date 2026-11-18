// Minimal M5Paper example for M5Unified.
// The IT8951 e-paper panel has auto_display enabled (M5GFX
// lgfx/v1/panel/Panel_IT8951.inl), so a write transaction ending with
// endWrite() is what pushes the region to the panel. Wrapping the whole
// first screen in startWrite()/endWrite() keeps it to one refresh.
#include <M5Unified.h>

static void drawScreen(void)
{
  M5.Display.setEpdMode(m5gfx::epd_mode_t::epd_quality);

  M5.Display.startWrite();
  M5.Display.fillScreen(TFT_WHITE);
  M5.Display.setTextColor(TFT_BLACK, TFT_WHITE);

  M5.Display.setTextSize(3);
  M5.Display.setCursor(24, 60);
  M5.Display.println("M5Paper");

  M5.Display.setTextSize(2);
  M5.Display.setCursor(24, 120);
  M5.Display.printf("panel : %dx%d", M5.Display.width(), M5.Display.height());
  M5.Display.setCursor(24, 156);
  M5.Display.printf("battery: %d mV", M5.Power.getBatteryVoltage());
  M5.Display.endWrite();
}

static void drawClicks(void)
{
  M5.Display.startWrite();
  M5.Display.fillRect(0, 240, M5.Display.width(), 48, TFT_WHITE);
  M5.Display.setTextColor(TFT_BLACK, TFT_WHITE);
  M5.Display.setTextSize(2);
  M5.Display.setCursor(24, 244);
  M5.Display.printf("BtnA clicks: %u", (unsigned)M5.BtnA.getClickCount());
  M5.Display.endWrite();
}

void setup(void)
{
  auto cfg = M5.config();
  M5.begin(cfg);

  drawScreen();
  drawClicks();
}

void loop(void)
{
  M5.update();
  if (M5.BtnA.wasClicked()) {
    drawClicks();
  }
  delay(10);
}
