#ifndef STUB_OF_H
#define STUB_OF_H
#include "../stubcore.h"
struct of_device_id { const char *compatible; };
struct device_node *of_parse_phandle(const struct device_node *np,
				     const char *name, int index);
void of_node_put(struct device_node *np);
int of_device_is_compatible(const struct device_node *np, const char *c);
int of_property_read_u32(const struct device_node *np, const char *name, u32 *out);
struct i2c_client *of_find_i2c_device_by_node(struct device_node *node);
#endif
