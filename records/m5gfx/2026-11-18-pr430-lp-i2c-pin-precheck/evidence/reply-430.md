Reviewed the change against the ESP-IDF driver it mirrors.

**Conclusion** — no blocker. `lp_pads_accepted()` reproduces the driver's pin rules exactly, and it runs before the first pad access in the LP bring-up path, so a rejected pair no longer loses the HP/LP routing it had.

**Evidence level** — code-level verification (source parity with ESP-IDF) plus a host-level check of the extracted predicate. `hardware validation` / `virtual-device validation`: NOT RUN here (see the end).

**Cross-checks**
- `lp_pads_accepted()` (`common.inl:1867-1875`) matches `s_lp_i2c_pins_config()` in IDF v5.4.4 (`i2c_common.c:366-386`), v5.5.4 (`:367-387`), v6.0.3 (`:358-378`) and v6.1.1 (`:358-378`): `rtc_gpio_is_valid_gpio()` on both pins first, then the fixed pair only under `!SOC_LP_GPIO_MATRIX_SUPPORTED`.
- The `#if !defined(LGFX_LP_GPIO_MATRIX)` guard is equivalent on these targets. M5GFX defines that macro only when the SoC has the LP GPIO matrix and `<driver/lp_io.h>` exists (`:192-196`); a P4 without that header does not define `LGFX_LP_I2C_LEND_PADS` at all (`:1863-1865`), so the fixed-pair branch is not compiled there.
- The fixed pairs match IDF: C6 6/7 in all four releases; C5 6/7 in 5.4.4 and 2/3 in 5.5.4 / 6.0.3 / 6.1.1. The per-pin `rtc_io_num_map` agrees too: on C5 5.5 GPIO7 is `-1`, so 2/3 is the only accepted pair; C6 maps 0-7 and P4 maps 0-15.
- Placement: the check is the first pad-affecting statement of the LP branch (`:2341`), before `release_lp_pad()` / `pinMode()` (`:2345-2348`) and `i2c_stop()` (`:2351`). `init(port, sda, scl)` configures the pins through `setPins()` first (`:2454-2462`), so the check sees an uninitialized context and a rejected call has no side effect on the new pins.
- Host check: I extracted the predicate verbatim and ran it with the real fixed-pair macros and the real LP-IO pin sets. C6 6/7 accept, 4/5 reject; C5 5.4 6/7 accept; C5 5.5 2/3 accept while 6/7 reject; P4 11/9 and 0/15 accept, 18/19 reject. All 20 cases came out as expected.

**Minor, non-blocking**
- With `LGFX_LP_I2C_LEND_PADS` active, `const bool lp_pads = rtc_gpio_is_valid_gpio(...)` at `:2363` is now always true where it is reached; it can stay as a guard or be dropped.
- On an SDK without `LP_I2C_SDA/SCL_IOMUX_PAD` the fixed-pair half compiles out, so a valid-but-wrong pair still reaches the driver and takes the old failure path. IDF 5.4.3+ and Arduino-ESP32 3.1.3 / 3.3.0 define both, so this only concerns older or other SDKs.

**Not covered / one request**
- CI is 26/26 green, but that is build only. I have no C5/C6 hardware, and I found no LP I2C model in the local emulator tree (C6 has QEMU profiles, P4 has the native profile), so the "routing survives" effect cannot be observed in a virtual run here. The P4 result in the body exercises the matrix path, where any LP pair is accepted.
- Could you add one C5 or C6 check for the fixed-pair path: keep a valid-but-wrong LP pair (for example C6 GPIO4/5) on another function, call `i2c::init(lp_port, 4, 5)`, and confirm it returns `invalid_arg` while that pair's IO MUX routing and level are unchanged? That is the exact behaviour this PR fixes.

Reviewed record with the IDF excerpts and the host harness: https://github.com/m5agent/agent-work-logs/blob/c2c5a8cc76c83ad007c1d2219ba16c1e87d945f9/records/m5gfx/2026-11-18-pr430-lp-i2c-pin-precheck/README.md
