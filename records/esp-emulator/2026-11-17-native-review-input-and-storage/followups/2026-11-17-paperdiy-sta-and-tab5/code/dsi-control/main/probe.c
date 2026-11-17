#include <stdint.h>
#include <stdio.h>
#include "esp_err.h"
#include "esp_lcd_mipi_dsi.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_ldo_regulator.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

enum { WIDTH = 128, HEIGHT = 120 };

void app_main(void)
{
    esp_ldo_channel_handle_t ldo;
    esp_ldo_channel_config_t ldo_config = { .chan_id = 3, .voltage_mv = 2500 };
    ESP_ERROR_CHECK(esp_ldo_acquire_channel(&ldo_config, &ldo));
    puts("DSI_CONTROL_LDO_READY");
    esp_lcd_dsi_bus_handle_t bus;
    esp_lcd_dsi_bus_config_t bus_config = {
        .bus_id = 0, .num_data_lanes = 2, .lane_bit_rate_mbps = 1000,
    };
    ESP_ERROR_CHECK(esp_lcd_new_dsi_bus(&bus_config, &bus));
    puts("DSI_CONTROL_BUS_READY");
    esp_lcd_panel_io_handle_t io;
    esp_lcd_dbi_io_config_t io_config = {
        .virtual_channel = 0, .lcd_cmd_bits = 8, .lcd_param_bits = 8,
    };
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_dbi(bus, &io_config, &io));
    ESP_ERROR_CHECK(esp_lcd_panel_io_tx_param(io, 0x11, NULL, 0));
    ESP_ERROR_CHECK(esp_lcd_panel_io_tx_param(io, 0x29, NULL, 0));
    esp_lcd_panel_handle_t panel;
    esp_lcd_dpi_panel_config_t panel_config = {
        .virtual_channel = 0,
        .dpi_clk_src = MIPI_DSI_DPI_CLK_SRC_DEFAULT,
        .dpi_clock_freq_mhz = 48,
        .in_color_format = LCD_COLOR_FMT_RGB565,
        .video_timing = {
            .h_size = WIDTH, .v_size = HEIGHT,
            .hsync_back_porch = 20, .hsync_pulse_width = 10, .hsync_front_porch = 20,
            .vsync_back_porch = 8, .vsync_pulse_width = 4, .vsync_front_porch = 8,
        },
    };
    ESP_ERROR_CHECK(esp_lcd_new_panel_dpi(bus, &panel_config, &panel));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel));
    void *framebuffer;
    ESP_ERROR_CHECK(esp_lcd_dpi_panel_get_frame_buffer(panel, 1, &framebuffer));
    uint16_t *pixels = framebuffer;
    for (int y = 0; y < HEIGHT; ++y) {
        for (int x = 0; x < WIDTH; ++x) {
            pixels[y * WIDTH + x] = x < 64 ? 0xf800 : y < 60 ? 0x07e0 : 0x001f;
        }
    }
    ESP_ERROR_CHECK(esp_lcd_panel_draw_bitmap(panel, 0, 0, WIDTH, HEIGHT, framebuffer));
    puts("DSI_CONTROL_FRAME_READY");
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
