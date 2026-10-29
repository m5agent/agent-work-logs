# Patch validation

`0001-esp32-espnow-peer-fabric.patch` is the unchanged main-repository
`0081` patch.

- SHA256：`b86d3561d503139a4ae8dbda6c4699534b478113ff681784012e562d4d8cf7ca`
- Source files：`include/hw/misc/esp32_wifi.h`、`hw/misc/esp32_wifi.c`、
  `hw/misc/esp32s3_wifi.c`、`hw/xtensa/esp32.c`、
  `hw/xtensa/esp32s3.c`
- Base：the retained QEMU source state after `0080`
- Forward check：PASS
- Applied output vs recorded QEMU source：PASS for all files
- Reverse check on the applied tree：PASS

```text
git apply --check patches/0001-esp32-espnow-peer-fabric.patch
git apply patches/0001-esp32-espnow-peer-fabric.patch
cmp applied-files recorded-qemu-source-files
git apply --reverse --check patches/0001-esp32-espnow-peer-fabric.patch
```
