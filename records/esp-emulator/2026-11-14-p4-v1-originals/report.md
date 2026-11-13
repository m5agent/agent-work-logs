# Original Tab5 regression report

## Purpose and hypotheses

The prior Tab5 investigations separated normal service image integrity from
upstream P4 emulation gaps. The older backend reached a DSI PHY wait for
UIFlow2 and a DWC identity assertion for Maker Fighter; rc2 already exposed
an older-P4 interrupt CSR fault. A newly published stable executable required
an actual same-image trial before deciding whether those blockers remained.

The alternatives were a corrected stable backend, an unchanged backend gap,
or an invalid comparison caused by image mutation, mismatched symbols or an
incomplete companion process. The last alternative was checked independently
against uploaded bytes, actual runtime process roles, sampled session identity
and the evidence archive.

## Fixed inputs

Source is `a5990e720a8c79310456bf5868141f4cfd50afe8`. The runtime is the official
macOS esp-emu v1.0.0 executable, SHA-256
`cdfe1e8f3d447af4af12f0699457e958af0ea6ff8601d909079801c8655c6ef5`.
The archive digest, published sums and strict platform signature were checked.
The re-downloaded rc2 executable matched the previously tested binary,
`fc07ca633a7451cc8038b3cd24540ee811a1a4cc159042930705038f53dfdb08`.
Identical public tag trees do not prove binary equivalence: the public source
does not contain the emulator core.

Both trials use P4 rev0 ROM
`948f2c7d108d04a9c3a982f9c1c498fb17f2c4a68abc51f87782592034d7ce44`,
revision-compatible eFuse seed
`0f8266520c4264b2ba898f3645e3f6f701e9304968c5a51307fe4baf6fc03f1e`
and C6 adapter firmware
`38669a215f8b290ec53bbbaeda154a77c8ab276c5deeb6beb85248e95986d554`.
These are configuration artifact hashes, not claims about physical silicon.

Original UIFlow2 V2.5.4 is
`94b6b43c02a95cfac1e7c70a6166ad669f308d0d16389c272de5ca7c2d45ef37`;
original Maker Fighter 1.4 is
`d96962362b262bcc4e5abcf6a720a2de1a53f0869c87916fd3f798eb845e08b6`.
Only trailing erased Flash padding was added. The separate normalized-image
and application-partition hashes are in the execution summaries. No unrelated
reference ELF was supplied to either original firmware.

## Execution and observations

The isolated service uses the frozen production implementation. Its only
DeviceSpec overrides select the verified executable for `emulator` and
`flash_emulator`; controller behavior, firmware bytes, guest return values and
watchdogs are unchanged. Both actual child command lines identified the same
verified binary and the expected `esp32p4` / `esp32c6` roles. Each role was
bound to its original process start identity and checked throughout the run.

UIFlow2 was observed for 120.909 seconds with 116 session samples. Its serial
contains 133 occurrences of MEPC `0x4ff0255c`, MTVAL `0x34602773`, 134 ROM boots
and 266 panic markers. The marker count is a text-occurrence count, not 266
independent crashes. No MicroPython banner was observed.

Maker Fighter was observed for 60.516 seconds with 58 samples. Its serial
contains 79 occurrences of MEPC `0x4ff01d82`, the same fault instruction,
80 ROM boots and 158 panic markers. The former DWC/GSNPSID assertion was absent
because execution failed earlier. USB initialization, enumeration and endpoint
transfers therefore remain unverified; the prior USB failure is retained.

`0x34602773` reads CSR `0x346`, the older P4 `mintstatus` address defined by
[fixed ESP-IDF v5.5.5 source](https://github.com/espressif/esp-idf/blob/v5.5.5/components/riscv/include/esp_private/interrupt_clic.h).
This observation is consistent with the previously identified revision-aware
CLIC gap. No instruction replacement or fabricated ready value was introduced.

After each uninterrupted observation window, one read-only GDB snapshot was
taken. These snapshots occurred at arbitrary points in repeated boot loops,
not at stopped faults. Their word at the old probe address did not match the
fault instruction; their zero DSI registers do not prove a PHY defect or fix.
The independent audit explicitly retains this limitation. Production frame
requests returned unavailable without matching symbols; there is no UI/touch
readiness claim.

Each evidence ZIP was requested before stopping with history retained. All
four manifest entries passed size/hash checks. The ZIP serial exactly matched
the separately saved final serial, and the complete application partitions
matched the uploaded originals. Both original runtime roles, Flash ownership,
lease and dedicated service were verified cleaned up. No resident service
was changed.

## Reproduction

1. Check out the fixed source and obtain the original images and backend assets
   matching the hashes above. Use a dedicated Device Service state directory and
   an unused endpoint. Configure only the two Tab5 executable fields to the
   verified stable binary; preserve the revision ROM, eFuse and C6 inputs.
2. Upload each BIN through `POST /api/v1/artifacts`, import for `device_id=tab5`
   through `POST /api/v1/firmware/import`, and create a `runtime=qemu` session
   with the returned firmware identity and a unique idempotency value.
3. Require exactly one P4 and one C6 child of that service, the expected binary
   hash, and the P4 process matching the session receipt. Observe the original
   roles for 120 seconds / 60 seconds, sampling session state each second.
   `running` alone is not an application readiness result.
4. Read serial and preserve evidence before stop. Do not attach a stale ELF.
   Compare each application partition in the Flash evidence against the original
   BIN, allowing only erased padding outside the original length. Verify ZIP
   manifest entries, then stop with `purge=0` and check both roles, Flash, lease
   and service cleanup.
5. Recompute the bounded serial results with
   `python3 code/analyze_serial.py SERIAL_LOG --issue 188` (or `226`). This
   archived function is the executed trial's serial oracle. It was rerun on
   both actual logs and all ten output fields matched their execution summaries.

The preparation controls also checked changed source/assets, occupied endpoint,
missing execution authorization, incomplete/changed process roles and cleanup
identity. An initial idle-service endpoint check incorrectly rejected TCP
TIME_WAIT; that host-only failure was retained and the probe corrected to match
the HTTP server's address reuse behavior while still rejecting a live listener.
Neither preparation check started a guest. They do not replace the two trials.

## Remaining work

Both applications remain FAIL on this exact stable backend. The service layer
can report and preserve those failures but cannot repair a closed emulator core.
The next upstream backend needs revision-correct CSR behavior, followed by the
existing DSI and USB controller requirements. A future result must repeat the
same original images and validate the actual application and data paths.

The [stable release](https://github.com/espressif/esp-emulator/releases/tag/v1.0.0)
describes P4 USB device mode with a virtual host; that is not guest USB-host root
port and endpoint support. This trial establishes neither USB path. There was
no code deployment to roll back, no physical-hardware measurement and no Burner
submission.
