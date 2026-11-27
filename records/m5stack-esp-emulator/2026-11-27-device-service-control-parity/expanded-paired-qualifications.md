# Expanded paired Device Service qualification

2026-11-27. Virtual-device validation. The runtime pin for the release is
[9c0447e8](https://github.com/m5agent/esp32sim/tree/9c0447e8e38d0bafc2f124e6e8b8cc5994d30eee).
Measurements use an isolated Device Service and QEMU host-image Flash
transport. Candidate defaults described here are source selections.

| Device | Paired Arduino service oracle | Stock and checked-in cases | Consumer scope | Candidate ordinary default |
| --- | --- | --- | --- | --- |
| Atom Lite | 4 PASS per runtime, each twice | Original Flash UART REPL, board 128, GPIO39 and LED 0x204060, 2 PASS per runtime | Common HTTP/evidence, 2 PASS per runtime | esp32sim |
| Atom Matrix | 4 PASS per runtime, each twice | Original Flash UART REPL, board 141, GPIO39 and 25 LEDs, 2 PASS per runtime | Common HTTP/evidence, 2 PASS per runtime | esp32sim |
| Atom Matrix v1.1 | 4 PASS per runtime, each twice | Original Flash UART REPL, board 141, GPIO39 and 25 LEDs, 2 PASS per runtime | Common HTTP/evidence, 2 PASS per runtime | esp32sim |
| Cardputer K132 | Selected display cases passed the paired display predicates | Original stock v2.5.4 offline page to app menu, 2 PASS per runtime | Common HTTP/evidence, 2 PASS per runtime. Saved SPI SD reviewer job reaches SIM_VERIFIED on both | esp32sim |
| Dial | Selected display and encoder cases exercised. The latest encoder both-runtime run passed paired input and display checks | Original stock encoder changes the guest menu frame in both trials per runtime | Common HTTP/evidence, 2 PASS per runtime. Saved encoder reviewer job reaches SIM_VERIFIED on both | esp32sim |
| Core2 | Selected display examples exercised | Complete original Home, touch response, and same-base UART REPL A/B/C transitions, 2 PASS per runtime | Common HTTP/evidence, 2 PASS per runtime | esp32sim |

The classic Atom Arduino service suite includes both GPIO pulses, two distinct
sensor samples or the Lite no-IMU control, three routed WS2812 colors and the
UART loop markers. IR waveform verification uses the standalone fork suite.
The stock REPL tests verify the guest board and original drivers through the
lease console. A missing original launcher module is tracked independently.

The stock timing from request to the observed MicroPython marker was 1.313–1.526 s
on esp32sim versus 8.412–8.416 s on QEMU for Atom Lite, 1.499–1.661 s versus
6.185–6.853 s for Matrix, and 1.379–1.616 s versus 6.159–8.912 s for Matrix v1.1.
Each side used two cold guest leases.

For Cardputer, wait for the orange offline banner and fully rendered Nickname
row, then press F12 for 450 ms on the modeled GPIO0. The guest shows the blue
Develop tile after input. The earlier QEMU input arrived during rendering and
its failure receipts are retained. Dial stock and Cardputer stock observations
cover display and modeled input. Stock USB-REPL was not exercised on those
two original images. The separate reviewer jobs retain their established
runtime unless the opt-in per-job flag is enabled.

The Core2 timing starts at the lease request and requires five complete menu
tiles and the fully drawn QR panel. esp32sim observed that Home at 4.178 and
4.184 s. QEMU observed it at 43.196 and 48.839 s in this run. An earlier
color-count-only check could count the boot splash and is superseded for Home
timing. Both runtimes received the same (34, 48) touch. The menu region changed.
The same pinned base with the checked UART bootstrap recorded A, B and C
press/release separately on both runtimes. Earlier QEMU runs missed C when
the harness used fixed host sleeps and a shorter guest polling loop.

## Tab5 comparison

On the previous merged parity pin, first qualifying frame took 9.101 and
9.260 s. On the runtime-gaps pin it took 9.554 and 9.968 s. The same two RGB
hashes appeared across the runs in different order. A qualifying frame has
at least eight colors and 10,000 lit pixels. Each isolated service had one
lease at a time. The host load and the guest cycle sampled after the frame
are recorded separately. This is a wall-clock observation and retains the
fork's independent exact guest-time and instruction-count comparison.

- [Classic Atom docs](evidence/expanded-classic-docs.json) · [Classic Atom stock](evidence/expanded-classic-stock.json) · [Classic Atom endpoints](evidence/expanded-classic-http.json)
- [Cardputer stock](evidence/expanded-cardputer-stock.json) · [Dial stock](evidence/expanded-dial-stock.json) · [Cardputer, Dial and Core2 endpoints](evidence/expanded-cardputer-dial-core2-http.json)
- [Core2 exact Home and REPL](evidence/expanded-core2-complete-stock.json) · [Tab5 timings](evidence/expanded-tab5-wall-comparison.json) · [CoreS3 sensor observations](evidence/expanded-cores3-sensors.json)
