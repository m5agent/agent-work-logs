# Patch validation

`0001-esp32-external-espnow-peer-bridge.patch` is the unchanged main-repository
`0076` patch.

- SHA256：`de39dd922d15bc2ad3827a13293d86dc2a2f0dafcfe2036783730dfab8037c62`
- Declared source files：`include/hw/misc/esp32_wifi.h`、
  `hw/misc/esp32_wifi.c`、`hw/misc/esp32s3_wifi.c`
- Base：the retained preimage files used to build the recorded QEMU runtime
- Forward check：`PASS`
- Applied output vs recorded QEMU source：`PASS` for all three files
- Reverse check on the applied tree：`PASS`

The QEMU checkout is a local imported source tree rather than a public Git
commit, so the record declares the retained preimage hashes instead of an
upstream commit:

| File | Preimage SHA256 |
| --- | --- |
| `include/hw/misc/esp32_wifi.h` | `7d9a63f191de75be546ae21b12601b8bfdc551b5907ec19fd9ab67e1cb239508` |
| `hw/misc/esp32_wifi.c` | `9fa6260d6465b5858b15d1483ac2f9e94ebd94e74b32056db1999d8951e0a29a` |
| `hw/misc/esp32s3_wifi.c` | `227828dcddbfef36038c8bc480d3af318a8fdbf2096849966d35e9ea03dc05f7` |

Note: the table is populated from the retained preimages; verify with the
commands in `report.md` before republishing the patch in another series.
