# ESP Emulator 当前状态、代码边界与执行队列重整

- 日期：`2026-10-25`
- 结果：`PASS`（docs/contracts；设备运行时项仍按 Backlog 执行）
- 工作类型：`code_change`
- 问题来源：用户要求完整整理代码和文档，并结合近期工作刷新过期状态
- 源码版本：`m5agent/m5stack-esp-emulator @ 1d3694eea6a4cf39ccfa56e53b8bbb9bfe28b575`
- 基线版本：`2cde43a466919a9d8eadb6c840fad31ca4b17d65`
- 环境：macOS 测试主机；不涉及物理硬件

## 结论

当前入口文档、设备生成源、QEMU profile、Backlog、验证台账和代码地图已按
`1d3694e` 对账，清除了三类明显漂移：

1. Core2 reconnect 契约已是 `1–121`、拒绝 `122`，旧设备文档仍写
   `1–120`、拒绝 `121`；
2. 旧 Core2 两小时 RSS 增长已由 `vmmap` 归因到未限容 TCG translation
   buffer，不能继续写成“增长对象未定位”；
3. 公开 M5Burner CDN 可在同一 firmware ID/version ID 下改变 BIN，历史
   PASS/PARTIAL 必须绑定 SHA，刷新后的制品必须重新执行 Device Service。

执行队列已收敛为：Core2 限容两小时收口 → 3 个独立 lease × 121 轮
reconnect → Linux namespace IPv6 AAAA/HTTP/denied-port/cleanup → 当前公开
AtomS3R/PaperMono 四样本功能重跑 → NET-04 跨主机能力与固件安全。

## 关键证据

- 完整平台套件：`349/349 PASS`。
- 文档一致性：`19/19 PASS`；新增公开 BIN 刷新与 SHA 绑定回归。
- Node SHA256/upload client：`2/2 PASS`。
- `runtime_coverage`、`peripheral_catalog`、`qemu_profiles` 和
  `project_snapshot --check`：全部 `PASS`。
- Python fatal Ruff、变更文件 `F401/F841` 检查、`compileall` 和
  `git diff --check`：全部 `PASS`。
- 四个刷新后公开 BIN 已完成下载与静态结构分析；Device Service
  boot/frame/input 功能验证为 `NOT RUN`。

## 文件

- `report.md`：改动、发现、验证和边界。
- `run.json`：机器可读记录。
- `evidence/verification-summary.json`：脱敏检查摘要。
- `patches/`、`code/`：不适用；代码和测试位于公开源码仓库。

## 未覆盖项

- Core2 限容 `7200s` 最终 evidence 尚未收集。
- 121 轮 reconnect、Linux namespace 同 guest IPv6 生命周期和四个刷新样本
  尚未执行。
- NET-04 跨主机 QEMU executor/reattach、companion continuity 仍在 Backlog。
- 全部结果均为代码、契约或虚拟设备证据；物理硬件 `NOT RUN`。
