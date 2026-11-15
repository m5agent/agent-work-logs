# m5stack/uiflow-micropython #130: webrepl hardcodes the WebSocket endpoint and drops the runtime gate

- Date: `2026-11-16`
- Result: `REVIEW` (source and released-artifact verification; no runtime reproduction)
- Work type: `issue` triage / `review`
- Source: https://github.com/m5stack/uiflow-micropython/issues/130 (opened 2026-11-15T22:44Z by FxIII, open, no prior comments)
- Source version: `m5stack/uiflow-micropython@54b1d242` (`master`), `webrepl.c` blob `0f23c8e2`; release tag `2.5.4` @ `e4371188`
- Environment: macOS; local clone plus GitHub contents API; public 2.5.4 release images; no device or emulator run
- Evidence class: **code-level verification** (reproducible source references, commit history and binary string inspection of the published images)

## Conclusion

The report is correct in substance: the shipped `webrepl` component connects to a hardcoded plaintext endpoint, does not read the `uiflow`/`server` NVS key, and starts unconditionally on boards that compile it in. Two scope statements need correction.

Confirmed:

1. **Hardcoded endpoint.** `webrepl.c:27` defines `ws://uiflow2.m5stack.com/ws/realtime?role=device&mac=%s`; `webrepl_build_uri()` (`110-126`) fills in the MAC only. The file has no NVS access at all.
2. **NVS `server` ignored.** `m5things` reads `uiflow`/`server` for the MQTT broker (`m5things.c:2198`, fallback `mqtt://uiflow2.m5stack.com:1883` at `2202`); `webrepl` does not. The factory NVS image sets `server=uiflow2.m5stack.com` (`partition_nvs.csv:3`) and is packed into the release image (`Makefile:198`).
3. **Runtime gate removed.** `05c2ca20` deleted `webrepl_read_server()`, `webrepl_should_start()` and the NVS-built URI; `main.c` now creates `webrepl_task` unconditionally under `#if WEB_REPL_ENABLE` (`main.c:319-321`). No reference to the old gate remains anywhere in `m5stack/`.
4. **REPL injection path.** `webrepl_process_text_message()` (`299-335`) accepts any JSON frame with `type == "clientMessage"` and forwards the string/number payload to `webrepl_queue_input()` (`181-195`), which lands in `stdin_ringbuf` via `webrepl_drain_rx_to_stdin()` (`197-218`). A `0x03` byte takes the keyboard-interrupt path (`200-205`), so an injector is not limited to an idle REPL.
5. **No client-side authentication or TLS.** The `esp_websocket_client_config_t` at `455-466` sets no `headers`, no token and no `wss://`; the MAC in the query string is the only identifier and travels in clear text. Whether the server enforces MAC ownership is outside this repository (`NOT VERIFIED`).

Corrections:

- **The old gate was not general user configuration.** At `7a5f7598` the task started only when `uiflow.server == "aiflow.m5stack.com"` (`webrepl.c:144-147` at that commit). With the factory default `server=uiflow2.m5stack.com`, webrepl did not start at all; a user-chosen self-hosted host also did not enable it. So "bypasses runtime gating" is accurate, but "it used to respect the user's `server` setting" overstates the old behaviour: it was a single-host allow-list used as a provisioning switch.
- **"Almost all S3/P4 board configs" is too broad.** 13 of 53 board directories set `WEB_REPL_ENABLE 1` (`CMakeListsDefault.cmake:174-179` defaults to `0`): AirQ, AtomS3, AtomS3R, CardputerADV, CoreS3, Dial, PaperMono, PaperS3, StackChan, StamPLC, StickS3, StopWatch, Tab5. The models named in the report are all in that set, but e.g. Cardputer, StampS3 and StampP4 are not.

Release mapping: `2.5.0` carries the gated implementation (blob `705b2491`); `2.5.1` and `2.5.2` carry the dynamic-MAC version (blob `3a2e7ef7`); `2.5.3`, `2.5.4` and current `master` carry the P4-MAC variant (blob `0f23c8e2`). The fixed developer MAC introduced by `05c2ca20` was replaced by `8003d01a` 19 minutes later and is not in the `2.5.1`+ source; intermediate CI images were not checked.

## Key evidence

- Source: `webrepl.c:27`, `110-126`, `181-195`, `197-218`, `299-335`, `442-447`, `455-466`; `main.c:319-321`; `m5things.c:2198-2205`; `partition_nvs.csv:3`; `Makefile:198`.
- History: `7a5f7598` (gated introduction), `05c2ca20` (gate and NVS removed), `8003d01a` (MAC derived from device).
- Published images: 2.5.4 CoreS3 (`a7b2483a…`, 16,121,856 B) and StickS3 (`44fca755…`, 8,384,512 B) both contain the URI template, `webrepl_task` and `webrepl_ws` strings, and zero `wss://` strings.
- `evidence/checks.txt`, `release-bin-strings.txt`, `webrepl-key-lines.txt`, `original-gate-7a5f7598.txt`.

## Files

- `report.md`: full analysis, commands and limits
- `run.json`: structured record
- `evidence/`: line excerpts, blob hashes, release image hashes and string matches

## Not covered

- `NOT RUN` runtime reproduction: no `clientMessage` was injected into the production channel and no on-path proxy was used. The observed call chain is source-level only.
- `NOT RUN` device or emulator boot: the shipped image is a retail build, so the `ESP_LOGD` markers for the webrepl task would not be visible; source and binary inspection already answer the reported questions.
- `NOT RUN` server-side behaviour: whether the server authenticates devices, validates frame senders or enforces MAC ownership is not in this repository.
- `NOT RUN` web IDE opt-in: whether the UIFlow2 web front end exposes an explicit opt-in for this channel was not checked; no device-side opt-in exists.
