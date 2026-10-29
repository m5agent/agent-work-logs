# Patch validation

`0001-esp32-espnow-loss-channel-rate.patch` is the unchanged main-repository
`0084` patch.

- SHA256：`91ef766541a9802336d5a3efaefc38fd28f5d7ea55107e605e2ec37fdf2594fc`
- Source files：`include/hw/misc/esp32_wifi.h`、`hw/misc/esp32_wifi.c`、
  `hw/misc/esp32s3_wifi.c`
- Base：the retained QEMU source state after `0083`
- Forward check：PASS
- Reverse check on the applied tree：PASS

```text
git apply --check patches/0001-esp32-espnow-loss-channel-rate.patch
git apply --reverse --check patches/0001-esp32-espnow-loss-channel-rate.patch
```
