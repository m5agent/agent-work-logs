# ESP Emulator PR #80：两款视觉主机接入合并

- 日期：`2026-11-02`
- 结果：`PASS`（合并与 CI；设备覆盖保持 `PARTIAL`）
- 工作类型：`pr_review`
- 问题来源：[PR #80](https://github.com/m5agent/m5stack-esp-emulator/pull/80)
- 源码版本：`m5agent/m5stack-esp-emulator @ 34c176f07812630ddfac3e8879208f35f00a0f1d`；merge：`930d7183e68f2e6abdca6803b10b42d3b82626d1`
- 环境：GitHub CI、原 PR 的 native QEMU 回归证据；本次合并任务未新启 guest。

## 结论

按用户要求审核并合并 AtomS3U 与 Atom VoiceS3R 接入。已普通 merge 至 `main`，提交 `930d7183e68f2e6abdca6803b10b42d3b82626d1`。
已有虚拟设备验证覆盖 AtomS3U 板级识别、RMT/GPIO RGB 与按键，以及
Atom VoiceS3R 板级识别和官方 Speaker 路径的 I2S TX DMA PCM。
本次仅回核原 PR 的执行证据、原始产物与 CI，不把证据审核称为新 guest 测试。
两台主机仍为 `partial`/`candidate`，物理硬件 `NOT RUN`。
本地 `main` 因已有 6 个未提交文件未快进，用户改动保持原样。

## 关键证据

- 构建或运行：head CI runs `41403408938`、`41403398446` 均成功，4/4 jobs；平台测试 `1,729` 项 = `1,719 PASS + 10 skipped`；merge CI run `41403793498` 待完成。
- 产物或部署：merge commit `930d7183e68f2e6abdca6803b10b42d3b82626d1`；未新增部署、patch 或固件。
- 实机或服务执行：沿用原 PR regression runner 的 virtual-device 证据；本次未新启 guest。
- 原始产物回核：两测试镜像哈希、12 个串口 marker、PCM 大小/非零字节数/哈希一致；历史运行时已被替换，未用当前二进制代替历史证据。
- 日志、测量或协议：AtomS3U `BOARD 138`、RMT 完成 4 帧；Atom VoiceS3R `BOARD 145`、`STATUS ok`、53,248 B PCM；完整哈希见结构化摘要。

## 文件

- [report.md](report.md)：范围、证据来源、复现与边界。
- [run.json](run.json)：结构化合并记录。
- [evidence/validation-summary.json](evidence/validation-summary.json)：已有执行证据的派生摘要；未附 raw 日志。
- `patches/`：不适用，本次只合并既有 PR。
- `code/`：不适用，复现代码在固定源码提交中。

## 未覆盖项

本次未执行新 guest、全矩阵、物理硬件、声学、光学或电气测试。
IR、麦克风、Grove Unit 数据面、USB CDC 与任意第三方固件不在已验证范围；
Atom VoiceS3R 的功放使能与实际发声未验证；其余视觉主机和 Unit 不继承本结果。

合并后主线 CI `41403793498` 两项成功；平台 `1,729` 项中 `1,719 PASS + 10 skip`。
