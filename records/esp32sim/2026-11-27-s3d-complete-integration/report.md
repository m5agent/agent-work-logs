# S3-D complete e-paper integration

| Board | Arduino docs | Stock UIFlow2 |
| --- | --- | --- |
| PaperDIY | 6/6 PASS | PASS |
| PaperS3 | 9/9 PASS | PASS |
| PaperMono | 25 PASS, 1 DOCS-DEFECT | PASS |
| PaperColor | 14 PASS, 2 DOCS-DEFECT | PASS |

All four stock images reached home, executed the USB CDC REPL marker and responded to scripted input against an idle control.

The first merge candidate regressed StackChan blank-tag formatting and PaperMono's buzzer waveform. The resolution restored StackChan's blank tag and PaperMono's packed I2S output. The initial mic and SD failures came from different test inputs. The final replay used the accepted 700 Hz and 1,200 Hz injection and the separate Mono and Color SD fixtures.

PaperMono kept the same visible 4-gray frame at both sampled points in its 1.000-second BUSY interval. PaperColor retained the same six-color frame during its 15.000-second BUSY interval. Both changed the visible framebuffer after BUSY ended. The transition times and frame digests are in the gate summary.

PaperMono NFC case nfc-4 initializes before IOE1 GPIO4 enables NFC power. PaperColor ir_nec aliases the IR output on GPIO48 with the feedback LED. PaperColor sht40 uses the pins that M5.update routes internally.

Conflict resolution kept one RX8130 for the existing and Paper boards, preserved old and new PM1 GPIO maps and BMI270 interrupt paths, and retained the S3-C NFC model behavior while adding PaperMono's Type 2 tag capability data. Shared RMT diagnostics and waveform callbacks both remain available.

Run the four `tools/run-paper*-docs.sh` scripts and `tools/check-paper-docs.py` with the pinned images and referenced board fixtures.

## Common gate

CoreS3 15/15, Cardputer-ADV 11/11, Tab5 25 PASS with one DOCS-DEFECT and two NOT RUN, and all earlier batch verdicts reproduced. Both ADV CAP NFC variants selected the tag 33 times each. Native and WASM Clippy passed. The hello and Pocket Tank instruction sentinels retained the same counts and serial output. Release workspace tests passed 2014 with zero failures.

The native CLI used the repository release profile. The workspace used release with LTO off, eight codegen units and debug symbols off. The S3-B runner used a scratch Bash 3.2 compatibility adjustment. Full transcripts stayed outside the archive.

Physical hardware, browser guest execution and cloud sync were NOT RUN. The pre-merge tree is the first parent of `5f795a9b84a5bde0afc2424c4c423079eeebb5ba`. Rollback in shared history would use a new revert of the merge with the first parent as mainline.
