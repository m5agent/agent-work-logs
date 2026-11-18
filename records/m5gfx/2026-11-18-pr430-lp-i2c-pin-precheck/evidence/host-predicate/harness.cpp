// Host harness for the predicate extracted verbatim from M5GFX PR #430
// (src/lgfx/v1/platforms/esp32/common.inl, commit 5ed5a0d).
// Only the IDF macro values are supplied from the real IDF headers; the
// pin-validity stub below stands in for rtc_gpio_is_valid_gpio().
#include <cstdio>

typedef int gpio_num_t;

static int g_valid_max = 0;  // inclusive upper bound of LP (RTC) IO pins
static bool g_valid_contiguous = true;

bool rtc_gpio_is_valid_gpio(gpio_num_t g)
{
  if (g < 0) { return false; }
  return g_valid_contiguous ? (g <= g_valid_max) : false;
}

#include "predicate.inc"

static int failures = 0;

static void expect(const char *name, int sda, int scl, bool want)
{
  bool got = lp_pads_accepted((gpio_num_t)sda, (gpio_num_t)scl);
  printf("%-28s sda=%2d scl=%2d -> %-5s want %-5s %s\n",
         name, sda, scl, got ? "true" : "false", want ? "true" : "false",
         got == want ? "OK" : "FAIL");
  if (got != want) { ++failures; }
}

int main()
{
#if defined(LGFX_LP_GPIO_MATRIX)
  g_valid_max = 15;  // ESP32-P4: SOC_RTCIO_PIN_COUNT 16 (IDF 5.5.4 soc_caps.h)
  printf("profile P4 (LP GPIO matrix, no fixed pair)\n");
  expect("pads used by the author", 11, 9, true);
  expect("other LP pair", 0, 15, true);
  expect("not LP IO", 18, 19, false);
  expect("one not LP IO", 11, 19, false);
#elif LP_I2C_SDA_IOMUX_PAD == 6 && LP_I2C_SCL_IOMUX_PAD == 7
  g_valid_max = 7;  // ESP32-C6 5.5.4 (count 8) / ESP32-C5 5.4.4 (count 8)
  printf("profile fixed pair 6/7\n");
  expect("fixed pair", 6, 7, true);
  expect("swapped pair", 7, 6, false);
  expect("LP IO, wrong pair", 4, 5, false);
  expect("one fixed, one wrong", 6, 5, false);
  expect("not LP IO", 18, 19, false);
#elif LP_I2C_SDA_IOMUX_PAD == 2 && LP_I2C_SCL_IOMUX_PAD == 3
  g_valid_max = 6;  // ESP32-C5 5.5.4: count 7 (IDF 5.5.4 soc_caps.h)
  printf("profile fixed pair 2/3\n");
  expect("fixed pair", 2, 3, true);
  expect("old 5.4 pair", 6, 7, false);
  expect("LP IO, wrong pair", 6, 5, false);
  expect("not LP IO", 18, 19, false);
#else
  printf("profile no fixed-pair macro\n");
  g_valid_max = 7;
  expect("any LP pair", 4, 5, true);
  expect("not LP IO", 18, 19, false);
#endif
  printf("%s (%d failure(s))\n", failures ? "FAIL" : "PASS", failures);
  return failures ? 1 : 0;
}
