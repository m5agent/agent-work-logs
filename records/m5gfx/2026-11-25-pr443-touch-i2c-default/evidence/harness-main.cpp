#include <M5GFX.h>
#include <lgfx/v1/touch/Touch_CSTxxx.hpp>
#include <cstdio>

static M5GFX display;

extern "C" void app_main(void)
{
  printf("HARNESS start\n");
  printf("HARNESS default_config_freq=%u\n", (unsigned)lgfx::ITouch::config_t{}.freq);

  const bool init_ok = display.init();
  const auto board = display.getBoard();
  printf("HARNESS display_init=%d board=%d size=%dx%d\n",
         init_ok ? 1 : 0, (int)board, (int)display.width(), (int)display.height());

  lgfx::ITouch* bt = display.panel() ? display.panel()->touch() : nullptr;
  if (bt)
  {
    const auto bcfg = bt->config();
    printf("HARNESS board_touch addr=0x%02x port=%d sda=%d scl=%d freq=%u\n",
           (unsigned)bcfg.i2c_addr, (int)bcfg.i2c_port, (int)bcfg.pin_sda,
           (int)bcfg.pin_scl, (unsigned)bcfg.freq);
  }
  else
  {
    printf("HARNESS board_touch none\n");
  }

  display.fillScreen(0x102030);
  display.setTextColor(0xFFFFFF, 0x102030);
  display.setTextSize(2);
  display.setCursor(16, 16);
  display.print("M5GFX #443");
  display.setTextSize(1);
  display.setCursor(16, 48);
  printf("HARNESS frame_drawn\n");

  static lgfx::Touch_CST816S touch;
  auto cfg = touch.config();
  printf("HARNESS driver_default_freq=%u addr=0x%02x\n",
         (unsigned)cfg.freq, (unsigned)cfg.i2c_addr);
  cfg.i2c_port = 1;
  cfg.pin_sda = 47;
  cfg.pin_scl = 48;
  cfg.pin_int = -1;
  cfg.x_min = 0;
  cfg.x_max = 233;
  cfg.y_min = 0;
  cfg.y_max = 233;
  touch.config(cfg);
  printf("HARNESS applied_freq=%u\n", (unsigned)touch.config().freq);

  const bool touch_ok = touch.init();
  printf("HARNESS touch_init=%d\n", touch_ok ? 1 : 0);

  for (int i = 0; i < 600; ++i)
  {
    lgfx::touch_point_t tp[5];
    auto n = touch.getTouchRaw(tp, 5);
    if (n)
    {
      printf("HARNESS raw n=%u x=%d y=%d size=%u id=%u\n",
             (unsigned)n, (int)tp[0].x, (int)tp[0].y,
             (unsigned)tp[0].size, (unsigned)tp[0].id);
      display.fillRect(tp[0].x - 4, tp[0].y - 4, 9, 9, 0x07E0);
    }
    if (bt)
    {
      lgfx::touch_point_t bp[5];
      auto bn = bt->getTouchRaw(bp, 5);
      if (bn)
      {
        printf("HARNESS board n=%u x=%d y=%d\n", (unsigned)bn, (int)bp[0].x, (int)bp[0].y);
      }
    }
    lgfx::delay(50);
  }
  printf("HARNESS done\n");
}
