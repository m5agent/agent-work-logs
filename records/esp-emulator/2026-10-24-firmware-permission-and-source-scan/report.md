# ESP Emulator 文件权限、源码许可扫描与 AXP I2C trace 报告

## 背景

当前 P0 仍需要推进 FirmwareManifest 安全审查和 Core2 运行时模型缺口。已有
FirmwareManifest 能导入镜像、检查 capability/security 并解析 LittleFS/FAT/
SPIFFS，但资源权限策略和源码许可证据不完整；Core2 的
`RUNTIME-03` 则被笼统描述为 AXP PMIC 寄存器事务错误。

## 文件权限策略

### 实现

- `firmware_filesystems.py` 增加统一的 `permission_policy`、`permission_model`
  和 `permission_summary`。
- FAT 文件从 directory entry 读取 `read-only`、`hidden`、`system`、`archive`
  属性；FAT 目录也有独立 `directory_permissions`。
- LittleFS/SPIFFS 不携带 Unix mode，因此文件明确记录
  `model=none`、`unix_mode=not-recorded`、`runtime_enforcement=not-proven`。
- `filesystem_permission_policy` / model / summary 已加入 Manifest schema。

### 边界

- FAT read-only attribute 不是 POSIX read-only、ACL 或运行态不可变证明。
- 所有文件系统的 `permission_summary.runtime_enforcement` 固定为 `NOT RUN`。
- 运行态权限只能由真实 guest/系统路径验证。

## 包内源码许可扫描

### 实现

- 扫描 `.c/.cc/.cpp/.h/.hh/.hpp/.py/.js/.mjs/.ts/.tsx`。
- 上限为 2048 文件、总计 64 MiB、单文件 2 MiB、每个文件读取前 64 KiB。
- 每个源文件记录 SHA256、脱敏路径和 SPDX 声明。
- 敏感路径只写 `<redacted-sensitive-path>` 与路径 SHA256。
- 声明进入 `license_policy.sources`，并记录
  `coverage.source_code_declarations`。

### 边界

- header 窗口之外的内容不扫描；
- 包外 vendor、生成代码和缺失源码不在覆盖范围；
- 这不是法律意见或完整许可证兼容结论。

## Core2 AXP I2C trace

同一公开固件：

- source SHA256：
  `18d77e28adfacf7e719a167bd0c3450b78357d13cb1d2f2a8b7bccc2248a909a`；
- normalized flash SHA256：
  `743c4ea49e8031ca1e293e9160c4b2af65035bfdbe1d93675779241858007ec4`；
- `m5core2`、`axp2101`。

临时启用 controller/device trace：

```bash
M5SW_I2C_TRACE=1 M5SW_I2C_ADDR_TRACE=34 \
  qemu-system-xtensa -M m5core2 ... -serial stdio -m 0
```

观察结果：

- AXP address `0x34` probe `start_rc=0`；
- chip id 读取 `[axp2101] rd 03 -> 4a`；
- 随后 Python `hardware.__init__.__read_byte` 返回
  `OSError: I2C bus error (19)`；
- 失败读取之前没有产生新的 address-`0x34` controller transaction。

因此首个已证实缺口位于 M5GFX 到 `machine.I2C` 的 driver/bus handoff，
而不是 AXP chip-id 或后续寄存器值。后续需要检查 bus ownership、driver
install 和 controller state，并取得匹配源码/frozen bytecode。

## 验证

```bash
PYTHONPATH=platform/tools:.work/py python3 -m unittest discover \
  -s platform/tests -p 'test_*.py' -v

python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check

ruff check --select E9,F \
  platform/tools/firmware_filesystems.py \
  platform/tools/firmware_manifest.py \
  platform/tests/test_firmware_analysis.py \
  platform/tests/test_firmware_manifest.py \
  platform/tests/test_docs_consistency.py
```

结果：平台套件 `329/329 PASS`；所有 catalog/profile/coverage/snapshot 检查和
定向静态检查 PASS。GitHub Actions run `40092069629` 的
`platform-contracts` 与 `network-namespace-policy` 两个 job 均 PASS。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build/static | `PASS` | Python compile、定向 Ruff、schema JSON 与平台测试 |
| static firmware | `PASS` | permission policy、FAT attributes、SPDX source scan |
| runtime diagnosis | `PASS` | Core2 AXP trace 完成首错分类 |
| runtime fix | `NOT RUN` | `RUNTIME-03` 未关闭 |
| full matrix | `NOT RUN` | 本轮没有改变共享 QEMU controller |
| hardware | `NOT RUN` | 无物理设备验证 |

## 风险与回滚

- 源码扫描基于有界 header 和扩展名，可能漏掉无 SPDX header 或不在包内的源码。
- FAT 属性不等同于运行态权限。
- AXP trace 使用临时本地地址过滤 instrumentation；产品 QEMU build 已恢复，
  evidence 绑定该诊断 build 的 SHA256。
- 回滚可整体 revert：
  `386cb8f520d93e9a44c12cf5897f419124e5ec30`。
