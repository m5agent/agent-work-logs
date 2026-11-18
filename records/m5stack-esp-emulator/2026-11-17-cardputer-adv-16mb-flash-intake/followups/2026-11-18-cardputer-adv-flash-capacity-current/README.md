# Cardputer ADV 16 MiB 镜像准入复验

- 日期 `2026-11-18`
- 结果 `PASS`，覆盖虚拟设备的 Flash 容量准入和原版 8 MiB 固件的启动、出帧。
- 工作类型 `firmware_review_attribution` / virtual-device validation
- 问题来源 [Issue #234](https://github.com/m5agent/m5stack-esp-emulator/issues/234)，[原始归因](../../README.md)
- 源码 Device Service 1.99.0 `7babbf9692c403cfc7052d8b9008d915b19a4418`，Reviewer `f0101b6bb0926a69ef2f8477ae81e991338391f5`
- 环境 macOS arm64，独立常规 Device Service 和 Reviewer，原生 QEMU `cardputer-adv`，guest 网卡关闭。

同一份 16 MiB 构建要求的原版 BIN 经 `/firmware` 和 `/firmware/import` 均得到 HTTP 409 `firmware_flash_contract_mismatch`。保存快照复审结束于 `failed / E_STATIC`，详情保留 `Flash 容量` 和 16 MiB / 8 MiB。该镜像未进入虚拟写入或来宾运行，也没有取得租约。

同一服务接受官方 Cardputer ADV 8 MiB UIFlow2 原版，规范化镜像恰为 8 MiB。实际 QEMU 进程执行文件通过哈希绑定，来宾正常出帧。证据 ZIP 的清单、成员大小和哈希均通过验证，停机后确认已释放 Flash、会话租约及进程。

- [执行与边界](report.md)
- [结构化运行记录](run.json)
- [脱敏证据摘要](evidence/replay.summary.json)

物理烧录、16 MiB 实物变体、应用按键和联网均为 `NOT RUN`。本轮未提交 Burner。
