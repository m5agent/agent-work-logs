# Merged rollout and consumer readback

2026-11-27. Virtual-device validation and service deployment.

[PR #287](https://github.com/m5agent/m5stack-esp-emulator/pull/287) merged as
`581073040c202821f54a4a00fd2823d6fd8fa520`. Its branch head was
`1e7822c44a5a52abb9cef1283b5f83e262f18da2`. Both CI checks passed and no
review threads remained open. The full Python 3.12 suite ran 2,588 tests
with 11 skips. All four validators, scope validation and whitespace checks passed.

The rollout was built from merged main, including the browser lane from
PR #286. The primary service and gateway changed over at
`2026-11-27T10:58:42Z`. The reviewer Device Service changed over at
`2026-11-27T10:58:53Z`. The same 36 catalog devices were visible on both.
The reviewer kept its explicit QEMU and network selection. Its review
queue and device leases were idle before the worker restart. The original
ports, state directories and Tab5 overrides were preserved.

The merged rollout's isolated workbench passed AtomS3 Lite, StickC and
NanoC6 guest checks, with one Worker before Stop and zero after Stop.
Both native-only factory flows passed their boot markers with runtime
omitted. StickC and StickC Plus retained all four terminal power-off
receipts and frames. Two Nesso pair retests received the same sequence
0 through 9 and stopped both sessions. The live reviewer dry-run cloned
the existing StickC Plus2 saved input and completed `SIM_VERIFIED`
with retained evidence. The job did not submit to Burner.

## Reviewer fixture outcomes

| Check | Outcome |
| --- | --- |
| Dial encoder | SIM_VERIFIED. Three real modeled detents. |
| Cardputer SD read | SIM_VERIFIED. Completed host fixture blocks observed through the guest controller. |
| PaperS3 SD write | SIM_PARTIAL. Write-stamp path exercised. The application write assertion remained unconfirmed. |
| Tab5 CarPlay frames | Frames and input evidence retained. Outer result SIM_PARTIAL for unresolved interaction assertions. |
| Tab5 crash diagnostics | The same review completed the diagnostics read with `no_evidence`. Positive fault injection was not run here. |
| Tab5 UserDemo V0.4 playback | Legacy baseline and merged standalone both SIM_VERIFIED. The merged run concurrent with SD missed the bounded PCM window. |
| Core2 STA | SIM_VERIFIED. The isolated review-sta fixture observed association and the DHCP lease assertion. |
| StickS3 provisioning | The admitted sequence passed the portal-to-station transition. Additional checks left the outer review SIM_PARTIAL. |
| CoreS3 Joystick Unit | SIM_VERIFIED. The guest observed the configured Unit I²C response. |

The official [Tab5 UserDemo V0.4 release](https://github.com/m5stack/M5Tab5-UserDemo/releases/tag/V0.4)
was SHA-verified. Both successful speaker runs verified the same visual
tap transitions and 192,000 bytes of post-action playback. The native
QEMU/esp-emu assets stayed at their pinned binaries.

## PaperColor timing follow-up

The first Arduino `display` comparison saw six colors on two QEMU
trials and only the initial white palette on two esp32sim trials within
16 seconds. In two matched extended trials each, both runtimes reached six
colors. Relative to the first frame sample, QEMU reached the palette at
approximately 2.02 seconds and esp32sim at 16.86–16.90 seconds, sampled
every two seconds. The board-side follow-up is to compare the initial white
refresh, the long busy/refresh phase and the second packed-palette refresh
timing on the same firmware. PaperColor keeps its QEMU default pending
complete comparison. Original bounded-window results are retained.

## Rollback

The release directory holds a primary rollback command that also restores
the LAN gateway's original browser site. The reviewer rollback command
restores its backed-up launcher and restarts only its Device Service
launch agent. Both prior release environments and their assets were retained.

[Exact qualification hashes and evidence](evidence/qualification.json) ·
[Per-device API readback](evidence/device-api-compatibility.json) ·
[Arduino case inventory](case-inventory.md)
