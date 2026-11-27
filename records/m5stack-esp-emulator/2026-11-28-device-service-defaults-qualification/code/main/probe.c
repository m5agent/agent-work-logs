#include <stdint.h>
#include <stdio.h>
#include "driver/i2c_master.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static uint16_t read_u16(i2c_master_dev_handle_t device, uint8_t command)
{
    uint8_t result[2];
    ESP_ERROR_CHECK(i2c_master_transmit_receive(device, &command, 1, result, sizeof(result), 250));
    return result[0] | (result[1] << 8);
}

void app_main(void)
{
    i2c_master_bus_handle_t bus;
    i2c_master_dev_handle_t gauge;
    const i2c_master_bus_config_t wires = {
        .i2c_port = 0, .sda_io_num = 10, .scl_io_num = 8,
        .clk_source = I2C_CLK_SRC_DEFAULT, .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true
    };
    const i2c_device_config_t gauge_config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7, .device_address = 0x55, .scl_speed_hz = 100000
    };
    ESP_ERROR_CHECK(i2c_new_master_bus(&wires, &bus));
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &gauge_config, &gauge));
    for (;;) {
        const int voltage = read_u16(gauge, 0x08);
        const int current = (int16_t)read_u16(gauge, 0x14);
        const int charge = read_u16(gauge, 0x2c);
        printf("NESSO_BQ27220 mv=%d ma=%d soc=%d\n", voltage, current, charge);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
