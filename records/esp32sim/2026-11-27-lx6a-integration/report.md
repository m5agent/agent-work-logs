# Integration and regression results

The classic shared controller implementation and board manifests landed with the single shared MPU6886 model. The conflict was in the shared device module list. The merge preserved exports for the earlier S3 boards and for the two Atom families.

| Board | Arduino docs | Stock UIFlow2 |
| --- | --- | --- |
| Atom Lite | 5/5 PASS | PASS |
| Atom Matrix | 5/5 PASS | PASS, including LED layout |
| Atom Matrix v1.1 | 5/5 PASS | PASS, including LED layout |
| AtomU | NOT RUN, no dedicated docs examples | M5Burner catalog PASS. GitHub v2.5.3–v2.5.5 launcher FAIL with missing M5Things. |
| Atom Echo | 3 DOCS-DEFECT, original sketches do not compile | All tested GitHub v2.5.1–v2.5.5 launcher FAIL with missing M5Things. REPL, button, RGB, mic and speaker PASS on the representative stock image. |

The pinned fixture decoded two distinct NEC frames through RMT RX and reported no frame on idle. AtomU raw PDM produced high, low and mixed sample words, while its idle run produced 20,480 all-low words. LX6-C owns the continuous DAC implementation, so its integration milestone covers the cyclic DAC fixture.

CoreS3, Cardputer-ADV, Tab5 and all S3-A through S3-D qualification outcomes reproduced. Both ADV CAP NFC cases passed. Native and WASM Clippy passed. The four instruction sentinels retained identical counts and serial output. The workspace ran 2014 tests with zero failures.

Run `tools/run-lx6-atoms.sh` using the pinned prebuilt sketches and UIFlow2 images. Replay the RMT and PDM fixture with `docs/fixtures/lx6-receivers/replay.py` and the binaries identified in [run.json](run.json). The native CLI used the repository release profile. The workspace used release with LTO off, eight codegen units and debug symbols off. Normalized summaries retain hashes and verdicts, with local paths and full captures omitted.

Physical hardware, browser guests and cloud sync were NOT RUN. The pre-merge tree is the first parent of `e9393f379071418e0acc196ada729ea0f338e5d6`. Rollback in shared history would use a new revert commit of that merge, with the first parent as the mainline.
