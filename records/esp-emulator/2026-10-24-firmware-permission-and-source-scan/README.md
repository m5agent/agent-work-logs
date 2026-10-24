# ESP Emulator 文件权限、源码许可扫描与 Core2 AXP I2C 首错定位

- 日期：`2026-10-24`
- 结果：`PASS`（平台契约与证据生成）
- 工作类型：`code_change`
- 源码版本：`m5agent/m5stack-esp-emulator @ 386cb8f520d93e9a44c12cf5897f419124e5ec30`
- 基线版本：`a79166b68524948ef18480313e3ff3da98031901`
- 环境：macOS Apple Silicon；Python 3；littlefs-python；patched QEMU；公开 UIFlow_Core2 固件

## 结论

完成三项围绕通用固件审查与 Core2 运行时缺口的推进：

1. LittleFS、FAT12/16/32 和 SPIFFS 的每个文件现在都有结构化
   `permission_policy`。FAT 原生 read-only/hidden/system/archive 属性会被
   记录；LittleFS/SPIFFS 明确标记 `unix_mode=not-recorded`。运行态 ACL/权限
   强制仍保持 `NOT RUN`。
2. FirmwareManifest 新增有界源码 SPDX header 扫描。文件数量、总字节、单文件
   和 header 读取均有上限，敏感路径只保留哈希，声明进入
   `license_policy.source_code_declarations`。
3. 对 `UIFlow_Core2` 的 AXP I2C 失败进行地址过滤 trace。AXP2101 address
   `0x34` probe 成功并读出 chip id `0x4a`；随后的
   `disable_timer_interrupt()` 读取在产生下一 address-`0x34` 总线事务前
   失败。`RUNTIME-03` 因而从“AXP 寄存器事务缺口”纠正为首个已证实的
   legacy I2C driver/bus handoff 缺口。

## 关键证据

- 平台套件：`329/329 PASS`，`0 skipped`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`；
- 定向 Ruff `E9/F` 与 Python compile：`PASS`；
- GitHub Actions run `40092069629`：`platform-contracts` 与
  `network-namespace-policy` 均 `PASS`；
- `source_license_scan`：2 个合成源码文件、MIT/Apache-2.0、
  敏感路径脱敏、无 allowlist 时 `REVIEW_REQUIRED`；
- permission policy：FAT read-only 属性、LFS/SPIFFS 无 Unix mode 和
  runtime `NOT RUN` 均有结构化证据；
- Core2 AXP trace：chip-id `0x4a` 成功，后续地址过滤总线事务缺失。

## 文件

- `report.md`：改动、诊断、验证、边界和回滚
- `run.json`：机器可读结果
- `evidence/verification.summary.json`：artifact hash、测试与 trace 摘要

## 未覆盖项

- 未实现固件运行态文件 ACL/权限强制；
- 未覆盖生成代码、包外 vendor 依赖或法律审批；
- `RUNTIME-03` 仍未关闭；
- 两小时 Core2 soak、完整矩阵、物理 cache/PSRAM 和真机未在本次代码提交中执行。
