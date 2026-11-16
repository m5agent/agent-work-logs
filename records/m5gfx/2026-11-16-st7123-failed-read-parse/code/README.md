# Host-side reproduction

`get_touchraw_check.cpp` copies `adv_info_t`, `touch_report_t` and the
`getTouchRaw()` body from M5GFX `28d4794`
(`src/lgfx/v1/platforms/esp32p4/Touch_ST7123.inl:109-157`), then replaces
`_readParams()` with a mock that can fail one of the three register reads and
leaves the destination buffer untouched (or partly filled) like a real
NACK/timeout. The stack is pre-filled with `0xFF` before each call.

`fw_info_check.cpp` copies `_read_fw_info()` (`:47-71`) with the same mock to
check the "init succeeds when the chip never answers" side note.

Run:

```bash
clang++ -std=c++17 -O0 -fno-inline get_touchraw_check.cpp -o get_touchraw_check
./get_touchraw_check
clang++ -std=c++17 -O0 fw_info_check.cpp -o fw_info_check
./fw_info_check
```

`-O0 -fno-inline` is required: the reproduction relies on the next call frame
reusing the stack region pre-filled by `poison_stack()`. Outputs are stored in
`../evidence/`. This harness models only the parsing path; it does not exercise
I2C, controller timing, the ST7123 model, or a panel.
