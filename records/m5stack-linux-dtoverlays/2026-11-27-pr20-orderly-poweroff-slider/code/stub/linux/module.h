#ifndef STUB_MODULE_H
#define STUB_MODULE_H
#include "../stubcore.h"
#include "device.h"
#define MODULE_AUTHOR(x)
#define MODULE_DESCRIPTION(x)
#define MODULE_LICENSE(x)
#define MODULE_DEVICE_TABLE(a, b)
#define module_platform_driver(x) static struct platform_driver *const __maybe_unused _drv = &(x)
#define __maybe_unused __attribute__((unused))
#endif
