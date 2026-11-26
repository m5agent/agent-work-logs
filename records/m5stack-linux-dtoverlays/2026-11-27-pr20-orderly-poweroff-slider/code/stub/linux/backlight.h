#ifndef STUB_BACKLIGHT_H
#define STUB_BACKLIGHT_H
#include "../stubcore.h"
struct backlight_device { int dummy; };
struct backlight_device *devm_of_find_backlight(struct device *dev);
void backlight_device_set_brightness(struct backlight_device *bd, int v);
#endif
