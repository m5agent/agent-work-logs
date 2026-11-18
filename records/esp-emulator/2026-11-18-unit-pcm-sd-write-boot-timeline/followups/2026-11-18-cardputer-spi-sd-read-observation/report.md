# Cardputer 原生 SPI SD 读响应与保存快照审核

## 原生 SPI 计数

原生 Xtensa 补丁 0227 在模型成功读取 512 字节并排入响应时增加 `accepted_cmd17` 或 `accepted_cmd18`。它在完整送出数据和最后一个 CRC 字节时增加 `completed_blocks`。一个 CMD18 可产生多个完成块。机器复位结束计数代次，旧多块流的续块仍属于原命令的代次。CS 中途中断会取消当前块的完成资格。计数基于模型响应，来宾取得或使用的数据需要单独核验。

固定运行时 SHA-256 为 `26f753119896c70d6287f516cc54e941ad9fa328b0464b7af7385c3b9387d12d`。实际 ESP-IDF 夹具在 Cardputer、Cardputer ADV 上各记录 16 条 CMD17 接受、16 个完成块。无卡的 ADV 为 0。ADV 多块夹具记录 16 条 CMD17、1 条 CMD18 和 18 个完整响应块，来宾 UART 另确认两扇区的 MBR 和空白扇区内容。Cardputer 复位后从代次 1 的 16/16 变为代次 2 的 19/19，读到的是新的累计值。原生会话关闭 SPI 日志。 [原生验证摘要](evidence/native-spi-sd-read.summary.json)

宿主侧协议回归覆盖 CRC 错误、越界、未就绪、最后 CRC 前移除片选、CMD18 续块跨复位被排除及新命令恢复。Cardputer 的两个 GP-SPI 主机在源码中共用计数。本轮来宾夹具实际用 SPI2，SPI3 独立路径未执行。

## Device Service 与原版审核

Device Service `23904862ae25a86d36e609b1f37e164027401d02` 的 `1.85.0` 合约把该信息绑定到同一会话、固件、进程、介质和复位代次，并按 ACL 授权。旧执行器缺能力时返回类型化的不可用结果。确认空槽能读到零和无介质。审核用同一稳定代次的累计值做最低块数判定，包含启动时读卡，另报告采样区间的增量。

固定 Reviewer `936be8b65ccf0598e80bf783c5a76cc06b2ddcb3` 和原版 CardputerDict ADV 0.5.0 的五轮离线保存快照同样关闭 SPI 日志。核对同会话 ZIP 的全部成员和审核报告，`sd-read.json` 与报告字段一致。

| 对照 | 已完整送出块 | SD 观察 | 查词画面 |
| --- | ---: | --- | --- |
| 完整词库 | 136 | PASS | PASS，指定释义 |
| 缺正文 | 110 | PASS | FAIL，稳定画面未显示指定释义 |
| 无卡 | 0 | FAIL，确认无介质 | FAIL |
| 新接口配旧执行器 | 不可用 | PARTIAL | PASS，完整词库显示指定释义 |
| 旧 Device Service 和旧执行器 | 不可用 | PARTIAL | PASS，完整词库显示指定释义 |

完整词库的基线已有 111 个完整块，观察结束为 136 个。缺正文从 79 到 110。两轮的累计计数都通过，只有完整词库取得目标功能证据。原版整单还需同一审核的其余功能与网络证据。此前用 SPI 日志统计的 CMD17 是请求数，本轮统计完整送出的响应块。 [原版 Reviewer 五路摘要](evidence/reviewer019-original-dictionary.summary.json)

## 原版 ADV MP3 复跑

相同审核版本在固定原版 Cardputer ADV MP3 Player 1.0.0 及 FAT32 音频夹具上运行。会话关闭 SPI 日志，累计完整响应为 58 个块，从基线 4 个增加 54 个。同会话数字扬声器 PCM 的两段各 16,384 字节，主频为 522.792 Hz 和 522.582 Hz，均符合 524 Hz 夹具的验收判据。回读 ZIP 中的精确样本范围与摘要一致，整体审核 `SIM_VERIFIED`。数字频率证明这次来宾音频行为，块计数独立支持底层 SPI 响应。 [原版 MP3 回执](evidence/reviewer019-original-mp3.summary.json)

## 源码与界面回读

本地完整平台套件运行 2,424 项，10 项跳过，零失败。较早一次套件保留四项失败，属于 API 操作清单及文档行数、生成快照和链接，修正后重跑。Reviewer 全部 256 项通过。GitHub CI 的平台合约和网络命名空间策略两项均通过。Chromium 对四条隔离审核结果经实际 HTTP 读取的 SD 状态进行核对，同时确认服务返回的 HTML 与固定候选相符。浏览器此处用于核对审核页面。 [模拟器原生证据](https://github.com/m5agent/m5stack-esp-emulator/blob/baf174cec565f160d146fbad39c857686319917b/tests/firmware/spi_sd_media/read-stats-summary.json) · [页面回读](evidence/reviewer019-ui.summary.json) · [GitHub CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44207826414)

## 复现与范围

用相同板型、固件和 SD 镜像分别执行有卡、缺正文和无卡控制。在独占原生会话读取两次会话 SD read-stats。核对代次与受控媒体身份，再通过原版 Enter 动作的稳定画面区域验证释义。原生会话、Flash、租约均清理。真机、浏览器 WASM 和 Burner 提交未执行。
