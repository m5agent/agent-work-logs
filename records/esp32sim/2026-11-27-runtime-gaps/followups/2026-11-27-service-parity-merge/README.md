# Runtime gap branch and Device Service parity merge

- Date — 2026-11-27
- Type — merge verification and timing follow-up
- Source — [runtime gap branch at 9c0447e8](https://github.com/m5agent/esp32sim/tree/9c0447e8e38d0bafc2f124e6e8b8cc5994d30eee)
- Environment — macOS AArch64, native and WASM virtual-device validation

The merged head passed the runnable regression and Device Service control checks. Known documentation defects and unavailable sketches remain visible. The Tab5 comparison recorded three matched-build pairs under load. The idle-host replay remains open because the host never reached the required idle threshold.

- [Report](report.md)
- [Execution manifest](run.json)
- [Evidence summaries](evidence/)

Hardware validation was outside the scope of this run.
