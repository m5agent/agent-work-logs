// Runtime equivalence check for detection_gpio_snapshot_t::restore_to_snapshot.
// transaction.inl only: detector_runner.inl is the PR's other file and does not
// compile with log arguments enabled, so it is deliberately excluded here.
#include "board_detect/board_detect.hpp"
#include "board_detect/ops.inl"
namespace m5gfx { namespace board_detect {
#include "board_detect/transaction.inl"
}}
#include <cstdio>
#include <initializer_list>

using namespace m5gfx::board_detect;

static void scenario(const char* name, std::initializer_list<int> requested,
                     const std::int8_t* snapshot_pins, std::size_t snapshot_count)
{
  detection_gpio_snapshot_t snap;
  pin_list_t list { snapshot_pins, static_cast<std::uint8_t>(snapshot_count) };
  if (!snap.capture(list, pin_list_t { nullptr, 0 }, false))
  {
    std::printf("%s CAPTURE_FAILED\n", name);
    return;
  }
  std::int8_t values[max_detection_pins] = {};
  std::size_t count = 0;
  for (auto pin : requested) { values[count++] = static_cast<std::int8_t>(pin); }

  hm::clear();
  snap.restore_to_snapshot(values, count);
  std::printf("%s logs=%zu", name, hm::logs().size());
  for (const auto& line : hm::logs()) { std::printf(" [%s]", line.c_str()); }
  std::printf("\n");
}

int main()
{
  const std::int8_t five[] = { 5 };
  const std::int8_t two[] = { 5, 0 };
  scenario("snapshot{5} req{-1,-1}",     { -1, -1 }, five, 1);
  scenario("snapshot{5} req{5}",         { 5 },      five, 1);
  scenario("snapshot{5} req{7}",         { 7 },      five, 1);
  scenario("snapshot{5} req{0}",         { 0 },      five, 1);
  scenario("snapshot{5} req{7,9}",       { 7, 9 },   five, 1);
  scenario("snapshot{5,0} req{0}",       { 0 },      two,  2);
  scenario("snapshot{5} req{-1,7}",      { -1, 7 },  five, 1);
  return 0;
}
