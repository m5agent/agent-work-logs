# Integration and regression results

The Paper board registry and memory defaults are merged with the earlier S3 profiles. The merge retains one RX8130 RTC and one ST25R3916 reader. The shared PM1 and IOE1 models preserve prior pin, IRQ and rail behavior and add the Paper connections. PaperS3 consumes the 32-bit buzzer duty samples across its two I2S slots. Dial retains its original sample conversion. RMT preserves sensor routing and the Paper LED trace.

| Board | Arduino examples | Stock UIFlow2 |
| --- | --- | --- |
| PaperDIY | 6/6 PASS | Home frame, USB CDC REPL, two button markers and idle control PASS |
| PaperS3 | 9/9 PASS | Home frame, USB CDC REPL, two touch points and idle control PASS |
| PaperMono | NOT RUN | Qualification beyond this milestone |
| PaperColor | NOT RUN | Qualification beyond this milestone |

PaperDIY showed the documented timed power actions, full grayscale frame and SD rendering. PaperS3 entered RTC timer sleep and resumed after 5.000 virtual seconds. Both buzzer sketches produced the expected ordered tones and silent gaps. The short wall-time service probe did not deliver a REPL response. The same native binaries and stock firmware produced the expected markers when replayed through the batch's virtual USB CDC fixture.

CoreS3, Cardputer-ADV, Tab5 and all S3-A through S3-C outcomes reproduced. Both CAP NFC cases passed. The workspace passed 2004 tests with zero failures. Native and WASM Clippy passed. The four instruction sentinels retained identical counts and serial output.

The native CLI used the repository release profile. The workspace used the optimized release profile with LTO off, eight codegen units and debug symbols off. To reproduce, run `tools/run-paper-docs.py` and `tools/check-paper-docs.py` with the firmware listed in [run.json](run.json), enable the original SD fixture for both boards, and use the matching stock images with their USB CDC and input scripts. The summary omits local paths and raw captures.

Physical hardware and browser guest execution were NOT RUN. The pre-merge tree is the first parent of `d6ae7a67809f135c812d5c21504853e682ce6cc4`. Rollback in shared history would use a new revert commit of that merge, with the first parent as the mainline.
