# StackChan controller-confirmed browser test hold

- Date: 2026-11-27
- Result: PASS on two Chrome virtual-device replays of the corrected gesture schedule
- Work type: hosted gate diagnosis and guest validation
- Source: [Pages run](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/46011319479)
- Hardware validation: NOT RUN

Each replay observed six real keyboard and pointer pulses through the original Si12T driver and actual Chrome Worker disappearance. Both replays used the hosted build's frozen QEMU WASM and exact StackChan Flash.

[Report](report.md) · [Run index](run.json) · [Evidence](evidence/)
