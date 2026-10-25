# Firmware security preflight understatement fail-closed

- 日期：`2026-10-26`
- 结果：`PASS`（static security contracts）
- 工作类型：`code_change`
- 源码版本：
  [m5stack-esp-emulator @ eb7d80a](https://github.com/m5agent/m5stack-esp-emulator/commit/eb7d80a27166be41f82782e7c104bc82226b6b30)
- Base commit：`904d4ec7c6fb9516942625c86d619ebba5ae90a3`
- 环境：macOS arm64；Python 3.13；Node `v22.14.0`；无 QEMU guest 启动

## 结论

Device Service 过去主要依据 manifest 的聚合
`security.secure_boot` / `security.flash_encryption` 字段做 runtime
preflight。调用者可以把聚合字段写成 `unknown`，同时保留 sdkconfig v2、
signed Secure Boot image、invalid signature 或 eFuse enabled 证据，从而绕过
“当前 runtime 未建模安全链”的拒绝。

现在 preflight 联合检查所有可用证据层：

- aggregate security；
- sdkconfig `secure_boot_config` / `flash_encryption_config`；
- `secure_boot_image.status`；
- 包内 `efuse_summary` 的 secure boot / Flash Encryption 声明。

任一层要求当前 profile 未建模的安全链，或有 invalid Secure Boot image
证据，都会 `REJECTED`。结构校验同时要求三个核心 security 字段存在且为合法
枚举；schema 补上了显式 `disabled` config 值。

## 关键证据

- security preflight 静态 fixture：`11/11 checks PASS`
- 当前代码的 Secure Boot v2 fixture：`26/26 checks PASS`
- platform tests：`530/530 PASS`
- 两轮 security/docs/service 定向测试分别为 `28/28` 与 `29/29 PASS`
- Node SHA/upload units：`2/2 PASS`
- security preflight 与 Secure Boot evidence 均可重复生成且 byte-identical
- product CI：
  [run 40246916115](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40246916115)
  的 `platform-contracts` 与 `network-namespace-policy` 均 `PASS`

## 文件

- `report.md`：绕过路径、修复、验证和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：提交、工具/evidence 哈希和检查。

## 未覆盖项

- 没有 live eFuse 读取或包内 summary 来源认证；
- 没有 ROM/bootloader trust-chain 执行；
- 没有 Flash Encryption key/runtime、生产 key 或真机验证；
- 没有重跑完整 UIFlow2 67-case matrix。
