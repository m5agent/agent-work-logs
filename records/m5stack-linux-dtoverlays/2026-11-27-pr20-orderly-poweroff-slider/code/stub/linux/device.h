#ifndef STUB_DEVICE_H
#define STUB_DEVICE_H
#include "../stubcore.h"
#define dev_emerg(dev, fmt, ...) printf("[emerg] " fmt, ##__VA_ARGS__)
#define dev_err(dev, fmt, ...)   printf("[err]   " fmt, ##__VA_ARGS__)
#define dev_warn(dev, fmt, ...)  printf("[warn]  " fmt, ##__VA_ARGS__)
#define dev_info(dev, fmt, ...)  printf("[info]  " fmt, ##__VA_ARGS__)
#define dev_err_probe(dev, ret, fmt, ...) \
	({ printf("[probe] " fmt, ##__VA_ARGS__); (int)(ret); })
#define dev_name(dev) ((dev)->name)
#define put_device(d)  ((void)(d))
#define get_device(d)  ((d))
static inline void *devm_kzalloc(struct device *dev, size_t n, int gfp)
{ (void)dev; (void)gfp; return calloc(1, n); }
static inline int devm_add_action_or_reset(struct device *dev,
					   void (*fn)(void *), void *arg)
{ (void)dev; fn(arg); return 0; }
#endif
