# ESP Emulator 代码文档重整与 Core2 同 guest 重连边界

- 日期：`2026-10-24`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 源码版本：`m5agent/m5stack-esp-emulator @ e686838e38dc8ec46daa6dbc2830322806ca7355`
- 基线版本：`4e055979c908d40d6c2ca31b78f3711599e90919`
- 环境：macOS Apple Silicon；Python 3；现有 Core2 UIFlow2 v2.5.3 镜像、匹配 ELF 和 patched QEMU

## 结论

完成一次代码、API、契约、当前状态、Backlog、专题文档和历史入口的统一对账。
动态能力只在 `project-status.md` 维护，未完成项只在 `project-backlog.md` 维护；
历史调查页继续保留原日期和取代关系。

同时把 Core2 同一 guest 的 BLE disconnect/reconnect 做成可复现门禁。第一轮
scan/connect/NUS write/notify/disconnect 通过，但 disconnect 后 guest 连续输出
`NimBLE: HCI process ack returned 12` 并进入 HCI reset 循环，第二轮没有
advertisement。未加入测试重广告逻辑的 stock guest 同样失败，因此 blocker 位于
disconnect/HCI command lifecycle，而不是单独的 `gap_advertise()` 调用。

本次为 virtual-device validation。同 guest reconnect 仍为 `FAIL`；bit-exact
BT controller、物理 cache/PSRAM、多小时 soak 和真机验证均未完成。

## 关键证据

- 平台测试：`299/299 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles：`PASS`；
- Node SHA256/upload client：`2/2 PASS`；
- `compileall` 与定向 Ruff：`PASS`；
- GitHub Actions CI run `40066005133`：`PASS`；
- reconnect 对照：stock guest 与测试用途重广告 guest 都在 cycle 1 后
  `ack 12`/HCI reset，cycle 2 advertisement timeout，无 guest panic；
- 完整 UIFlow2 外设矩阵本轮未重跑：`NOT RUN`；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：改动范围、验证、证据与边界
- `run.json`：机器可读记录
- `evidence/verification.summary.json`：聚合验证和 artifact hash

## 未覆盖项

- 未定位 `ack 12` 来自哪一条 H2C command 或哪一条 QEMU HLI event 顺序；
- 未实现同 guest 第二轮 GATT PASS；
- 未执行多小时 soak、bit-exact controller/baseband 或物理 cache/PSRAM；
- 未执行真机同路径验证；
- 未重跑完整 UIFlow2 外设矩阵。
