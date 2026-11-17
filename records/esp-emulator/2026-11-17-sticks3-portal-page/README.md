# StickS3 original setup page in the native virtual device

- Date `2026-11-17`
- Result `PASS` for the first-boot setup page read
- Kind `code_change`
- Source `m5stack-esp-emulator@d627ac203218e64387355b3ea541809b4bad3157` and StickS3-Claude-Codex-Assistant v0.2.4
- Environment StickS3 virtual device, native Xtensa and a dedicated Device Service lease with one private UNIX socketpair
- Issue or pull request not applicable. This check addresses the firmware review data-plane backlog.

The original release booted its setup screen and advertised `StickS3-Setup`. The peer joined, obtained a DHCP lease, resolved the guest via ARP and read the setup page over HTTP in that same virtual device. Independent reconstruction from Ethernet capture verified one GET, HTTP 200, a 5,448-byte response and the setup heading and Wi-Fi form. The guest refused the first connection while HTTP was starting, then answered the fresh connection. [Author release](https://github.com/bulb888/StickS3-Claude-Codex-Assistant/releases/tag/v0.2.4)

The guest binary, QEMU, capture, frame, ZIP and readback identities are in the [derived evidence summary](evidence/portal-session-summary.json). The [full report](report.md) gives the reproduction and negative controls. The [machine-readable record](run.json) records acceptance by layer.

Credential submission, transition of the original firmware to STA, browser-WASM and physical RF are `NOT RUN`.

[组合版本原生复验](evidence/combined-native-summary.json)
