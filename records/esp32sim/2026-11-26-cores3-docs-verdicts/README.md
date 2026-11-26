# CoreS3 Arduino examples on esp32sim

- Date 2026-11-26
- Work type `code_change`
- Source `m5/cores3-fixes` on esp32sim base `5d620c21acb2becb473746d0dbb8bcc57f2dc7ac`
- Environment Native Rust simulator on macOS arm64, ESP32-S3 mask ROM, CoreS3 board profile
- Result `PASS` for the 15 prebuilt examples and UIFlow2 functional checks in virtual-device validation

The panel model now discards out-of-range pixel data before mirroring. The unchanged prebuilt sketches establish which display and console behavior comes from their library configuration. The automated verdicts combine framebuffer, PCM, FAT32, USB and controller observations.

- [Report](report.md)
- [Execution and input hashes](run.json)
- [Case verdicts](evidence/verdicts.md)
- [Negative controls](evidence/checker-controls.txt)
- [Instruction counts](evidence/bench-summary.json)

Physical CoreS3 and browser-WASM execution were `NOT RUN`. These runs exercised the native simulator. Public delivery is `NOT RUN` under the local-only task instruction.
