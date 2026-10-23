# ESP Emulator Two-Guest Lab Fabric

- 日期：`2026-10-24`
- 结果：`PASS`（virtual-device）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`8e37781326e337d1d479b3dd432099f4734e8c16`
- 基线版本：`72c2b8d59edc0f446fb35809d4c8e73c818dd9f5`
- 环境：macOS Apple Silicon 本地 Linux fixture；Ubuntu GitHub Actions

## 结论

两台 StickS3 QEMU guest 已能在 private Linux network namespace 内通过
同一个 socket L2 switch 完成独立 DHCP、真实 guest TCP 请求/响应和双侧
pcap 取证。switch 按配置 MAC 绑定连接槽位，不依赖 guest 建连顺序；宿主
控制面、公网 IPv4、metadata 和默认路由均不可达，运行后 namespace、helper
socket 和虚拟网卡已清理。

同一提交还完成共享 WLAN patch `0028` 后的 67-case 全矩阵：`67/67` case、
`274/274` check PASS，所有 case 均为 `attempts=1`、`retry_used=false`。
这是 virtual-device validation，不是 RF、WPA2/WPA3、生产 worker 或恶意
固件沙箱验证。

## 关键证据

- 双 guest fixture：17/17 checks PASS，包含 DHCP reservation、MAC 绑定、
  A→B/B→A TCP、双侧 pcap、宿主隔离和清理。
- UIFlow2 全矩阵：S3/C6/Core2 `67/67` case、`274/274` check PASS。
- 平台契约：`260/260` tests PASS，runner/catalog/profile 校验 PASS。
- GitHub Actions：run `40036279511` 全绿，包含新双设备 TAP/bridge
  primitive。
- 首轮全矩阵曾为 `66 PASS / 1 FAIL`；Cardputer-ADV 键盘用例在 6 秒启动
  窗口内未更新帧。复现后将启动/输入端等待加固为 10/2 秒，定向用例和最终
  全矩阵均通过，没有使用 case retry。

## 文件

- `report.md`：实现、根因、执行、验证和边界
- `run.json`：机器可读记录
- `evidence/verification.summary.json`：公开脱敏证据摘要

## 未覆盖项

- 物理硬件、RF、WPA2/WPA3、多信道和天线行为；
- 自托管 QEMU worker、drain/re-attach、多机调度和对象存储；
- 外部 IPv6 endpoint policy；
- 恶意固件 VM、文件系统/资源隔离和正式租户边界。
