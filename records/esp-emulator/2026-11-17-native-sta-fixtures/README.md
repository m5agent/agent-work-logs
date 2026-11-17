# Native STA fixture validation

The initial Cardputer and Cardputer ADV both completed the native STA peer
test. The guest rejected a wrong UDP payload even though it received a UDP
response. A separate ADV SoftAP control reached application startup and DHCP
server startup, but the emulated peer did not complete Wi-Fi authentication.

- [Report and reproduction](report.md)
- [Run record](run.json)
- [Native STA cases](evidence/sta-summary.json)
- [SoftAP negative control](evidence/softap-control-summary.json)
