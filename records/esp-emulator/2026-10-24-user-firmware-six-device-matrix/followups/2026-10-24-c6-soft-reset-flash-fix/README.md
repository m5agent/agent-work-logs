# C6 软件复位 Flash/PMP 修复

- 日期：`2026-10-24`
- 结果：`PASS`（`RUNTIME-01` virtual-device closure）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`d6694295e1ebee48f1056c2894171c48da6cac99`
- 结果版本：`58b7c14538f9407e4ffaecccd98825619ddd0bd6`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40078148754>
- 环境：macOS Apple Silicon；QEMU ESP32-C6；Nesso N1 / NanoC6；
  Device Service `/api/v1`

## 结论

原六设备固件矩阵中的
`c6_chip_id_lost_after_software_reset` 已关闭。问题不是 eFuse 或 chip-id
寄存器，而是 16 MiB Flash 模型把 legacy `0x02/0x20` 三字节写擦命令错误地
按全局四字节地址解析，导致 core dump 写入 `0x300000` 时实际覆盖 Flash
offset `0` 的 C6 bootloader；C6 软件复位后又保留了上一轮 PMP range。

修复后：

- bootloader offset 0 保持 `chip_id=0x0d`；
- `LP_SW_HPSYS` 后不再出现 `Invalid chip id. Expected 13 read 12`；
- 同一 Meshtastic SHA 经 Device Service 重跑为
  `runtime_model_gaps=[]`；
- Nesso N1 官方外设组 `5/5 PASS`；
- NanoC6 板级探针 PASS。

该 Meshtastic 样本仍有独立的 Instruction access fault，因此完整功能仍是
`PARTIAL`。本轮只关闭 Flash/PMP 导致的软件复位 chip-id 错误，不宣称该
固件整体 PASS。

## 关键证据

- 固件 SHA256：
  `ef8249ac7930fa51ac5bf03cea52d8de9a59dcbaf2130663ca0d5087a8053744`
- QEMU SHA256：
  `25497c521ebd5838a56b066551dd5c33d6dd00df853ed4a256fcca79944de7db`
- 修复前坏 header：
  `e9010200100486406c0000000c000000`
- 修复后 offset 0：
  `e903024010c48640ee0000000d000000`
- Device Service session：
  `b405105224694aa68dc51159ffb085d8`
- 重跑 serial SHA256：
  `f08a47b81806ebdf0eb9746ce0dfa00231afa1190b230b40e243540da9db2736`
- 本地平台 `317/317 PASS`；Node `2/2 PASS`；CI 两个 job PASS。

## 文件

- `report.md`：根因、修复、回归与边界；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：聚合 evidence；
- `evidence/relevant-serial-summary.txt`：修复前后的关键串口行。

## 未覆盖项

- Meshtastic 修复后的独立 Instruction access fault；
- C6 Zigbee/802.15.4 `RUNTIME-02`；
- 所有 C6 flash opcode/reset cause 的穷举；
- RF、功耗、电气和物理硬件验证。
