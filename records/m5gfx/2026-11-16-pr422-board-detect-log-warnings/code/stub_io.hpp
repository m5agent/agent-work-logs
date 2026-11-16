// Host stub for the M5GFX board_detect I/O contract.
// M5GFX_BOARD_DETECT_IO_HEADER is the library's documented replacement hook.
#pragma once
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

namespace hm {
inline std::vector<std::string>& logs() { static std::vector<std::string> v; return v; }
inline void clear() { logs().clear(); }
template <class... A> inline void capture(const char* fmt, A... a)
{
  char buf[512];
  std::snprintf(buf, sizeof(buf), fmt, a...);
  logs().emplace_back(buf);
}
template <class... A> inline void log_eval(const char*, A&&...) {}
}

#if defined(HM_LOG_CAPTURE)
#define HM_LOG_IMPL(fmt, ...) ::hm::capture(fmt, ##__VA_ARGS__)
#elif defined(HM_LOG_LEVEL) && (HM_LOG_LEVEL >= 4)
#define HM_LOG_IMPL(fmt, ...) ::hm::log_eval(fmt, ##__VA_ARGS__)
#else
#define HM_LOG_IMPL(fmt, ...) do {} while (0)
#endif
#define ESP_LOGE(tag, fmt, ...) HM_LOG_IMPL(fmt, ##__VA_ARGS__)
#define ESP_LOGW(tag, fmt, ...) HM_LOG_IMPL(fmt, ##__VA_ARGS__)
#define ESP_LOGI(tag, fmt, ...) HM_LOG_IMPL(fmt, ##__VA_ARGS__)
#define ESP_LOGD(tag, fmt, ...) HM_LOG_IMPL(fmt, ##__VA_ARGS__)
#define ESP_LOGV(tag, fmt, ...) HM_LOG_IMPL(fmt, ##__VA_ARGS__)

namespace m5gfx { namespace board_detect { namespace io {

constexpr int i2c_port_0 = 0;
constexpr int i2c_port_1 = 1;
constexpr int low_power_i2c_port_0 = 0;
constexpr int pin_count = 64;
constexpr unsigned package_classic_q6 = 6;
constexpr unsigned package_classic_pico_d4 = 4;
constexpr unsigned package_classic_picov3 = 3;
constexpr unsigned package_s3_qfn56 = 56;
constexpr unsigned package_s3_lga56 = 57;
constexpr unsigned package_c6_qfn40 = 40;
constexpr unsigned package_c6_qfn32 = 32;
constexpr unsigned package_p4 = 4;
constexpr bool dedicated_gpio_supported = true;


struct pin_state_t {
  int pin_ = -1;
  int mode_ = 0;
  int level_ = 0;
  void save(int pin) { pin_ = pin; }
  bool matches_current() const { return true; }
  void restore() {}
  int pin() const { return pin_; }
};

struct critical_section_t {
  void enter() {}
  void exit() {}
};

inline void pin_mode(int, pin_mode_t) {}
inline void pin_high(int) {}
inline void pin_low(int) {}
inline bool pin_read(int) { return true; }
inline bool pin_valid(int pin) { return pin >= 0 && pin < pin_count; }
inline bool pin_output_level(int, bool* level) { if (level) { *level = false; } return true; }
inline void release_lp_pad(int) {}
inline volatile std::uint32_t* pin_low_register(int) { static std::uint32_t r = 0; return &r; }
inline volatile std::uint32_t* pin_high_register(int) { static std::uint32_t r = 0; return &r; }
inline std::uint32_t cpu_cycles() { return 0; }
inline std::uint32_t cpu_hz() { return 240000000u; }
inline std::uint32_t millis() { return 0; }
inline std::uint32_t micros() { return 0; }
inline void delay_ms(std::uint32_t) {}
inline void delay_us(std::uint32_t) {}
inline void delay_rom_us(std::uint32_t) {}

inline bool i2c_open(int, int, int) { return false; }
inline void i2c_close(int) {}
inline bool i2c_ack(int, std::uint16_t, std::uint32_t, bool = false) { return false; }
inline bool i2c_read_reg8(int, std::uint16_t, std::uint8_t, std::uint8_t*, std::uint32_t) { return false; }
inline bool i2c_write_reg8(int, std::uint16_t, std::uint8_t, std::uint8_t, std::uint32_t) { return false; }
inline bool i2c_write(int, std::uint16_t, const std::uint8_t*, std::size_t, std::uint32_t) { return false; }
inline bool i2c_write_read(int, std::uint16_t, const std::uint8_t*, std::size_t, std::uint8_t*, std::size_t, std::uint32_t) { return false; }

inline unsigned package_version() { return 0; }
inline bool psram_ready() { return false; }
inline unsigned chip_revision() { return 0; }
inline unsigned flash_capacity_code() { return 0; }
inline void module_memory_capacity(unsigned* f, unsigned* p) { if (f) { *f = 0; } if (p) { *p = 0; } }
inline std::uint8_t st_touch_address() { return 0; }
inline std::uint8_t gt911_touch_address() { return 0; }
inline unsigned usb_serial_jtag_frame() { return 0; }
inline bool uart_rx_held_high() { return false; }

inline std::uint32_t dedicated_release_read_in() { return 0; }
inline void dedicated_release_write_mask(std::uint32_t, std::uint32_t) {}
inline void dedicated_release_channel_masks(dedicated_gpio_handle_t, std::uint8_t, std::uint32_t*, std::uint32_t*, int*, int*) {}
inline int dedicated_release_core_id() { return 0; }
inline std::uint32_t dedicated_release_cycle_count() { return 0; }
inline int dedicated_release_task_core() { return 0; }
inline int no_core_affinity() { return -1; }
inline bool dedicated_gpio_in_use() { return false; }
inline void pin_weak_pullup_open_drain(int) {}
inline int dedicated_gpio_open(const int*, std::uint8_t, dedicated_gpio_handle_t*) { return -1; }
inline int dedicated_gpio_close(dedicated_gpio_handle_t) { return 0; }

template <int channel_a, int pin_a, int channel_b, int pin_b, std::uint32_t timeout_us>
inline bool classic_touch_measure(std::uint16_t* t4, std::uint16_t* t7) { if (t4) { *t4 = 0; } if (t7) { *t7 = 0; } return false; }

template <int led_gpio, std::uint16_t pixels>
inline void classic_led_clear() {}

}}}
