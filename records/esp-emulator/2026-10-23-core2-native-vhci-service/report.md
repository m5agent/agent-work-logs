# Core2 native-VHCI Device Service 报告

## 背景

同 guest native-VHCI 已由独立 runner 验证 3/3，但还没有进入正式 Device
Service 状态机。此次目标是把相同能力暴露为 `/api/v1` lease，并保留 frame、
QOM、网络、BLE、pcap 和 manifest evidence。

## 实现

- 新增 `core2-native-vhci` unified profile；
- 强制 `network.elf_artifact_id`，并校验 artifact 记录；
- 将 ELF 加入 session source artifacts，避免 active/history 期间被 GC；
- QEMU 使用 `-m 0`、`-S`、dynamic GDB port、OpenMAC WiFi 和 QMP；
- GDB bridge 从指定 ELF 动态解析 VHCI/API/idle 符号；
- supervisor 先启动 Bumble peer，再启动 GDB bridge；
- 停止 session 时先终止 GDB bridge，再终止 QEMU 和 Bumble；
- `/network` 汇总 serial、peer、HTTP、bridge H2C/C2H/ACL 和 pcap；
- evidence ZIP 加入 `native-vhci-gdb.log`；
- OpenAPI/runtime contract 升至 `1.7.0`。

## 执行

真实 Device Service 流程：

```text
POST /artifacts              firmware
POST /artifacts              matching ELF
POST /firmware               merged image
POST /sessions               qemu-unified / core2-native-vhci
GET  /sessions/{id}          running + network PASS
GET  /sessions/{id}/network  18/18 checks PASS
GET  /sessions/{id}/evidence ZIP with frame/QOM/pcap/bridge/peer
GET  /sessions/{id}/qom      AXP2101=4000, MPU6886 accel-x=0.25
DELETE /sessions/{id}        purge=0, retain_flash=0
```

## 验证

```text
device service native-VHCI    PASS
network checks                18/18 PASS
evidence ZIP                  12 files
platform tests                213/213 PASS
runtime coverage              PASS
peripheral catalog            PASS
QEMU profiles                 PASS
physical hardware             NOT RUN
```

## 证据

evidence ZIP 包含：

- serial、QEMU stdout/stderr；
- `ble-probe.log`；
- `native-vhci-gdb.log`；
- `frames/current.png`；
- `audio/speaker.pcm`；
- `qom/snapshot.json`；
- `network/evidence.json`；
- `network/capture.pcap`；
- `manifest.json`。

pcap summary 记录 DHCP、DNS、受控 HTTP、公网 HTTP 和 payload hashes，不复制
明文 payload。

## 边界

该记录是 virtual-device validation。GDB bridge 是服务托管的诊断后端，不是
bit-exact controller。trusted-host 网络也不是恶意固件沙箱。RF、功耗、
声学、光学、机械和真机验证均未执行。

## 回滚

回滚源码提交 `bf500ec3a6287586bdb28713a0feedc7e19a9eaf` 可撤销 profile、
API 1.7.0、GDB supervisor 和 evidence 集成；没有修改物理设备。
