# Cardputer ADV MP3 Player 主线交付与 dry-run 报告

原复核确认默认虚拟板挂载选配外设会触发 M5GFX 板型探测自锁，SPI SD 空闲状态应答也会导致挂载失败。上一轮独立候选已经复现修复后的 FAT32 文件读取、按键触发播放和匹配的虚拟扬声器 PCM。本轮独立记录主线交付，以及正式审核路径中对原版 v1.0.0 的再次验证。[原始虚拟设备复核](https://github.com/m5agent/agent-work-logs/blob/0a4969c549561efcf5423a592ca567a86d838e0b/records/firmware-review-service/2026-11-09-cardputer-adv-mp3-startup/report.md) · [先前的模型修复验证](https://github.com/m5agent/agent-work-logs/blob/db7c1d8b4e876b665aaa3267ae04a7de4709e20a/records/firmware-review-service/2026-11-09-cardputer-adv-mp3-startup/followups/2026-11-09-cardputer-adv-model-fidelity/report.md)

## 构建与执行身份

| 项目 | 身份 |
| --- | --- |
| 合并前主线 | `80d1879a014a55bc598fbc1474445c1f6773ff34` |
| 修复候选 | `340d80cf2e54bbe867f5dbade422ac0907251607` |
| 合并后主线 | `340d80cf2e54bbe867f5dbade422ac0907251607`（本地与远端回读一致） |
| 精确提交的 CI | `platform-contracts` 与 `network-namespace-policy` 均通过。[精确提交 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42548926018) |
| 已验证候选原生 QEMU SHA-256 | `d150c645291e66202d73eb6bdc98900980c2dcb4e851b41d9386dfa6a1ae4b7d` |
| 本轮运行中的原生 QEMU SHA-256 | `d150c645291e66202d73eb6bdc98900980c2dcb4e851b41d9386dfa6a1ae4b7d` |
| v1.0.0 固件源 SHA-256 | `c5918ff914a51b0dc4398f331c8306c25e26a4b157592d3e7d9c0dff2d0c5e45`，885,600 字节 |
| 预期合并 Flash SHA-256 | `10d42a08a69d3e1f628fd9078015a64b598a74f02437c26ecc7201cc2db3e78d`，8,388,608 字节 |
| 已验证 64 MiB FAT32/MBR 卡镜像 SHA-256 | `6e7c003e532f2912b5a6841ea24b6ffbe1ca113caf0dd83b26d750d0cbd7f4a0` |
| 测试音轨 SHA-256 | `30ffce5202e6926566a920c2b236ac74c6077752642b34b85193f67931ae8fc4`，36,362 字节 |

以原版发布文件为输入，核对审核实际取得的源镜像、合并 Flash、介质及运行时身份。让审核任务通过 Device Service 建立 `cardputer-adv` 的独立原生 QEMU 会话，保留无输入的曲库基线，在相同会话选择文件，再绑定输入、SPI 扇区访问、播放帧和后续 PCM。保存并脱敏实测证据，核对任务终态、提交选项关闭、会话停止及 Flash 清理。本轮使用 `saved_snapshot` 审查公开版本的同哈希保存副本。原始任务终态是 `manual_review / SIM_PARTIAL / E_NO_FRAME`，与本轮 `done / SIM_VERIFIED` 分开记录。原始证据已归入审核尝试历史，ZIP SHA-256 为 `10519833a807ae9194334464458476089eba827091031705c79301881781994d`。[上游版本](https://github.com/TurbulentGoat/cardputer-adv-mp3-player/releases/tag/v1.0.0)

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| 主线交付 | PASS | 本地与远端主线回读相同，ahead/behind 为 0/0 |
| 精确提交 CI | PASS | 两项 job 通过，Linux 平台运行 2,041 项，2,031 通过、10 跳过 |
| 审核入口与设备路由 | PASS | 保存快照的源 BIN 与预期 SHA-256、字节数匹配。审核经 Device Service 建立 Cardputer ADV 原生 QEMU 会话，终态为 `done / SIM_VERIFIED` |
| SPI SD 读卡 | PASS | CMD59 在空闲态返回 `0x01`，ACMD41 返回 `0x00`。确认 FAT 读取，回车后观察到 18 个曲目扇区起始 LBA |
| 播放界面 | PASS | 两帧均为 240×135，目视从 `LIBRARY / TEST.MP3` 切到 `NOW PLAYING / TEST`。审核记录接受回车按下和释放 |
| 数字音频 | PASS | 输入前 0 字节，输入后 43,520 字节。按单声道 48 kHz 分析，524 Hz 匹配 3 个窗口，峰值能量占比 0.9833 |
| 清理与审核提交边界 | PASS | 审核报告为 `NOT SUBMITTED`。会话停止，帧和设备状态保留，可写 Flash 已释放且无残留来宾进程 |
| 真机与物理声学 | NOT RUN | 本轮使用原生虚拟设备 |
| 浏览器挂卡播放 | NOT RUN | 审核使用原生 QEMU |

两次取证都关联审核报告里的同一会话。首次离线观察器读取输入收据时用错嵌套层级，误报按键未记录。修正后仅对原两份 ZIP 重新解析，没有重跑固件。[同会话脱敏摘要](evidence/execution-summary.redacted.json)

## 范围与回滚

功能结论只适用于记录中的原版固件、Cardputer ADV profile、虚拟介质和实际运行时。保存快照模式不覆盖实时待审队列。公开摘要只保留运行身份哈希、协议值、状态与计数。主线如需撤回，按 Git 历史创建独立 revert 提交。
