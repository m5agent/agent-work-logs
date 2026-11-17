# Isolated native ESP32-S3 open SoftAP fixture

Date 2026-11-17. Result PARTIAL overall. The fixed open-AP data plane passed on Cardputer and Cardputer ADV in isolated native Device Service sessions. A same-session reset produced a second independently checked DHCP and HTTP exchange. The application under test was a purpose-built ESP-IDF fixture. The earlier SoftAP association test remains part of the historical record. [Prior association record](../2026-11-17-native-softap-tab5-touch/README.md)

- [Scope, proof and reproduction](report.md)
- [Structured run](run.json)
- [Bounded integrated source summary](evidence/native-open-softap-summary.json)

Original firmware portals, encrypted APs, RF, browser-WASM and Linux workers were outside the tested fixture. No Burner submission occurred.

A combined native runtime separately repeated the Cardputer ADV reset case and confirmed both DHCP and TCP exchanges. [Combined ADV reset evidence](evidence/combined-adv-reset-summary.json)
