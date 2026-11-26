#ifndef STUB_GPIO_CONSUMER_H
#define STUB_GPIO_CONSUMER_H
#include "../../stubcore.h"
struct gpio_desc { int value; };
enum gpiod_flags { GPIOD_IN = 0, GPIOD_OUT_LOW = 1 };
struct gpio_desc *devm_gpiod_get(struct device *dev, const char *con, enum gpiod_flags f);
struct gpio_desc *devm_gpiod_get_optional(struct device *dev, const char *con, enum gpiod_flags f);
int gpiod_get_raw_value_cansleep(const struct gpio_desc *d);
void gpiod_set_value_cansleep(struct gpio_desc *d, int val);
#endif
