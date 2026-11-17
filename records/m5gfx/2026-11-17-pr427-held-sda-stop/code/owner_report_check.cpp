// Two consecutive release_held_sda() attempts on a peripheral left at the MSB of
// the byte after the master's ACK (the ainyan03 #427 report state).
// Models only what the report needs: the peripheral sends bits MSB first, takes
// SDA low for each 0 bit, releases in the acknowledge slot, stops on a NACK or
// a STOP. Line levels are replayed from host_hardware::events.
#define CONFIG_IDF_TARGET_ESP32S3 1
#define CONFIG_IDF_TARGET "esp32s3"
#include <cassert>
#include <cstdio>
#include <vector>
#include "board_detect/board_detect.inl"
using namespace m5gfx::board_detect;

static constexpr int sda = 4;
static constexpr int scl = 5;

struct peripheral_t
{
  std::vector<bool> bits;
  std::size_t start;
  bool transmitter;
};

static bool sda_level(const peripheral_t& p)
{
  bool master_sda = true, master_scl = true, active = true;
  std::size_t position = p.start;
  auto peripheral_sda = [&]() { return !active || p.bits[position % p.bits.size()]; };
  for (const auto& e : host_hardware::events)
  {
    if (e.kind != 4) { continue; }
    if (e.pin == scl)
    {
      const bool rising = !master_scl && e.value;
      const bool falling = master_scl && !e.value;
      master_scl = e.value;
      if (rising && active && p.transmitter && position % 9 == 8 && master_sda) { active = false; }
      if (falling && active) { ++position; }
    }
    else if (e.pin == sda)
    {
      const bool line_was_low = !(master_sda && peripheral_sda());
      master_sda = e.value;
      if (master_scl && line_was_low && master_sda && peripheral_sda()) { active = false; }
    }
  }
  return master_sda && peripheral_sda();
}

static bool master_scl_level()
{
  bool level = true;
  for (const auto& e : host_hardware::events) { if (e.kind == 4 && e.pin == scl) { level = e.value; } }
  return level;
}

static std::vector<bool> byte_bits(std::uint8_t value)
{
  std::vector<bool> bits;
  for (int bit = 7; bit >= 0; --bit) { bits.push_back((value >> bit) & 1); }
  bits.push_back(true);
  return bits;
}

struct attempt_t { bool released; unsigned pulses; bool sda; };

static attempt_t attempt(const peripheral_t& p)
{
  const std::size_t before = host_hardware::events.size();
  host_hardware::input = [&](int pin, int, bool latch) {
    if (pin == scl) { return master_scl_level(); }
    if (pin == sda) { return sda_level(p); }
    return latch;
  };
  const bool released = release_held_sda(sda, scl);
  unsigned pulses = 0;
  for (std::size_t i = before; i < host_hardware::events.size(); ++i)
  {
    const auto& e = host_hardware::events[i];
    pulses += e.kind == 4 && e.pin == scl && e.value == 0;
  }
  return {released, pulses, sda_level(p)};
}

int main()
{
  for (const std::uint8_t value : {0x55, 0x2A, 0x02})
  {
    host_hardware::reset();
    const peripheral_t p{byte_bits(value), 0, true};
    const auto first = attempt(p);
    const auto second = attempt(p);
    std::printf("value=0x%02X attempt1 released=%d scl_low_pulses=%u sda_high_after=%d\n",
                value, int(first.released), first.pulses, int(first.sda));
    std::printf("value=0x%02X attempt2 released=%d scl_low_pulses=%u sda_high_after=%d\n",
                value, int(second.released), second.pulses, int(second.sda));
  }
  return 0;
}
