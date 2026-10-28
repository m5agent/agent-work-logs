# Reproduction code

The executable runner, patch, and contract test are maintained in the public
source repository:

- `tests/firmware/core2_handoff_trace/run_pause_sweep.py`
- `tests/firmware/core2_handoff_trace/run_wdt_liveness.py`
- `platform/tests/test_core2_legacy_status_cas.py`
- `patches/qemu-m5stack-peripherals/0075-esp32-legacy-status-cas-correlation.patch`

Source commit:
[`66af02cc6061bded00659ee13632f5e3a9a397dc`](https://github.com/m5agent/m5stack-esp-emulator/commit/66af02cc6061bded00659ee13632f5e3a9a397dc)

The record includes the generated patch and machine summary; raw QEMU stderr,
frame, and local Device Service state remain in ignored workspace storage.
