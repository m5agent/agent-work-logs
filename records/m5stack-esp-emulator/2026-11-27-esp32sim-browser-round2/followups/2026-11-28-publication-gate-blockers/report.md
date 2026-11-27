# Browser release gate and live readback

PR #290 merged at `f08414ded16e1a38c88f14eea59456256fe1c332`. PR #292 merged at `3ec64361ca9094fff773f32614e5ed13e8fe54a2` and measures StackChan input from the observed QEMU controller down edge. The patched gate passed StackChan, Cardputer and every remaining editor/control case in the independent local serial run.

The browser runtime is fork `c2329ebeb1f0a258eedecbab0dac7390aa31987f` with SHA-256 `e9c99a3addf8f57a9c62ed59a89fba932061e1a272ac267c5bebf62101b6991d`. It incorporates the newer native runtime-gaps milestone and the browser branch's board, PSRAM and media changes. Chrome device evidence and same-firmware engine comparisons already passed before publication. Six tested defaults select esp32sim. The exact release gate below remains open.

| Attempt | Result | Observation |
| --- | --- | --- |
| [Actions 46011129495](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/46011129495) | FAIL | Pinned older QEMU artifact producer had a different static exporter input. |
| [Actions 46011319479](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/46011319479) | FAIL | Hosted StackChan zone 2 guest down was absent after a 238 ms controller pulse. Corrected probe validated in two repeats and the local serial gate. |
| [Actions 46022104370](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/46022104370) | FAIL | Cardputer QEMU-WASM guest panic on second boot after hardware reset. |
| [Actions 46027701442](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/46027701442) | FAIL | Cardputer K132 original UIFlow2 launcher did not redraw in the prescribed F12 observation window. |
| Local prepared candidate | FAIL | 52 PASS, 1 FAIL and 19 NOT RUN. CoreS3's QEMU wall-clock fixture hit Core 1 LoadStorePIFAddrError, then reported display dimensions 0 × 0. |

The CoreS3 failure occurred at PC 0x4038ab44 with EXCVADDR 0x60023070. The device-ready assertion rejected the frame before input acceptance. Two isolated runs of the exact CoreS3 fixture on this export passed 34 checks each and reported 320 × 240. Two independent K132 stock runs also produced the expected F12 redraw and zero Workers after Stop. The original failure stays in the gate receipt even when a separate replay passes. An individual guest replay does not authorize publishing a failed full export.

The previous registered Pages artifact `pages-20261127-dd6265db` still serves manifest `38cf12dcfdb8d9cdc3ecab92d7fa3cc568cf75a652a9048033031d738cadf1dd`. A new Pages tag and live checks against this candidate remain pending. The official deployment job was skipped on each failed run.

Local Python 3.12 ran 2,592 tests with 11 skips, Node contracts passed and merged CI passed. Runtime coverage, peripheral catalog, QEMU profiles, project snapshot and PR scope passed. Source cleanup required recreating the checkout and all eight uploaded guest fixtures. Those fixtures rebuilt to their original recorded SHA-256 values. The earlier worktree removal discarded raw historical screenshots and full serial captures. Public summaries and recovered current evidence remain available.

[Full board-by-board admissions, defaults and remaining limits](../2026-11-27-runtime-gaps-and-pages/report.md) · [StackChan failed pulse and corrected replays](../2026-11-27-pages-stackchan-controller-hold/)
