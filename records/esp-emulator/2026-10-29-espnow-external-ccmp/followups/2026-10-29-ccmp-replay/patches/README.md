# Patch validation

`0001-esp32-espnow-external-ccmp-replay.patch` is the unchanged
main-repository `0078` patch.

- SHA256：`b30c56272dba2fd6e4000ee8b12f82a08e57ccadf8bc8e0d0d42488b5baa1adc`
- Source files：`include/hw/misc/esp32_wifi.h`、`hw/misc/esp32_wifi.c`
- Base：the retained QEMU source state after `0077`
- Forward check：PASS
- Applied output vs recorded QEMU source：PASS for both files
- Reverse check on the applied tree：PASS

Retained preimages:

| File | Preimage SHA256 |
| --- | --- |
| `include/hw/misc/esp32_wifi.h` | `d32f8aef2b3a3f1176dca1317712e6cc7e7e108af9d1ee484bb1fa956d8710be` |
| `hw/misc/esp32_wifi.c` | `a26e1659e640d92805a70b80d88af84fa9475922eea69089f296f33020330504` |
