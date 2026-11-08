# UIFlow UHF inventory parser validation

## Background and source

Issue #89 reports inventory decoding failures on Core2 with UIFlow 2.4.3. The public baseline searches for the binary byte `0x7E` before respecting the declared payload length. EPC and CRC data can contain that byte, producing premature frame truncation. [Original issue](https://github.com/m5stack/uiflow-micropython/issues/89)

The JRD4035 driver and Unit wrapper are byte-identical between public tag 2.4.3 and public master base `f20d5a00e8c9106aae1d944f3d6f1128839f59cb`. The final patch changes only `inventory()` and `_receive()`. The remaining 58 methods, wrapper and license bytes are unchanged. The two changed methods exactly match the executed final source overlay. The submitted source commit is `8006dd8a2b0c39b8cac99e21f56ce80a65a837d8`. [Source and patch proof](evidence/source-contracts.summary.json)

## Execution

DeepSeek executed 35 retained sessions through Device Service `/api/v1`. Each probe made two normal `UHFRFIDUnit.inventory()` calls through guest `machine.UART`, the simulated UART controller and attached UHF Unit model. The Core2 model lacked the necessary controller wiring. CoreS3 PORT.A, UART1 RX1/TX2, exercised the shared driver and wrapper path.

The base was public CoreS3 UIFlow v2.5.5 preview, SHA256 `5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded`. The pinned runtime SHA256 was `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e`. The composition changed the VFS to load the byte-verified source overlays. Native application and other non-VFS bytes remained unchanged.

The coordinator independently checked all 35 execution receipts, 350 indexed ZIP members, effective images, VFS source readback, two live process-identity observations per run, download completion before cleanup, terminal histories and bound runtime exits. The final dsh turn completed normally with process exit 0. [Independent receipts](evidence/independent-receipts.summary.json), [executor closeout](evidence/executor-completion.summary.json)

## Findings and changes

The original public implementation reproduced four decode failures. The maintainer's proposed length-based parser corrected embedded-terminator handling. Guest execution then exposed two additional compatibility problems in that candidate. Bytearray item deletion raised `TypeError` during bad-checksum and noise resynchronization. A bulk UART read consumed a queued second frame into a local buffer, which was discarded after returning the first frame. [Maintainer proposal](https://github.com/m5stack/uiflow-micropython/issues/89#issuecomment-6574488896)

A separately preserved compatibility variant replaces four deletions with slice assignment. It passed the original eight vectors. The final variant adds `read(1)` to retain one-frame consumption. Its nine vectors passed. `inventory()` also returns an empty result when a successful payload is shorter than five bytes. The receiver evaluates declared length, terminator and checksum before returning a frame. [Public-base patch](patches/0001-fix-uhf-frame-parser.patch)

| Vector | Baseline | Original candidate | Slicing variant | Final fixed |
| --- | --- | --- | --- | --- |
| normal-inventory | PASS | PASS | PASS | PASS |
| embedded-7e-epc | FAIL | PASS | PASS | PASS |
| embedded-7e-crc | FAIL | PASS | PASS | PASS |
| synthetic-truncated-prefix | FAIL | PASS | PASS | PASS |
| short-valid-payload | FAIL | PASS | PASS | PASS |
| bad-checksum | PASS | FAIL | PASS | PASS |
| module-error-response | PASS | PASS | PASS | PASS |
| noise-before-valid | PASS | FAIL | PASS | PASS |
| queued-complete-frames | PASS | FAIL | NOT RUN | PASS |

The first response in the queued vector injects complete synthetic frames A+B atomically. The next command injects C. Baseline and final fixed returned A then B, with 24 unread UART bytes after call one. The original candidate returned A then C, with zero pending bytes after call one. All identifiers were generated solely for the fixture.

The summaries retain subject behavior and harness acceptance independently. Baseline has 5 PASS and 4 FAIL, with the four failures satisfying their defect-reproduction oracles. Original candidate has 6 PASS and 3 FAIL. Slicing-only has 8 PASS. Final fixed has 9 PASS. [Baseline](evidence/baseline.summary.json), [candidate](evidence/candidate.summary.json), [slicing variant](evidence/compatible.summary.json), [final fixed](evidence/fixed.summary.json)

## Acceptance layers

| Layer | Status | Scope |
| --- | --- | --- |
| build | NOT RUN | Official firmware rebuild. Python compile, Python 3.7 AST, Ruff and public-base patch checks passed. |
| transport | PASS | 35 guest UART executions, source readback and observed controller command/injection counters. |
| device_response | PASS | Final variant's nine declared response oracles. |
| data_behavior | PASS | Final variant's nine vectors, next-call recovery and queued-frame preservation. |
| visual_or_physical | NOT RUN | Physical RF and electrical properties. |
| delivery | PARTIAL | Source pushed to personal fork. Maintainer review and merge pending. |

## Boundaries

- These results are virtual-device validation on CoreS3 with source overlays. Original Core2 whole-device execution, original 2.4.3 binary execution, stock frozen-module behavior, official firmware rebuild and deployment are NOT RUN.
- Timed fragmentation within one response is NOT RUN / BLOCKED_FIXTURE. The model injects each configured chunk atomically for the next complete command. The truncated-prefix case exercised an incomplete input.
- `rx-frames-hex` mirrors configured responses. Application returns, serial source markers, UART pending-byte observations and controller command/injection counters provide the executed observations. The Unit state exposes no read-byte counter.
- Thirty-five methods, including inventory, share the receiver. Other command decoders, continuous inventory, arbitrary timing and long-duration reliability are NOT RUN. The candidate's 512-byte payload cap and absolute ticks deadline remain review boundaries.
- CRC-16/GENIBUS is used to construct fixtures. The driver does not independently validate the tag CRC field. RF, antenna, Gen2 air interface, read range, electrical behavior and power are NOT RUN.

## Reproduction and rollback

Apply the public patch to `f20d5a00e8c9106aae1d944f3d6f1128839f59cb`. Its temporary-index application check reproduced the recorded driver bytes. The second patch adapts the separately hashed maintainer overlay to the final version. Exact executed guest probes are indexed in the evidence. [Patch delta](patches/0002-micropython-maintainer-overlay-compatibility.patch), [probe inventory](evidence/probe-inventory.summary.json)

Run `python3 code/generate-fixtures.py` to generate the synthetic fixture inputs. All nine generated response queues and expected values were compared with the actual executed inputs. Configure the admitted UART Unit with each generated `initial_responses_hex`, compose the corresponding source overlay and guest probe into the public base VFS, then submit through Device Service. Check both ordered API results, source markers and UART counters. Semicolon-separated response entries advance on subsequent commands. [Fixture rules](evidence/fixtures.summary.json), [generator equality](evidence/fixture-generator.summary.json)

All 35 session histories are retained. Physical tag write, kill and lock operations were NOT RUN. Reverting the two-method patch restores the original source. Failed observations remain archived in the summaries.
