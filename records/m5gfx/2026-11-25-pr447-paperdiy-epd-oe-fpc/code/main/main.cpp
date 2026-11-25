#include <M5GFX.h>
#include <cstdio>
#include <cstdint>
#include "board_detect/m5/generated/esp32s3_board_data.hpp"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static M5GFX display;
static constexpr int kOe = m5gfx::board_detect::m5::wiring::paperdiy::display_oe;

static void marker(const char *s)
{
  std::printf("PR447 %s\n", s);
  std::fflush(stdout);
}

static void draw_page(const char *title, uint32_t accent)
{
  display.fillScreen(TFT_WHITE);
  display.setTextColor(TFT_BLACK, TFT_WHITE);
  display.setTextSize(4);
  display.drawString(title, 40, 60);
  display.setTextSize(2);
  display.drawString("M5GFX paperdiy EPD OE test", 40, 140);
  display.fillRect(40, 220, 300, 120, accent);
  display.drawRect(360, 220, 300, 120, TFT_BLACK);
  display.drawRect(380, 240, 260, 80, TFT_BLACK);
  display.display();
  display.waitDisplay();
}

extern "C" void app_main(void)
{
  marker("BOOT");
  bool ok = display.init();
  std::printf("PR447 init=%d board=%d width=%d height=%d display_oe=%d\n", (int)ok, (int)display.getBoard(),
              (int)display.width(), (int)display.height(), kOe);
  std::fflush(stdout);
  if (!ok) { marker("INIT_FAIL"); return; }

  display.setRotation(0);
  draw_page("PR447 DRAW1", TFT_BLACK);
  marker("DRAW1_DONE");

  display.sleep();
  marker("SLEEP_DONE");
  vTaskDelay(pdMS_TO_TICKS(1000));
  display.wakeup();
  marker("WAKE_DONE");
  vTaskDelay(pdMS_TO_TICKS(200));

  draw_page("AFTER WAKE", TFT_BLACK);
  marker("DRAW2_DONE");

  for (;;) { vTaskDelay(pdMS_TO_TICKS(1000)); }
}
