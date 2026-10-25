# Firmware capability fail-closed and manifest identity stability

- 日期：`2026-10-26`
- 结果：`PASS`（static firmware contracts + virtual-device regression）
- 工作类型：`code_change`
- 源码版本：
  [m5stack-esp-emulator @ 904d4ec](https://github.com/m5agent/m5stack-esp-emulator/commit/904d4ec7c6fb9516942625c86d619ebba5ae90a3)
- Base commit：`8d7122b79bd6afe43f035e59697f91f8a3e3abc3`
- 环境：macOS arm64；Python 3.13；Node `v22.14.0`；QEMU virtual Core2；
  physical hardware `NOT RUN`

## 结论

发现并修复两个 FirmwareManifest 契约漏洞：

1. unknown **required** capability 过去只产生 warning，manifest 仍可能
   `PASS`。现在 importer、CLI 和 Device Service 都 fail closed，返回
   `REJECTED` / `unsupported_firmware_capability`；unknown optional 仍保持
   warning 和候选状态。
2. 同一 WebBurner 内容从不同名字的输出目录导入时，`artifact.file` 变化导致
   `manifest_id` 漂移。现在 identity payload 排除 `created_at`、
   `manifest_id` 和 `artifact.file`，相同语义内容得到相同 ID。

同一公开 StickS3 Weather SHA 已在 merged 与 WebBurner 两条输入路径验证：
baseline 均 `PASS`，unknown required 均 `REJECTED` 且 exit `1`，unknown
optional 保持 `PASS` 并 warning。两个不同目录名的 WebBurner 包得到相同
manifest ID。

## 关键证据

- capability：
  [`evidence-2026-10-26-unknown-required-capability-fail-closed.json`](https://github.com/m5agent/m5stack-esp-emulator/blob/904d4ec7c6fb9516942625c86d619ebba5ae90a3/tests/firmware/evidence-2026-10-26-unknown-required-capability-fail-closed.json)
- Secure Boot tool-hash rebind：
  [`evidence-2026-10-26-secure-boot-image.json`](https://github.com/m5agent/m5stack-esp-emulator/blob/904d4ec7c6fb9516942625c86d619ebba5ae90a3/tests/firmware/evidence-2026-10-26-secure-boot-image.json)
- Core2 8-instance rebind A/B：
  [A](https://github.com/m5agent/m5stack-esp-emulator/blob/904d4ec7c6fb9516942625c86d619ebba5ae90a3/tests/uiflow2/core2_native_hci/evidence-2026-10-26-core2-concurrent-8x120-fixed-icount-pass-a.json)、
  [B](https://github.com/m5agent/m5stack-esp-emulator/blob/904d4ec7c6fb9516942625c86d619ebba5ae90a3/tests/uiflow2/core2_native_hci/evidence-2026-10-26-core2-concurrent-8x120-fixed-icount-pass-b.json)
- platform tests：`525/525 PASS`
- Node SHA/upload units：`2/2 PASS`
- Core2 8×120 秒：两批均 `8/8 PASS`，合计 `16/16`
- product CI：
  [run 40246432149](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40246432149)
  的 `platform-contracts` 与 `network-namespace-policy` 均 `PASS`

## 文件

- `report.md`：问题、修复、运行、验证和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：提交、哈希、测试和 CI。

## 未覆盖项

- 没有真机、RF、功耗、物理 PSRAM/cache timing 或电气验证；
- known capability 的声明不代表 runtime call path 已执行；
- 没有重跑完整 UIFlow2 67-case matrix；
- unknown capability 的业务语义仍由操作者声明，系统只负责拒绝无法验证的
  required 项。
