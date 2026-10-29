# Patch validation

`0001-esp32-espnow-external-ccmp.patch` is the unchanged main-repository
`0077` patch.

- SHA256：`4a0aa4fa4d92ddf00d02e62136c4bc881b4a5b6e73edeb78a835feb94a74e095`
- Source files：`include/hw/misc/esp32_wifi.h`、
  `hw/misc/esp32_wifi.c`、`hw/misc/esp32_wifi_ap.c`
- Base：the retained QEMU source state after `0076`
- Forward check：PASS
- Applied output vs recorded QEMU source：PASS for all three files
- Reverse check on the applied tree：PASS

The QEMU checkout is a local imported source tree rather than a public Git
commit, so the record pins retained preimages:

| File | Preimage SHA256 |
| --- | --- |
| `include/hw/misc/esp32_wifi.h` | `e3fb8e27b2ad4159cc0d2c8d29949b93c3c3142852c75d74ed461d3f85d4d9c6` |
| `hw/misc/esp32_wifi.c` | `dfffe5f2e6d60c8726bff4815904af3646daefa705fae7ea8032017cd7954635` |
| `hw/misc/esp32_wifi_ap.c` | `1234310925b1310b0b71aff59110b0a5dfc240656a9877bd78c524e6e02951ee` |
