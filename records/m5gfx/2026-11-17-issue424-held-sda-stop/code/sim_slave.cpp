// Focused host test for release_held_sda(): models an I2C slave that was left
// mid-read by an MCU reset and is still clocking out its byte.
//
// Entry state: SCL high, SDA low (held by the slave's current 0 bit), which is
// the state the issue reports on ToughC5 before board detection runs.
#define CONFIG_IDF_TARGET_ESP32S3 1
#define CONFIG_IDF_TARGET "esp32s3"
#include <cassert>
#include <cstdio>
#include <initializer_list>
#include <vector>
#include "board_detect/board_detect.inl"
#include "board_detect/m5/esp32s3.inl"
#include "support/display_backend.hpp"

using namespace m5gfx::board_detect;

namespace {
constexpr int SDA = 3;
constexpr int SCL = 9;

struct slave_sim_t {
  std::vector<int> bits;
  std::size_t idx = 0;
  bool slave_low = false;
  bool stuck = false;
  bool last_scl = true;
  std::size_t cursor = 0;
  unsigned scl_falls = 0;
  unsigned scl_rises = 0;
  bool write_ack = false;

  void arm(std::initializer_list<int> b, bool scl_high = true, bool sda_held = false)
  {
    bits.assign(b.begin(), b.end());
    idx = 0;
    slave_low = bits.empty() ? sda_held : (bits[0] == 0);
    stuck = false;
    write_ack = false;
    last_scl = scl_high;
    cursor = host_hardware::events.size();
    scl_falls = 0;
    scl_rises = 0;
  }
  void arm_write_ack()
  {
    bits.clear();
    idx = 0;
    slave_low = true;      // data bits all 0
    stuck = false;
    write_ack = true;
    last_scl = true;
    cursor = host_hardware::events.size();
    scl_falls = 0;
    scl_rises = 0;
  }
  void arm_stuck()
  {
    bits.clear();
    idx = 0;
    slave_low = true;
    stuck = true;
    write_ack = false;
    last_scl = true;
    cursor = host_hardware::events.size();
    scl_falls = 0;
    scl_rises = 0;
  }
  void advance()
  {
    if (stuck) { return; }
    if (idx + 1 < bits.size()) { ++idx; slave_low = (bits[idx] == 0); }
    else { slave_low = false; }   // acknowledge slot: the slave lets go of SDA
  }
  void process_events()
  {
    while (cursor < host_hardware::events.size())
    {
      const auto e = host_hardware::events[cursor++];
      if (e.kind == 4 && e.pin == SCL)
      {
        const bool high = e.value != 0;
        if (!last_scl && high) {
          ++scl_rises;
          // Mid-write slave: it drives ACK low on clock 9 and lets go after.
          if (write_ack && scl_rises == 10) { slave_low = false; }
        }
        if (last_scl && !high) {
          ++scl_falls;
          if (!write_ack) { advance(); }
        }
        last_scl = high;
      }
    }
  }
  bool line(int pin) const
  {
    if (!host_hardware::gpio[pin].high) { return false; }   // MCU open-drain drives low
    if (pin == SDA && slave_low) { return false; }
    return true;
  }
  bool input(int pin, int, bool)
  {
    process_events();
    return line(pin);
  }
};

slave_sim_t sim;

struct run_t {
  bool released;
  unsigned clocks;
};

run_t run_case(std::initializer_list<int> bits)
{
  host_hardware::reset();
  host_hardware::gpio[SDA].high = true;   // pin_mode(input) leaves the latch high
  host_hardware::gpio[SCL].high = true;
  host_hardware::input = [](int pin, int mode, bool latch) { return sim.input(pin, mode, latch); };
  sim.arm(bits);
  const bool released = release_held_sda(SDA, SCL);
  sim.process_events();
  return {released, sim.scl_falls};
}

run_t run_write_ack()
{
  host_hardware::reset();
  host_hardware::gpio[SDA].high = true;
  host_hardware::gpio[SCL].high = true;
  host_hardware::input = [](int pin, int mode, bool latch) { return sim.input(pin, mode, latch); };
  sim.arm_write_ack();
  const bool released = release_held_sda(SDA, SCL);
  sim.process_events();
  return {released, sim.scl_falls};
}

run_t run_stuck()
{
  host_hardware::reset();
  host_hardware::gpio[SDA].high = true;
  host_hardware::gpio[SCL].high = true;
  host_hardware::input = [](int pin, int mode, bool latch) { return sim.input(pin, mode, latch); };
  sim.arm_stuck();
  const bool released = release_held_sda(SDA, SCL);
  sim.process_events();
  return {released, sim.scl_falls};
}

struct expect_t {
  const char* name;
  bool want;
};

int failures;
void check(const expect_t& e, const run_t& got)
{
  const bool ok = got.released == e.want;
  std::printf("%-26s released=%d want=%d clocks=%u %s\n",
              e.name, int(got.released), int(e.want), got.clocks, ok ? "OK" : "MISMATCH");
  if (!ok) { ++failures; }
}
}  // namespace

int main()
{
  // The 1 bit is a data bit, not the end of the byte: the slave takes SDA back
  // for the following 0 bit, so the old "clock until SDA high, then STOP" exits
  // early and the STOP does not hold.
  const auto one_then_zero = run_case({0, 0, 1, 0, 0, 0, 0, 0});
  check({"0,0,1,0,... (issue case)", true}, one_then_zero);
  if (one_then_zero.clocks > 9) { std::printf("clocks exceed 9\n"); ++failures; }

  // A slave whose remaining bits are all 0 releases only in the ACK slot.
  const auto all_zero = run_case({0, 0, 0, 0, 0, 0, 0, 0});
  check({"0,0,0,0,0,0,0,0", true}, all_zero);
  if (all_zero.clocks > 9) { std::printf("clocks exceed 9\n"); ++failures; }

  // Already released after one 0 bit: one clock plus STOP is enough.
  const auto one_zero_then_ones = run_case({0, 1, 1, 1, 1, 1, 1, 1});
  check({"0,1,1,... (benign)", true}, one_zero_then_ones);

  // Reset during a slave WRITE: the slave ACKs on clock 9, so a 9-pulse budget
  // ends on a held-low ACK; the original's 9 clocks + STOP had a 10th pulse.
  const auto write_ack = run_write_ack();
  check({"write mid-ACK (10th pulse)", true}, write_ack);

  // A peripheral that never releases must not spin forever.
  const auto stuck = run_stuck();
  check({"stuck SDA", false}, stuck);

  std::printf("failures=%d\n", failures);
  return failures != 0;
}
