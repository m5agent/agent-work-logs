# ESP Emulator public firmware refresh and SHA binding

- 日期：`2026-10-25`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：公开 M5Burner 固件 ID/version 下的 CDN 内容会变化
- 源码版本：`m5agent/m5stack-esp-emulator @ b8dbc2d0d6fad12f341145a6c25e2d91e48c45ba`
- 基线版本：`3631a13f1f7b06c35850f7f843e91d5d1179d3f3`
- 环境：macOS Python 平台测试；静态 FirmwareManifest 导入；无 QEMU 执行

## 结论

矩阵 artifact identity 已收紧：

- 首次选择强制刷新当前公开 BIN；
- `--resume` 也重新下载并重算 SHA；
- result key 为 `device:firmware:sha256`，CDN 字节变化后不会复用旧完成结果；
- 当前 4 个刷新 BIN 均完成静态分析和完整 FirmwareManifest 导入；
- 4 个 manifest validation 均为 `PASS`，但 static review 全部为
  `REVIEW_REQUIRED`；
- Device Service boot/frame/input 仍为 `NOT RUN`，因此整体为 `PARTIAL`。

## 关键证据

- 平台套件：`351/351 PASS`；
- user firmware matrix：`15/15 PASS`；
- 文档一致性：`19/19 PASS`；
- GitHub Actions run `40113705698`：`PASS`；
- 4 个 source SHA、normalized artifact SHA、manifest ID 和 review 计数已绑定。

## 未覆盖项

- 当前 4 个 BIN 的 Device Service 启动、首帧和输入；
- 全部 7 台设备/更多固件族回归；
- 物理硬件验证。
