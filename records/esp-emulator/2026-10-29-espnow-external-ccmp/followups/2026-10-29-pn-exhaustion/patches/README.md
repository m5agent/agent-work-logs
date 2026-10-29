# Patch validation

`0001-esp32-espnow-ccmp-pn-exhaustion.patch` is the unchanged main-repository
`0083` patch.

- SHA256：`3e9d54b16b0ec3429347bb9d36efe96755935e2cff3d045cf3af3b0b82adcfa9`
- Source files：`include/hw/misc/esp32_wifi.h`、`hw/misc/esp32_wifi.c`
- Base：the retained QEMU source state after `0082`
- Forward check：PASS
- Applied output vs recorded QEMU source：PASS for both files
- Reverse check on the applied tree：PASS

```text
git apply --check patches/0001-esp32-espnow-ccmp-pn-exhaustion.patch
git apply patches/0001-esp32-espnow-ccmp-pn-exhaustion.patch
cmp applied-files recorded-qemu-source-files
git apply --reverse --check patches/0001-esp32-espnow-ccmp-pn-exhaustion.patch
```
