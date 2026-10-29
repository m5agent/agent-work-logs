# Patch validation

`0001-esp32-espnow-per-peer-key-routing.patch` is the unchanged
main-repository `0082` patch.

- SHA256：`5405d62fe3e4b6fff9cd1b41129b32d296a56b8a288e927ac19e1770acb88a6c`
- Source files：`include/hw/misc/esp32_wifi.h`、`hw/misc/esp32_wifi.c`
- Base：the retained QEMU source state after `0081`
- Forward check：PASS
- Applied output vs recorded QEMU source：PASS for both files
- Reverse check on the applied tree：PASS

```text
git apply --check patches/0001-esp32-espnow-per-peer-key-routing.patch
git apply patches/0001-esp32-espnow-per-peer-key-routing.patch
cmp applied-files recorded-qemu-source-files
git apply --reverse --check patches/0001-esp32-espnow-per-peer-key-routing.patch
```
