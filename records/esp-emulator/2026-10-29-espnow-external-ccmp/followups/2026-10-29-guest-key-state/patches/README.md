# Patch validation

`0001-esp32-espnow-guest-key-state.patch` is the unchanged main-repository
`0080` patch.

- SHA256：`c827a3e6e76f591b319379342e099a5cd4ffd086029fb514cb99c61a72e2babc`
- Source files：`include/hw/misc/esp32_wifi.h`、`hw/misc/esp32_wifi.c`、
  `hw/misc/esp32s3_wifi.c`、`hw/xtensa/esp32.c`、
  `hw/xtensa/esp32s3.c`
- Base：the retained QEMU source state after `0079`
- Forward check：PASS
- Applied output vs recorded QEMU source：PASS for all files
- Reverse check on the applied tree：PASS
