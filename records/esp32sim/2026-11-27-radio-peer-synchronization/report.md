# Paired radio timing and validation

## Failure and implementation

PaperMono sent four packets in both ten-trial baseline series. The old peer loops polled UDP on each guest's own clock, so the receiver could reach its guest-time limit before the final sender transmission reached its host socket. Nesso also lost its first payload in a separate startup control. [Baseline counts and timing controls](https://github.com/m5agent/agent-work-logs/blob/5c229671cd38068499b025c1841d8f2d0fa1ea71/records/esp32sim/2026-11-27-lora-loopback-repeat/report.md)

C6's Cooja coordinator already drives both peers with timestamped virtual steps. The new board-radio medium uses a similar common clock without requiring an external coordinator. Both CLI processes rendezvous before boot. At each 1 ms boundary, they exchange completed transmissions and an explicit progress marker over an ordered TCP stream. The receiver schedules each frame at the sender's virtual TX completion plus a fixed 2 ms delivery delay. This lookahead lets both guests advance in bounded slices while preserving the receiver's power, channel, listening and pending-IRQ checks. On normal exit the peer exchanges its final frames before releasing the remaining guest. [Shared radio peer implementation](https://github.com/m5agent/esp32sim/blob/239d2bfa7c5dc91ca36ec82bda4fb2fe6a82ba49/esp-soc/src/devices/radio_peer.rs)

The same transport serves Nesso N1 and PaperMono's SX1262, both Cardputer-ADV SX1262 CAP variants, and its CC1101 CAP. The flags and reciprocal port syntax remain. Host programs that emitted the old raw datagrams need to use the synchronized stream protocol. An isolated process omits the peer option. [CLI compatibility and capture timing](https://github.com/m5agent/esp32sim/blob/239d2bfa7c5dc91ca36ec82bda4fb2fe6a82ba49/docs/cli.md#paired-sx1262-and-cc1101-radios)

## Reproduction

Build the pinned fork revision with `cargo build --release --locked -p esp32sim --bin esp32sim --bin esp32sim-p4`. Stage the fixture files under a caller-supplied directory, using the relative names and SHA-256 values in [run.json](run.json). The [baseline record](https://github.com/m5agent/agent-work-logs/tree/5c229671cd38068499b025c1841d8f2d0fa1ea71/records/esp32sim/2026-11-27-lora-loopback-repeat) identifies the frozen sketch, ROM and UIFlow2 inputs. Use the [fork's ROM fetcher](https://github.com/m5agent/esp32sim/blob/239d2bfa7c5dc91ca36ec82bda4fb2fe6a82ba49/tools/fetch-rom-elfs.sh) for the ROM ELFs.

```sh
export RADIO_FIXTURES="$PWD/fixtures"
python3 code/repeat.py "$FORK" "$BINARY" normal --commit "$COMMIT" \
  --only nesso paper lora1262 lora868 nesso-isolated
python3 code/repeat.py "$FORK" "$BINARY" loaded --commit "$COMMIT" --load 10 \
  --only nesso paper lora1262 lora868 cc1101 nesso-isolated
python3 code/repeat.py "$FORK" "$BINARY" controls --commit "$COMMIT" --rounds 2 \
  --only cc1101 cc1101-isolated lora1262-isolated lora868-isolated
python3 code/late-join.py "$BINARY" late-join "$COMMIT"
```

For the ADV LoRa cases, the USB host loads the exact UIFlow2 examples and the input script types `wasm` before pressing Enter at 8.2 guest seconds. A CDC REPL query reads the received bytes from the callback's variable. The CC1101 RX example adds a serial print at the existing successful CRC branch. The CC1101 sender's CDC script starts 1.8 guest seconds later so the receiver finishes configuring before the first transmit. The first equal-start CC1101 trial received sequence 1 through 6 out of seven sends. A separate observer run closed its CDC window after five packets even though the radio counted seven. Both diagnostic outcomes were retained, and the final CDC observer reads through the last packet.

The C6 runs used the firmware, scripts, timing and reset inputs from the LX6-B integration. The [comparison script](code/check-c6-pairs.py) verifies byte equality for the radio event stream and both guest consoles. The existing checker confirms Thread UDP receipt and isolation, Zigbee binding and blue LED transitions, and Zigbee rejoin after a scheduled reset.

## Results

| Pair | ef799a13 baseline | 9ac09fb7 baseline | Synchronized, without added CPU stress | Synchronized, with CPU stress |
| --- | ---: | ---: | ---: | ---: |
| Nesso N1 lora-1/lora-2 | 14/14 | 14/14 | 14/14 in 10/10 trials | 14/14 in 10/10 trials |
| PaperMono lora-1/lora-2 | 1–4/4 | 2–3/4 | 4/4 in 10/10 trials | 4/4 in 10/10 trials |
| Cardputer-ADV lora1262 | 1/1 | 1/1 | 1/1 in 10/10 trials | 1/1 in 10/10 trials |
| Cardputer-ADV lora868 | 1/1 | 1/1 | 1/1 in 10/10 trials | 1/1 in 10/10 trials |
| Cardputer-ADV CC1101 | NOT RUN in repeat baseline | NOT RUN in repeat baseline | 7/7 in 2/2 confirmed trials | 7/7 in 10/10 trials |

Each LoRa lane produced one ordered-payload SHA-256 across both conditions. Nesso and PaperMono's isolated receivers stayed at zero in every round. Both ADV LoRa variants and CC1101 also received zero in their two dedicated isolated runs. Starting the Nesso sender one host second ahead of the receiver still yielded all 14 payloads. Remaining regression jobs shared the host during the first rounds without added CPU stress. The stress phase used ten continuous CPU workers. [Trial counts and hashes](evidence/trials-summary.json) · [Controls](evidence/controls-summary.json) · [CPU sample](evidence/load-summary.txt)

The workspace passed 2,040 tests. Native and WASM Clippy returned zero with warnings denied. Four sentinels preserved instruction counts and serial output against the milestone build. CoreS3 passed 15/15 and Cardputer-ADV passed 11/11. Tab5 passed all 25 runnable cases, with one existing speaker docs defect and two NOT RUN entries for missing example sketches. [Regression receipt](evidence/regression-summary.json)

Two candidate Cooja runs and the LX6-B baseline emitted byte-identical traces and serial logs for the four checked C6 cases. Thread delivered its IPv6 UDP payloads and the isolated receiver did not join or receive them. Zigbee bound the LED device and toggled it, and the recovery case rejoined after a scheduled reset. [C6 replay receipt](evidence/c6-summary.json)

The record qualifies native virtual-device packet delivery with these images and deterministic inputs. Physical RF and paired browser execution were NOT RUN. The new peer protocol requires both processes to use the same revision. To roll back to raw UDP hosts, run both peers on the baseline revision.
