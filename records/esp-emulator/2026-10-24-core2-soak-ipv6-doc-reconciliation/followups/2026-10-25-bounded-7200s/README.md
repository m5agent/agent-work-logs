# ESP Emulator Core2 bounded 7200-second soak

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device validation）
- 工作类型：`code_change`
- 问题来源：上一记录中两小时 host RSS 增长为 `REVIEW`
- 源码版本：`m5agent/m5stack-esp-emulator @ aa656c029697940f805442ab37f578edc73485b2`
- 基线版本：`387de4307e06c9a986397e2adbd0bbd789a69015`
- 环境：macOS Apple Silicon；补丁构建 QEMU；真实 Device Service lease

## 结论

最终 `tb-size=128` artifact-bound Core2 active-BLE 两小时 soak 为 `PASS`：

- 1/1 lease，`hold_seconds=7200`；
- firmware、ELF、QEMU 和 runner/service/accelerator/BLE-limit 工具哈希在首
  lease 前冻结，运行期无漂移；
- `bounded_tcg_cache`、frame、34 节点 QOM、WiFi/DHCP/HTTP、公网 DNS/HTTP、
  外部 NUS GATT、active peer、pcap、evidence ZIP 和 cleanup 全部 PASS；
- HLI `45/45`、events 36、ACLs 9，errors/queue/dropped/last-error/peer-close
  均为 0，无 panic；
- 240 个资源采样中 RSS `323536→252992 KiB`、phys footprint
  `250880→188416 KiB`，未形成旧未限容运行的持续增长曲线。

## 未覆盖项

- 121 轮 reconnect；
- bit-exact ESP32 BT controller/baseband；
- 物理 cache/PSRAM、RF、功耗和真机验证。
