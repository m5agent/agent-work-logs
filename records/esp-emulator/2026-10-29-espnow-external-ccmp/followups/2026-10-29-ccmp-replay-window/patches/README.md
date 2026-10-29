# Patch validation

`0001-esp32-espnow-external-ccmp-window.patch` is the unchanged main-repository
`0079` patch.

- SHA256：`c4f40a614412db0b0c642f448820bb1acb8cf9bbe980df4e20e15d5c74556e0c`
- Source files：`include/hw/misc/esp32_wifi.h`、`hw/misc/esp32_wifi.c`
- Base：the retained QEMU source state after `0078`
- Forward check：PASS
- Applied output vs recorded QEMU source：PASS for both files
- Reverse check on the applied tree：PASS

Retained preimages:

| File | Preimage SHA256 |
| --- | --- |
| `include/hw/misc/esp32_wifi.h` | `d4b9f3e84f40d49196a8c15b4245906e426f6648b9433c02fea59126ce621251` |
| `hw/misc/esp32_wifi.c` | `9cc864986c0eb811cda69469eb2c2ad268ba4718f871224e5491d9817059afd3` |
