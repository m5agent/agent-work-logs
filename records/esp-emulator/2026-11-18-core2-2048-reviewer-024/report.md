# Core2 2048 Game 1.0 原版四方向审核

本次用同一份 505,760 字节原版应用 BIN，在已冻结的 Device Service 1.93.0 和原生 QEMU 上复跑审核。此前 1.89.0 对照保存了相同固件和四向操作基线。[此前复审](../2026-11-18-mp3-2048-original-replay/followups/2026-11-18-core2-2048-189-review021/report.md)

## 棋盘级验收

Reviewer 0.24.0 可为匹配的 Core2、原版应用摘要和规范化 Flash 摘要启用 `validation.core2_2048_moves`。`drag_plan` 使用 320×240 屏内水平或垂直坐标，至少包含每个方向一次。测量以动作前后的成对稳定帧读出 4×4 棋盘，预测该方向的移动与合并，随后核对只在原为空位的一格出现新 2 或 4。方向纳入覆盖需要真实输入回执和合法棋盘变化。畸形计划在排队和分配设备租约前以 HTTP 400 拒绝。

| 方向 | 已验证合法移动 |
| --- | ---: |
| 左 | 2 |
| 右 | 2 |
| 上 | 2 |
| 下 | 2 |

最终 Reviewer 提交 `c1d9bc98dbdf5253ba7a15cf87103d040e6f89ad` 通过同一原版保存快照复审，结果为 `done / SIM_VERIFIED`。独立取证重新读取每次动作的两张画面、位移规则、证据 ZIP 的 CRC 与清单，并核对应用分区原字节、启动串口和实际原生 QEMU 摘要。隔离来宾与服务均已停止，租约归零，临时 Flash 已释放。首轮隔离结果也为四向 8/8。早期复跑脚本误期待 HTTP 409，实际得到 HTTP 400 后停在排队前。修正脚本后再次通过标准重试，HTTP 202 受理并执行到终态。[原版、棋盘与归档证据](evidence/core2-2048-reviewer-024.summary.json)

## 交付范围

原生运行时保持同一冻结版本。已更新 Reviewer 并核对 0.24.0 接口，两个 Device Service 角色均保留 1.93.0。Reviewer 的 283 项源代码测试通过。当前未发现匹配的实体 Core2，因此实体操作与同 BIN 实机对照为 NOT RUN。浏览器为 NOT RUN，Burner 未提交。[Device Service 精确 OpenAPI](https://github.com/m5agent/m5stack-esp-emulator/blob/8ba3677708fbf11d47576f2dda1baa8431492452/docs/device-service.openapi.yaml)
