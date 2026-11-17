# Native open SoftAP data-plane validation

The earlier native run showed station association while DHCP and HTTP remained open. This follow-up uses a purpose-built ESP-IDF 5.5.4 application on Cardputer and Cardputer ADV. The Device Service registers one same-session peer through a Unix socketpair. Guest DHCP and ARP run before the client requests one compiled application response over TCP. The HTTP body and request digests match across both generations. The evidence is from native QEMU virtual-device execution. [Prior association record](../2026-11-17-native-softap-tab5-touch/report.md) · [Pinned ESP-IDF source](https://github.com/espressif/esp-idf/tree/735507283d5b2f9fb363a1901172dbd9e847945d)

## Observed behavior

| Probe | Observation |
| --- | --- |
| Cardputer ADV and same-session reset | Peer generations 1 and 2 reached DHCP, ARP and HTTP. Finalized pcap recorded two completed DHCPv4 DORAs and two bidirectional TCP payload flows. UART included fixture-ready, joined, leased and HTTP-sent markers. |
| Two concurrent leases | Cardputer and Cardputer ADV each recorded one DORA and one bidirectional TCP flow. The peers reported release and the service finished with zero leases. |
| Rejection and lifecycle controls | Denied ACL returned 403. The previous engine returned 503 before launch. A custom routing request was rejected. Graceful shutdown released the guest. Restart after interruption reconciled the incomplete lease and released the old process. |
| Separate STA regression | Open and correct WPA2 cases each reached DHCP and fixture HTTP. The wrong-credential case had no association, DHCP lease or HTTP exchange. |
| Separate PaperDIY regression | The SD fixture detected the card, mounted, wrote and read after remount. The uploaded source image remained unchanged. |

The archive holds the exact 17,929-byte bounded summary from the integrated source. Its SHA-256 is 238a8dd2a00633caef1945aaa2f537688759c45dd91eb50d4eae5d56c61bd1b2. QEMU, firmware, ROM, fixed exchange and capture identities are in that summary. The same-session peer result provides the controller-side observation and the finalized Ethernet capture provides independent transport evidence. [Integrated source summary](evidence/native-open-softap-summary.json)

## Reproduction

Build the standard fixture under tests/network/native_open_softap with ESP-IDF 5.5.4 pinned in the summary. Use the 8 MiB merged ESP32-S3 image and the listed native QEMU build. Start a dedicated Device Service, upload the image, then create a session for Cardputer or Cardputer ADV with runtime qemu-wifi, network.profile cardputer-open-softap-fixture and ready marker AP_FIXTURE_HTTP_READY. Read the joined, leased and HTTP-sent UART markers and verify the session peer response. Reset on the same session, repeat the exchange, collect the ZIP before stop, then confirm finalized Ethernet DORA/TCP counts and release. Repeat in two independent concurrent leases with the same image. Use the prior QEMU build and a denied runtime ACL as negative admission controls.

The tested scope is one fixed open access point and one reference application. It leaves original captive-portal firmware, encrypted guest APs, Linux-worker behavior, browser-WASM and physical RF open. No firmware images, raw packet captures, internal topology or production claims are included in this record.

## Combined runtime follow-up

Source 6da7ab20351d732c6738fe13311f686efc856db3 with native QEMU SHA-256 5f8a5f38f0512db04a36fb7ca5cf13ec3d359d0fff1eb481fe9b2c06ab3580f2 repeated the exact ADV fixture firmware 25eaf5347edbb7a8e8139830c4e2bf4cd696c0964f30cf969e4a2c52aede9ee2. Generations 1 and 2 both reached DHCP, ARP, and fixed HTTP; the finalized capture again recorded two completed DORAs and two bidirectional TCP flows. Both receipts have the same fixed request and response digests. Peer and lease release were observed. The repeat used one ADV session and does not requalify the concurrent, STA, authorization or restart controls on this combined executable. [Combined ADV reset evidence](evidence/combined-adv-reset-summary.json)
