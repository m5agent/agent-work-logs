# Native firmware-review cutover and original replay

## Scope

The workbench and dedicated review worker use emulator source [feb627f22e01cd1a530f63dd148285d3f39afe43](https://github.com/m5agent/m5stack-esp-emulator/commit/feb627f22e01cd1a530f63dd148285d3f39afe43). The reviewer uses revision `7cab78ca1629f9845977739fd2461f6b146793f4`. Both source branches advanced by fast-forward. The Xtensa executable was `cbc0ea74c5763a9d989562b7061516fb3489fdc4056ddce4e016d555c1b86bb2`. C6 and Tab5 retained their previous executables. The local browser assets were exported again with 42 byte-identical browser runtime files. GitHub Pages was left on its existing export.

The 2,283-case platform suite completed without failure with 10 skips. Browser host contracts and catalog, runtime-coverage, profile and snapshot checks passed. [Main CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44052052495) passed. The reviewer passed 129 tests and its API document was aligned with the implementation.

## Isolated qualification and production readback

The exact frozen release was first run with independent state and unchanged ROMs. PaperDIY mounted and wrote FAT32, then read back its write after a same-guest reset. The empty-slot control and old executable's reject-before-allocation control passed. A controlled Cardputer open-network guest and Cardputer ADV WPA2 guest completed DHCP and matched a fixed HTTP response. These observations cover STA in the controlled lab. Linux namespace review admission, AP, and generic DNS and UDP operations remain open. [Isolated release checks](evidence/isolated-preflight-summary.json)

Each resident endpoint returned the expected health and release bytes after cutover. The switch preserved both state directories and the 92 reviewer job rows. Verification at the switch boundary preserved 41 workbench sessions and all 100 visible review-worker sessions. The three post-switch replays subsequently added three device sessions and updated their existing review jobs in place. Under the existing 100-session worker retention cap, three older stopped sessions expired. A separate SQLite backup retained the pre-switch reviewer verdicts. Existing reviewer batch rows and event rows were unchanged. Startup and readback preserved credentials and submission settings. No review jobs, sessions or leases were active after the replays. [Readback counts](evidence/resident-readback-summary.json)

The launch controller stopped the old reviewer asynchronously. The first immediate check reported that the listener had not stopped before any install. Independent listener and launch registration checks then confirmed shutdown and the planned process resumed. The previous immutable release and integrity-checked SQLite backups were retained. Live rollback was not needed. The evidence summaries omit service addresses, raw credentials, job or session identifiers, and physical device identifiers.

## Reproduction

Use the emulator commit and the pinned native runtime above. Run the platform suite with
`PYTHONPATH=platform/tools python3 -m unittest discover -s platform/tests -p 'test_*.py'`.
Run the browser host contracts with `npm run --prefix platform/tests test:contracts`.
Confirm release bytes with `GET /api/v1/openapi.yaml` and worker readiness with
`GET /api/v1/worker`. Replay each already-stored original through the reviewer's
`POST /api/reviews/{id}/retry` with `sourceMode=saved_snapshot` and `submit=false`.
Use the matching boot components for both app-only images. Capture session evidence
before stop. Compare each 2048 board transition against the requested direction
and evaluate the PCM against the frequency of the mounted MP3 fixture.

## Saved-original dry-runs

All three replays used the actual reviewer and dedicated native worker, ran for at least 60 seconds, kept the original application bytes, produced valid ZIPs and released the guests, mutable Flash and leases. Retry used `sourceMode=saved_snapshot`, and no Burner submission was requested or sent. Package SHA-256, runtime identity, ZIP hashes and input/output details are in the [original-firmware replay summary](evidence/original-replay-summary.json).

| Original firmware | Observed behavior |
| --- | --- |
| Cardputer ADV MP3 Player v1.0.0 | The library listed `TEST.MP3` on the FAT32 fixture. Enter showed the playback state, and the emulated sink captured 1,372,672 bytes of PCM. Seven sample windows matched the 524 Hz fixture. |
| Core2 2048 Game 1.0 | App-only intake used the pinned matching boot configuration. Eight drags, two per direction, produced legal 2048 moves and a valid tile spawn in decoded guest frames. |
| EMBER 2.1 | App-only intake used three pinned bootstrap segments and the exact original app at `0x10000`. The guest booted, drew frames and responded to Enter with the recorded FAT32 fixture. |

These were native virtual-device runs. Physical hardware, RF, electrical behavior, acoustics and browser-WASM guest execution of this release were not run. `SIM_VERIFIED` covers the tested functions. The static security stage remains `REVIEW` and malware scanning was `NOT RUN`.

The official Tab5 candidate produced a frame with a DSI control fixture. Three original BINs remained without a valid frame, so resident Tab5 retained its current backend. [Tab5 controls and limits](../2026-11-17-paperdiy-sta-and-tab5/report.md)
