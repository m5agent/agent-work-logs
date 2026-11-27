# C6-A NanoC6 and Nesso N1 integration

| Board | Arduino docs | Stock UIFlow2 |
| --- | --- | --- |
| NanoC6 | 15/15 PASS | PASS |
| Arduino Nesso N1 | 11/11 runnable PASS, power-1 DOCS-DEFECT | PASS |

The NanoC6 temperature sketch detected the ENV-III SHT30 at 0x44 and sent multiple valid measurements. The missing-unit control reported a missing SHT30. A guest software reset was followed by the transmitted rejoin request and received response. Thread and Nesso LoRa used peer and isolated controls. Nesso power-1 uses the wrong API enum. NanoC6 BLE was NOT RUN because there was no pinned runnable docs case.

The peer runner receipts omit timed serial arguments. The first stock replay reached boot but lacked REPL input. Replaying the accepted REPL commands and timing on the same binary restored NanoC6 button, UART and ENV-III readbacks and Nesso N1 battery readback.

The merge retained one PI4IOE5V6408. The resolved shared SX1262 implementation retains PaperMono LoRa and the full version register while accepting the Nesso peer route. Both ADV CAP LoRa variants passed payload forwarding and receiver checks. Both previously merged ADV CAP NFC variants remained green.

Run `tools/run-nanoc6-docs.py` and `tools/run-nesso-n1-docs.py` with their matching `check-` scripts, the pinned ROM and prebuilt firmware. For peer, isolation and recovery cases, run `tools/run-nanoc6-peers.py` and `tools/run-nesso-n1-lora.py` using the board fixtures and documented virtual times.

## Common gate

CoreS3 15/15, Cardputer-ADV 11/11, Tab5 25 PASS with one DOCS-DEFECT and two NOT RUN, and all earlier batch verdicts reproduced. Both ADV CAP NFC variants selected the tag 33 times each. Native and WASM Clippy passed. The hello and Pocket Tank instruction sentinels retained the same counts and serial output. Release workspace tests passed 2030 with zero failures.

The native CLI used the repository release profile. The workspace used release with LTO off, eight codegen units and debug symbols off. The S3-B runner used a scratch Bash 3.2 compatibility adjustment. Full transcripts stayed outside the archive.

Physical hardware, browser guest execution and cloud sync were NOT RUN. The pre-merge tree is the first parent of `ef799a1332bfc98ce63077ee9efc814f1fa3f83c`. Rollback in shared history would use a new revert of the merge with the first parent as mainline.
