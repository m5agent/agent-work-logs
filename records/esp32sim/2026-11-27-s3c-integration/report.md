# Integration and regression results

The merge keeps the three S3 batch board lists and their memory defaults. StopWatch, StamPLC and Tab5 share the RX8130 implementation and its 12-bit countdown. Tab5 uses the shared INA226 and PI4IOE5V6408 models. Its original charger input and PA rail wiring are mapped through the expander's input and driven-output APIs.

| Board | Arduino PASS | DOCS-DEFECT | Stock UIFlow2 |
| --- | ---: | ---: | --- |
| StamPLC | 12 | 1 | PASS |
| StackChan | 25 | 1 | PASS |

CoreS3 passed 15/15 and Cardputer-ADV passed 11/11. Both NFC UID variants produced 33 guest selections. Tab5 retained 25 PASS, one DOCS-DEFECT and two NOT RUN. Its guest reported 7980 mV and charging, and firmware toggled the PA and USB rails independently. All S3-A and S3-B verdicts reproduced on the merged tree.

The S3-C batch includes a refresh of two P4 SMP instruction-count goldens and four P4 ESP-Hosted report goldens. The previous integration baseline reproduced those six mismatches. The updated instruction counts match that baseline's executed guest output, and the report change represents the existing four SDIO data pins as an array. The refreshed goldens passed. No workspace failures remained.

Native and WASM Clippy used the repository flags with warnings denied. The workspace used the optimized release profile with LTO off, eight codegen units and debug symbols off. The native CLI and instruction sentinels used the repository release profile. S3, C3 and C6 hello and Pocket Tank retained identical instruction counts and serial output. The S3-B replay used the empty-array default required by Bash 3.2.

Run the repository `tools/run-s3c-docs.py` and `tools/check_s3c.py` with the prebuilt firmware and stock images identified in [run.json](run.json). Set `ESP32SIM_ROM_DIR`, supply the original SD, microphone and camera stimuli and run the reference suites with the same candidate binary. Normalized summaries retain hashes and verdicts. Local paths, raw images and full traces were omitted.

Physical hardware and browser guest execution were NOT RUN. The pre-merge tree is the first parent of `d992a1171db4aed2504603fa3fa91b259be2fca4`. Rollback in shared history would use a new revert commit of that merge, with the first parent as the mainline.
