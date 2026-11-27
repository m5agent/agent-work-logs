# Repeated SX1262 UDP loopback comparison

Native virtual-device validation compared the pinned C6-A parent `ef799a13` and LX6-B candidate `9ac09fb7`. Each of ten rounds ran four paired cases on each build. A Nesso isolated control ran alongside each build block. PaperMono's tracked runner also ran its disconnected control. Each block completed before the next, and alternate rounds reversed the build order. The runtime, ROM, firmware and runner hashes were verified before and after the series.

| Pair | ef799a13 RX by trial 01–10 | 9ac09fb7 RX by trial 01–10 | Oracle failures, parent / LX6-B |
| --- | --- | --- | --- |
| Nesso N1 | 14, 14, 14, 14, 14, 14, 14, 14, 14, 14 | 14, 14, 14, 14, 14, 14, 14, 14, 14, 14 | 0/10 and 0/10 |
| PaperMono | 1, 2, 2, 4, 2, 3, 2, 3, 1, 2 | 2, 2, 3, 2, 3, 3, 3, 2, 3, 3 | 2/10 and 0/10 |
| ADV CAP lora1262 | 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 | 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 | 0/10 and 0/10 |
| ADV CAP lora868 | 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 | 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 | 0/10 and 0/10 |
| Nesso N1 isolated | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 0/10 and 0/10 |

Nesso sent 14 packets per trial. Each ADV CAP variant sent and received its one `wasm` payload per trial. PaperMono sent four packets in every trial. The receiver logged only consecutive prefixes starting at packet 1. The parent received 22/40 and failed the two-exact-payload oracle in `r01-ef799a13-papermono` and `r09-ef799a13-papermono`. LX6-B received 26/40 and met the oracle in ten of ten repeat trials, with at least one packet missing in each. All 20 Nesso isolated and 20 PaperMono disconnected receivers accepted zero packets.

The initial cumulative LX6-B gate had two additional failures. Capture `full-gate-9ac09fb7-nesso-initial` saw 13 of 14 packets and missed the initial unnumbered payload. Capture `full-gate-9ac09fb7-papermono-initial` saw one of four. Exact-binary targeted retries saw 14 and three respectively. These historical failures and retries are additional to the ten repeated trials per pair and build.

## Timing controls and source comparison

When the receiver reported that it was listening before the sender started, Nesso captured the initial unnumbered payload on both builds. When the receiver process launched after the sender's first transmission completed, both missed that payload. Each order captured 13 of 14 on each build. The receiver-first run missed the last numbered packet at the original run limit. These controls used the original firmware and commands.

With PaperMono's original 500 ms listener polling and a 43-second guest horizon, the LX6-B receiver exited at 3.340 seconds of host time after launch. The sender logged packet 4 at 4.294 seconds. The receiver accepted only packet 1. An 80-second receive horizon with the 500 ms polling captured all four packets on both builds. At 25 ms listener polling, both builds captured all four even at 43 guest seconds. These timing controls identify a concrete loss window in the independently scheduled peer run.

The LoRa model, all three board peer implementations, and the original pair runners have the same source across the two builds. Each board polls a nonblocking UDP peer against its own virtual clock. The shared chip accepts a datagram only in RX mode with no unhandled RX_DONE. It cannot accept a datagram after the process has exited. The LX6-B FIFO work is gated to the classic 16-slot controller. The measurements establish a pre-existing host-timing dependency. They show no worsening on LX6-B in the tested acceptance rate or total delivery. The Nesso launch order reproduces the missing-first-packet symptom on both builds. The original Nesso gate capture does not identify the exact instant the receiver entered RX. [Shared SX1262 receiver](https://github.com/m5agent/esp32sim/blob/9ac09fb79cefe4a2cb6f911172ffa6cbdfbd784a/esp-soc/src/devices/sx1262.rs#L131-L145) · [PaperMono peer loop](https://github.com/m5agent/esp32sim/blob/9ac09fb79cefe4a2cb6f911172ffa6cbdfbd784a/esp32s3/src/board/paper_spi.rs#L112-L131) · [Nesso peer loop](https://github.com/m5agent/esp32sim/blob/9ac09fb79cefe4a2cb6f911172ffa6cbdfbd784a/esp32c6/src/board/nesso_n1.rs#L182-L205)

The separate fix can make receiver-ready state and the common virtual-time receive window explicit, with diagnostics for datagrams rejected before RX, while RX_DONE is pending, and after exit. Raw captures from every trial and each failed gate attempt were retained. Physical RF was NOT RUN.
