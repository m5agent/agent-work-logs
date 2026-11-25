# Cardputer-ADV NEC timing under a private deterministic accelerator

The original IR example had failed strict GPIO44 envelope checks under both the default virtual clock and an explicit divider of 8. This follow-up used the same incremental diagnostic WASM, source ROM and strict decoder with an existing QEMU deterministic accelerator configuration. It tested the exact original portrait firmware and the separate official landscape binary. [Issue #258](https://github.com/m5agent/m5stack-esp-emulator/issues/258)

## Runtime and unchanged inputs

The candidate static browser site is private with `publication_eligible=false`. Its manifest SHA-256 is `6d9b1069a4fb3080e5927c5bf8ce2f13b09eb40980d628c0a7d5778afd32f437`. The compiled diagnostic WASM SHA-256 remains `3cde0df151570bad4670525d2ad453fb8adbd332fad2f23bb5a602bb0f59bb29` and its runtime manifest SHA-256 remains `ddedb331fe64f094a85fc2e17537054dda382bdb0419077a6389d0698b9d37a9`. The copied Cardputer-ADV registry row selected the existing `tcg-icount` accelerator with `thread: single`, `tbSizeMb: 128`, `icountShift: 5`, and normal virtual clock divisor `1`. The conflicting Cardputer-ADV one-instruction workbench variant was removed from this copy of the registry. The browser receipt recorded the intended arguments for both guests.

```text
-accel tcg,thread=single,tb-size=128 -icount shift=5,align=off,sleep=off
```

The original 4 MiB BIN has SHA-256 `0969326c036e7a88168dcf9dae65de20b71ee501e2ecc1074c86819d10c240fb`. The separately built landscape example has SHA-256 `ae81222c68c2e24eb3809bdb0a656763acd64cc764fccf68351945a5d7e2afdb`. The same identified image is used within each run from upload through receipt, frame, waveform and cleanup. Both images retain the same command pair. [Firmware, runtime and controller receipt hashes](evidence/ir-icount.summary.json)

## Virtual-device results

| Run | Strict NEC frames | Virtual burst lengths | Host USB markers from runtime start |
| --- | ---: | ---: | ---: |
| Original, normal virtual clock | 0/2 | 82.265 / 83.260 ms | 2.563 / 3.809 s |
| Original, virtual clock ÷8 | 0/2 | 65.462 / 65.182 ms | 4.407 / 13.082 s |
| Original, single-thread icount | 2/2 | 66.822 / 66.780 ms | 8.422 / 10.765 s |
| Official landscape, single-thread icount | 2/2 | 66.696 / 66.903 ms | 8.388 / 10.754 s |

Both icount runs captured 136 edges in the fixed GPIO44 LEDC observation, with virtual timestamps and a configured 37,987 Hz carrier at 76/256 duty. The same unchanged decoder and ±25% tolerance accepted both full frames, at edge indices 0 and 68, with address `0x1111` and commands `0x34` and `0x35`. USB Serial/JTAG returned the same address and commands, and the real controller counted 435 transmitted bytes in 24 packets in each trial. The nominal frame burst is 63.280 ms.

The original firmware showed its upright +90° portrait view with the source text still clipped. The landscape firmware showed the 240 × 135 view at 0°. Its exact screenshot digest matched the previously observed landscape presentation. Both outputs came from the guest framebuffer. The test required one public Start action per new session. Start-to-runtime-ready was 257 ms for the original and 348 ms for landscape. Landscape observation and shutdown completed in 14.922 s. The normal-clock guest emitted its first marker earlier. These wall-clock observations include browser delivery and possible concurrent build load and are scoped to the local test runs. [Timing, source and screenshot digests](evidence/ir-icount.summary.json)

## Cleanup and preserved runner result

Each QEMU guest exited with code 0 and reported no remaining pthreads after the normal Stop action. The actual worker topology had four pthreads and one engine. The browser observed all five targets close and zero remain, and both engine iframes were removed. The first runner kept its earlier fixed six-target minimum and recorded `FAIL` when the independent browser already showed no workers. Its raw failure remains recorded. The second run bound the closure count to the observed independent topology and checked it against the QEMU count before passing.

## Reproduction

1. Use the exact prior private QEMU diagnostic build with signed portrait and the fixed GPIO44 LEDC capture. The required archived C patch SHA-256 values are `d95f729f5cae8a38105849a4b434ed0bf7409f16d7951f49310de12da64ab916` for signed portrait and `2406ef2676a9e78d8f9092ed5b78bcc88d4559f432632f679b912dcae47d6395` for the GPIO44 observation. Verify the WASM and runtime manifest before selecting a different clock profile.
2. Make a separate local non-public copy of the site. Change only the private Cardputer-ADV profile and private admission configuration as described above. Rehash the site files and reject any change to the runtime or authorized firmware. The exact verified ROM hash is in the evidence summary.
3. For each image start a fresh browser, select Cardputer-ADV and browser mode, upload the local file and check the reported firmware input and runtime hashes. Verify the effective `-accel` and `-icount` arguments. After USB command `0x35`, read the fixed `runtime.ask('ir-waveform')` diagnostic from the same guest. Run the unchanged decoder below against the captured JSON.
4. Stop each guest using the normal UI, then compare independent browser worker closure against QEMU's created-pthread count plus one engine. Preserve timing and cleanup as separate observations.

```sh
python3 code/check_ledc_nec.py gpio44-waveform.json --address 0x1111 --commands 0x34 0x35
```

## Validation boundary

This is a private exact-firmware workaround for the virtual controller timing. Production `0049` timing and standard profile admission with icount are `NOT RUN`. Wider firmware compatibility and performance remain open. Physical optical output, receiver decode and electrical timing are untested. The standard Cardputer-ADV profile remains outside this change.
