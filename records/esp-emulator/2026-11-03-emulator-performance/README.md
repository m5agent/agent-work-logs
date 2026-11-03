# ESP Emulator 性能修复与同固件对照

- 日期：`2026-11-03`
- 结果：`PARTIAL`；未发布初稿，最终 r2 浏览器与既有准入设备回归待补。
- 工作类型：`code_change`、`report`
- 问题来源：用户询问相同设备、相同固件为何启动慢、运行卡顿，并要求修复及与[参照模拟器](https://zhuzhe1983.github.io/esp-online-tester/platform/)实际比较。
- 源码版本：[m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)，base `3691870c27b028dde76202e42ecddba31d1547c1`；最终源码 commit 待补。QEMU base `40edccac415693c5130f91c01d84176ae6008566`。
- 环境：独立 Device Service 的 native QEMU 虚拟设备，Chromium 156.0.8078.80，实际 Apple M4 Metal 模型画布；未使用物理设备。

## 结论

已验证 native 公共工作台的取帧、SCS 原始读回到 3D 模型及自动路由修复。四次同 native runtime、同固件的前后对照有完整输入、原始 QOM、DOM、实际渲染和清理证据。该结果不授予 browser-WASM CPU、完整逻辑帧或物理性能 PASS。

最终浏览器交付方向为单一 QEMU TCI，保留 O3、typed helper、GPIO 有界事务、精确固件绑定的 one-instruction TB 配置、资源缓存/并行加载和独立帧轮询。最终 r2 patch、构建和真实浏览器验收尚待闭环；JIT/第二后端与中间原型不作为正式 PASS。

## 关键证据

- 构建或运行：本初稿只纳入已验证 native r4；最终 r2 build/guest 未纳入，candidate-r1 不冒充 final。
- 产物或部署：未发布或部署；最终源码 commit 和正式 runtime 身份待补。
- 实机或服务执行：四次 native QEMU 虚拟设备运行，46/46 限定检查通过；证据 ZIP 均在 `purge=0` 停止前请求，保留历史和最后帧，进程已退出。
- 日志、测量或协议：[native summary](evidence/native-summary.json)、[native 验证说明](evidence/native-validation.md)、[证据清单](evidence/manifest.summary.json)。这些是可公开派生摘要，非原始日志或二进制。

## 文件

- [report.md](report.md)：根因、改动方向、限定结果及待验收边界。
- [run.json](run.json)：分层结构化记录。
- `evidence/`：已脱敏的 native 派生证据及其 SHA-256。
- `patches/`：不适用；最终 patch 在源码仓库维护，其最终身份由根任务补齐。
- `code/`：不适用；复现测试入口在源码仓库，最终 commit 待补。

## 未覆盖项

正式 r2 浏览器性能/输入/渲染/清理与全部既有准入设备回归待完成；本记录尚无可引用的最终源码或归档提交。完整原子应用帧保真为 `REVIEW`。native 启动提速比较因冷热缓存不一致而排除，StackChan touch 仅证明协议接受。物理行为、长稳、其他固件/主机/容量均未验证。本初稿未提交、未推送，尚未更新索引。
