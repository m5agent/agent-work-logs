#ifndef STUB_PLATFORM_DEVICE_H
#define STUB_PLATFORM_DEVICE_H
#include "../stubcore.h"
#include "device.h"
struct of_device_id;
struct platform_device { struct device dev; void *drvdata; };
struct platform_driver {
	int  (*probe)(struct platform_device *);
	void (*remove)(struct platform_device *);
	void (*shutdown)(struct platform_device *);
	struct { const char *name; const struct of_device_id *of_match_table; } driver;
};
int platform_get_irq(struct platform_device *pdev, unsigned int n);
void *platform_get_drvdata(struct platform_device *pdev);
void platform_set_drvdata(struct platform_device *pdev, void *data);
#endif
