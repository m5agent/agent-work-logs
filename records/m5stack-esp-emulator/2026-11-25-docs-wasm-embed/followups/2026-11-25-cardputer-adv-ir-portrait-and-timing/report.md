# Cardputer-ADV IR NEC browser investigation

The goal was to distinguish three user-visible behaviors in the original Arduino example: readable orientation, guest USB messages, and NEC frame timing. The same original sketch and firmware were used throughout. [Issue #258](https://github.com/m5agent/m5stack-esp-emulator/issues/258) · [Official example](https://docs.m5stack.com/en/arduino/m5cardputer/ir_nec)

## Signed portrait

The guest calls `setRotation(1)`. The Cardputer-ADV M5GFX panel adds its one-quarter-turn offset and sends ST7789 MADCTL `0xd4`. With the physical glass mount, this guest orientation requires `+90°` in the 3D viewer. The locked `0044` browser only knew that the axes were exchanged, so its fixed `−90°` choice inverted the text. The candidate C panel reports the signed direction from MADCTL and the mount. The browser uses that angle for the 3D viewer and the corresponding rotation and coordinate transform for the flat canvas. The physical framebuffer remains 240 × 135.

With the exact same uploaded firmware, the locked runtime had an upside-down 135 × 240 flat preview and the candidate had an upright 135 × 240 preview. Both screenshots still show text clipped at the short edges. The original sketch draws centered text wider than the portrait canvas. This record covers the IR display rotation and does not qualify a separately edited landscape sketch. [Before and after screenshot hashes and observations](evidence/ir-virtual-device-summary.json)

## USB and timing

In each execution the actual guest emitted the first two commands `0x34` and `0x35` for address `0x1111`. The simulated ESP32-S3 USB Serial/JTAG controller reported 435 emitted bytes. Packetization varied among runs. It used the same console epoch as the frame and guest receipt. In every case the public Stop control led to QEMU exit 0, engine iframe removal and all six observed workers closing.

The candidate captured the committed LEDC duty transitions routed through the GPIO44 output matrix. The observer uses the virtual clock, has a fixed 192-edge buffer, and reports the configured carrier and count during each mark. Each A/B capture contains 136 edges and uses 37,987 Hz with 76 active counts in a 256-count PWM period. The decoder checks the leader, every mark and space, the stop mark, the carrier, the address and the command complement. It uses the pinned IRremote NEC unit of 560 µs and a fixed ±25% tolerance in both trials. The expected words contain the extended address `0x1111` and commands `0x34` and `0x35`.

| Measurement | Default virtual clock | Virtual clock ÷8 |
| --- | ---: | ---: |
| Strict decoded NEC frames | 0/2 | 0/2 |
| Virtual full burst times | 82.265 / 83.260 ms | 65.462 / 65.182 ms |
| Intervals outside ±25% of the two expected frames | 32 / 39 | 2 / 1 |
| Median non-leader marks | 705.1 / 720.0 µs | 580.6 / 580.6 µs |
| Longest observed off interval per burst | 7.725 / 9.340 ms | 1.723 / 1.711 ms |
| Host interval between received USB messages | 1.246 s | 8.675 s |

Each nominal 63.280 ms burst includes the leader and stop mark. At ÷8 the three intervals outside tolerance were a short space at 808.746 µs, a mark at 721.253 µs, and a short space at 838.104 µs. The fixed diagnostic 1120 µs short/long midpoint recovered both exact pulse-distance words with valid command complements at ÷8. The strict decoder still rejected the bursts. Under the normal clock the same midpoint misread one bit in the first burst during a 7.725 ms off interval.

The browser runs were consecutive. A runtime compile could consume up to two host jobs during the A/B. The host USB measurements include browser delivery time. SYSTIMER and edge capture use `QEMU_CLOCK_VIRTUAL`. The improvement under ÷8 shows sensitivity to host-scaled execution. The observation does not isolate CPU interpretation, MMIO, guest interrupts or host scheduling. Physical optical output and an external receiver were not tested. [Timing aggregates and remaining outliers](evidence/ir-virtual-device-summary.json)

## Reproduction

1. Use the original sketch and the pinned Arduino dependencies in [run.json](run.json). The tested merged image is 4,194,304 bytes and has SHA-256 `0969326c036e7a88168dcf9dae65de20b71ee501e2ecc1074c86819d10c240fb`. Verify the sketch and image digests before testing. The browser receipt identifies the same image padded with `0xff` to 8 MiB.
2. Use the [runtime recipe at the emulator base commit](https://github.com/m5agent/m5stack-esp-emulator/tree/a5a48eceee172be037fe7c742eeff5f529f778d5/scripts/qemu-wasm-build). The recipe pins [Espressif QEMU `40edccac`](https://github.com/espressif/qemu/commit/40edccac415693c5130f91c01d84176ae6008566), the source lock through `0044`, and Emscripten 3.1.50. Apply `0001` and `0002` to the QEMU sources after those pinned layers. `git apply --check` passed on the derived `0044` sources, and the reverse checks passed on the candidate. The recorded private run recompiled nine affected or header-dependent objects, verified 705 unchanged link inputs against the base, and relinked. A fresh reproduction may instead rebuild the full target. That would yield a separately identified runtime.
3. Apply `0003` to the emulator source at the base commit. Forward and reverse checks passed. The private browser site must use the new C runtime and list `0001` at the exact `patches/qemu-wasm-probe/0045-cardputer-adv-portrait-direction.patch` manifest identity expected by `0003`, with SHA-256 `d95f729f5cae8a38105849a4b434ed0bf7409f16d7951f49310de12da64ab916`. List `0002` under temporary diagnostic identity `patches/qemu-wasm-probe/0090-cardputer-adv-ledc-ir-observation.patch`. Use a private static site with `publication_eligible=false`, the required verified ROM, and a fresh browser context for each run.
4. Select Cardputer-ADV and the browser runtime, choose the merged local file, enter its expected SHA-256 and start. For the candidate divisor test pass `clockDivisor: 8` to `PublicQemuRuntime.start` through its existing opt-in `allowCandidateProfiles` path. Confirm the normal or candidate clock in the runtime receipt, and confirm `M5_WASM_SLOW_CLOCK divisor=8` in the candidate diagnostic. No firmware or C changes are required between these two runs.
5. Observe the 135 × 240 flat preview and the USB Serial/JTAG address and commands. After `0x35`, read only the fixed private `runtime.ask('ir-waveform')` operation from the active browser runtime. Save its JSON and run the same decoder in both cases. Use the public Stop control and verify QEMU exit, iframe removal and the absence of workers from the closed session.

```sh
python3 code/check_ledc_nec.py gpio44-waveform.json --address 0x1111 --commands 0x34 0x35
```

The bounded evidence retains artifact hashes, measured values and cleanup counts. Raw browser IDs, local URLs, serial logs, screenshots and per-edge timestamps are outside this archive. The baseline, private first capture and two clock trials are separate executions.

## Status and rollback

The signed portrait correction can be built independently of the GPIO44 observer. It still needs locked-runtime acceptance using the original IR sketch and the four-rotation keyboard/display regression. The timing case remains `FAIL`. The global ÷8 profile still misses NEC timing and lengthens the demo, so it remains a private experiment. Reverting the candidate C and browser changes restores the original signed-angle fallback and removes the private observer. No persistent device changes were made.
