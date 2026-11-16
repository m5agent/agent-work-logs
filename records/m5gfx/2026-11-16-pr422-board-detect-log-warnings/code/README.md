# Host harness for M5GFX PR #422

The M5GFX `board_detect` implementation is header-only and has a documented
replacement I/O hook, `M5GFX_BOARD_DETECT_IO_HEADER` (`src/board_detect/detect_io.hpp:135`).
`stub_io.hpp` implements that contract so the real `src/board_detect/*.inl`
files compile on the host without an Arduino/ESP-IDF toolchain.

The ESP_LOG macros are the only thing that changes between the two builds:

- default: `ESP_LOGE/W/I/D/V` expand to `do {} while (0)`, so all log arguments
  are discarded — the same preprocessor behaviour as `CORE_DEBUG_LEVEL=0`.
- `-DHM_LOG_LEVEL=4`: log arguments are passed to a no-op variadic function and
  are therefore evaluated — the same code path as an `ESP_LOGD`-enabled build.

`tu.cpp` includes the real `board_detect/board_detect.inl`.

`tx_check.cpp` includes only `board_detect.hpp`, `ops.inl` and `transaction.inl`
(not `detector_runner.inl`) and checks `detection_gpio_snapshot_t::restore_to_snapshot`
at runtime with log capture. This isolates the second half of the PR, which is
the half that still compiles on both commits.

## Run

```sh
M5GFX_SRC=/path/to/M5GFX ./run.sh
```

`M5GFX_SRC` must point at a clean checkout of the commit under test. Check out
`28d4794` for master and `ab6cf1c` for the PR head.

The expected result:

| checkout | log arguments off | `ESP_LOGD` enabled |
| --- | --- | --- |
| master `28d4794` | 6 warnings, including `transaction.inl:59` and `detector_runner.inl:51` | compiles cleanly |
| PR head `ab6cf1c` | 4 warnings, the two reported ones gone | **error**: `detector_runner.inl:66: use of undeclared identifier 'family'` |

This harness models only the compile/log-macro behaviour and the snapshot
restore logic. It does not exercise I2C, GPIO, a panel, or firmware.
