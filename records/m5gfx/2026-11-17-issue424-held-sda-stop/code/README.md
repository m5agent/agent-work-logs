# `release_held_sda()` host model

`sim_slave.cpp` links the production `src/board_detect/probe_hardware.inl` and drives
`release_held_sda()` against a modeled I2C slave. It does not copy the function text.

## Build

Use the M5GFX tree to test as `<repo>` (checked out at `b48dce0` or with the proposed
patch applied):

```sh
c++ -std=c++11 -O2 -Wall -Wextra -Wno-unused-function -Wno-unused-parameter -pedantic \
  '-DM5GFX_BOARD_DETECT_IO_HEADER="support/detect_io.hpp"' \
  -include <repo>/test/board_detect/support/native_devices_io.hpp \
  -I<repo>/test/board_detect -I<repo>/test/board_detect/stubs -I<repo>/src \
  sim_slave.cpp -o sim_slave
cd <repo> && /path/to/sim_slave
```

The `cd <repo>` is required because the harness and the production includes resolve
relative to the M5GFX root.

## Model

- Entry state SCL high, SDA low (the state the issue reports when
  `probe_i2c_bus_present()` starts on ToughC5).
- The slave presents a bit on each SCL falling edge; a 0 bit holds SDA low.
- After eight bits the slave releases SDA in the ACK slot.
- The `write mid-ACK` case models a slave that was receiving: it drives ACK on clock 9
  and releases after it.
- Mid-byte STOP attempts are ignored, the same worst case the issue describes.
- `host_hardware::events` is replayed to follow the real SCL edges produced by
  `pin_low` / `pin_high`, so the modeled slave sees the production clock sequence.

## Expected

| Case | `b48dce0` | 9-clock patch | 10-clock variant |
| --- | --- | --- | --- |
| read `0,0,1,0,...` | fail | pass | pass |
| read `0,0,0,0,0,0,0,0` | pass | pass | pass |
| read `0,1,1,...` | pass | pass | pass |
| write mid-ACK | pass | fail | pass |
| stuck SDA | pass (returns false) | pass (returns false) | pass (returns false) |

The 10-clock variant is the proposed patch with `++i < 10` instead of `++i < 9`.
It is a model-level variant; it was not submitted upstream and was not tested on hardware.
