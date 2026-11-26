#ifndef STUB_I2C_H
#define STUB_I2C_H
#include "../stubcore.h"
struct i2c_client { struct device dev; };
s32 i2c_smbus_write_i2c_block_data(const struct i2c_client *c, u8 cmd,
				   u8 len, const u8 *values);
s32 i2c_smbus_read_word_data(const struct i2c_client *c, u8 cmd);
s32 i2c_smbus_read_byte_data(const struct i2c_client *c, u8 cmd);
#endif
