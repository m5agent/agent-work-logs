# LX6-A and S3-A merge qualification

- Date 2026-11-27
- Result PARTIAL
- Work type code change and firmware diagnosis
- Request batch integration and investigation of factory startup on AtomU and Echo
- Source [esp32sim merge milestone](https://github.com/m5agent/esp32sim/tree/8e17dcd553fbd59b2dc9034cb5bd8eecb0884302)
- Environment native AArch64 on macOS with independently replayed ESP32 and ESP32-S3 guest images

Atom Matrix and AtomS3 now share one MPU6886 model. The merged branch retained the accepted classic and S3 results. The AtomU and Echo stock v2.5.4 images still abort in the factory launcher because the headless startup script imports `M5Things` unconditionally and both images lack that module.

[Report](report.md) · [Run identities](run.json) · [Merge gate](evidence/merge-gate-summary.json) · [Stock startup](evidence/startup-summary.json)
