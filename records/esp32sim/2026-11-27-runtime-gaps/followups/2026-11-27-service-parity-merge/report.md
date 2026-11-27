# Verification after merging Device Service parity

The runtime-gap branch `2fba23b0305cc96a3bd9b9ccb78d0f3ed50523d8` merged cleanly with the Device Service parity milestone `1bde80f2472c4b4763a66fde63fad9fb4906a7ae`. The merge commit is `9c0447e8e38d0bafc2f124e6e8b8cc5994d30eee`. The validation used independent CLI child processes and inherited Unix control sockets.

## Build and suite

```sh
export CARGO_PROFILE_RELEASE_LTO=off
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=8
export CARGO_PROFILE_RELEASE_DEBUG=0
cargo build --release --locked --bin esp32sim --bin esp32sim-p4
cargo test --release --workspace --no-fail-fast --locked -- --include-ignored --skip external_
cargo clippy --workspace --all-targets -- -D warnings
cargo clippy --release --target wasm32-unknown-unknown -p esp32sim-wasm --features jit-tests -- -D warnings
```

The CoreS3 launcher recovery used the merged tree's tracked runner when the old wrapper pointed at a retired worktree. The Tab5 SDK MSC case used the original reference image with SHA-256 `1d404ac87703a9647fe38735211c031675f04096d4ef3faa0a20f08ba3d80b50` and full-speed attachment. Board suites used the pinned documentation firmware and their established oracles.

The accepted AtomS3 limitations are five `DOCS-DEFECT` outcomes. The AtomS3 Lite button and the AtomS3 and AtomS3 GC9107 button and IMU sketches omit `Serial.begin`, so their fixture serial assertions fail on both baseline and candidate. The stock REPL runs exercise the respective boards independently. These results stay visible in the suite summaries.

The supplemental controller replays again read the DSI RX FIFO as `98 81 0c`, matched both host-image sector hashes over the full-speed MSC path, reported both C6 software reset reasons with intact flash, and received the original NanoC6 light's acknowledged leave and post-rejoin Off.

## Control socket

The Classic Core2 checks boot the stock UIFlow2 image with no SD image prepared. They compare the device snapshot with board/panel reads, drive and release a GPIO through the documented socket commands, and read the provisioned snapshot and final Flash export. An unsupported SD insertion returns an explicit rejection. The separate prepared-media boot uses the original Core2 microSD sketch. Its media generations advance on insert, reset and eject. The guest completes actual SPI reads after insert. The PaperDIY regression verifies its physical card-detect GPIO along the same control path.

The restricted STA fixture obtained a virtual DHCP lease, exercised link down/up and radio down/up and checked that RX stayed unchanged while radio was down. This is virtual-device validation. The control probe does not measure physical radio behavior.

The first PaperMono Flash and touch trials overlapped the bulk matrix and reached their wall-clock limits. Their traces are preserved in the local run evidence. The first Classic Core2 probe also attempted the optional PMIC node before using the documented board and panel properties supported by that profile.

Both PaperMono controls passed on the same binary with the original fixture assertions after the concurrent matrix exited.

## Merged gate results

| Gate | Observed result |
| --- | --- |
| Workspace tests | 2,045 passed and 34 external checks filtered by the same command as the initial gate |
| Clippy | Native and WASM passed with `-D warnings` |
| Sentinels | Four workloads matched baseline instructions and serial bytes across three repeats |
| Reference boards | CoreS3 15/15, Cardputer-ADV 11/11, Tab5 25 PASS, one documentation defect and two cases lacking sketches |
| Board batches | All replayable cases passed, with known documentation defects retained. Both Core2 PMIC variants passed the 15-case gate. |
| Radio and C6 | All nine connected or isolated radio cases passed, and the C6 Thread and Zigbee paths passed. Two ADV receiver runs exceeded their 140-second wall limit under load and passed the same delivery checks in the targeted replay. |
| PaperColor recovery | The loaded PM1 case recorded the expected power-on restart before the 900-second runner limit. The targeted replay finished all 112 guest seconds and passed the same verifier. The stock home, USB REPL, buttons and no-input control also passed. |
| Service parity | Classic Core2 state, Flash and SPI SD passed. PaperMono Flash and touch state, PaperDIY SD hot-plug and restricted STA passed. |

## Tab5 stock home timing

The previous 34.81 s and 41.04 s comparison used different release profiles. The baseline used fat LTO and one codegen unit. The candidate used LTO off and eight codegen units. Host load also differed. The timings are retained in the original record with the corrected build metadata.

The follow-up builds source `4e257b6be8ee0ed706c2e509d8f31ef7472a424b` and the merged head with the same Rust 1.100.0 toolchain and release profile listed above. It keeps the stock UIFlow2 v2.5.3 Flash image, P4 and C6 startup configuration and ROM directory fixed. The runs alternate baseline/candidate, candidate/baseline, then baseline/candidate. Before starting each run, the harness samples host CPU idle once per second and requires three successive samples at or above 85%. It continues sampling while the simulator runs.

The native launch uses `esp32sim --chip p4 --boot rom --board m5stack-tab5 --flash-image "$FW" --service-fd "$FD" --max-seconds 9 --no-dump --console both --coproc "$C6_CONFIG"`. The client requests the RGB565 framebuffer approximately every 0.15 guest seconds. Home timing starts when the child is spawned and ends when the client receives the first frame whose RGB565 payload has SHA-256 `e6d01521e3dfe04d2971aa8fe8068c6f79988b62c2a2f3feb6a1ae6cf616d67a`.

The idle-host run is **NOT RUN**. Three quiet-window waits of 120, 360 and 900 seconds yielded zero qualifying starts on the shared host. The last ten one-second samples showed 29.2% to 40.3% CPU idle. Other guest runs and background processes remained active.

The same six boots were then run as a loaded-host diagnostic. CPU idle is the median across each boot and includes simulator use. CPU time is user plus system time for the simulator over the entire nine-guest-second replay. Every run received the same home payload at the 5.94 guest-second frame poll and recorded 3,240,000,000 P4 core 0, 3,178,761,696 P4 core 1, and 1,438,400,000 C6 instructions by exit.

| Pair | Baseline wall home (s) | Merged wall home (s) | Baseline / merged CPU idle (%) |
| --- | ---: | ---: | ---: |
| 1 | 17.34 | 26.60 | 0.55 / 0.00 |
| 2 | 14.51 | 17.67 | 0.55 / 2.40 |
| 3 | 13.65 | 13.18 | 11.70 / 10.40 |
| Median | 14.51 | 17.67 | |

The median total simulator CPU times were 17.95 s and 18.89 s. The third pair had the most comparable CPU idle and total simulator CPU times of 17.23 s and 17.49 s. The change in wall time varied in magnitude and direction. An idle-host wall-time regression remains unverified. No performance patch was made on the basis of these loaded pairs.
