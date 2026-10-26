# ESP Emulator FirmwareManifest policy fail-closed report

## 背景

目标要求标准 FirmwareManifest、WebBurner 导入、安全配置和 capability
mismatch 检查可用于后续固件审查。上一轮已关闭 unknown required capability
和 aggregate security understatement，但继续审计手写 manifest 发现：

1. 根 `capabilities` 不在 schema required 中，内部校验也会在字段缺失时跳过；
2. image status understatement 只检查 aggregate status，没有检查同对象
   中仍存在的 signed blocks；
3. `efuse_summary` 在 schema 中是无约束 object，内部结构校验也未检查其
   secure-boot / encryption 值。

## 修复前反例

最小 Python fixture 在普通 ESP32-S3 镜像上确认：

```text
delete manifest.capabilities
  validate_manifest_structure -> []
  validate_capabilities -> PASS

signed Secure Boot image
  set security.secure_boot_image.status = not-found
  keep two signed image entries
  set aggregate/config secure boot = unknown
  validate_capabilities -> PASS

efuse_summary = {
  secure_boot: enabled,
  flash_encryption: enabled-active
}
  validate_manifest_structure -> []
  validate_capabilities -> PASS
```

## 修复

### Capability policy

- root schema required 新增 `capabilities`；
- `capabilities.required` 和 `capabilities.optional` 必须存在且为数组；
- 每个数组最多 64 项，每项 1–64 字符；
- 内部结构校验和 `validate_capabilities()` 都独立检查，避免调用方绕过
  schema；
- 缺失对象返回 `capabilities_required`，缺失/畸形数组返回
  `invalid_capability_declarations`。

### Security evidence consistency

- `secure_boot_image.status=not-found` 不能再与 signed image blocks 共存；
- image status 与 trust-root comparison 必须一致；
- package eFuse key digest mismatch 直接拒绝；
- image secure version 低于 package eFuse anti-rollback version 直接拒绝；
- `efuse_summary.secure_boot` / `flash_encryption` 使用严格枚举；
- 主 manifest 和 eFuse summary 的 security 字段同时缺省/非法时 fail
  closed。

## 验证

新增 `tests/firmware/manifest_policy/run_test.py`，并生成
`evidence-2026-10-26-manifest-policy-fail-closed.json`。checks 覆盖：

- baseline PASS；
- capabilities 整体缺失、required/optional 缺失、64 项上限；
- signed image status 下调；
- eFuse 非法启用字符串；
- key digest mismatch；
- secure-version rollback。

同时用新 `firmware_manifest.py`/schema tool hash 重跑 Secure Boot v2 image
fixture，`26/26` checks PASS，签名数学、image digest、key digest 和
anti-rollback 的 static/not-verified 边界不变。

验证命令：

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'

PYTHONPATH=platform/tools python3 \
  tests/firmware/manifest_policy/run_test.py

PYTHONPATH=platform/tools python3 \
  tests/firmware/secure_boot_image/run_test.py \
  --out-dir /tmp/m5-secure-boot-rebind \
  --date 2026-10-26
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| platform contract | `PASS` | `537/537` |
| manifest policy fixture | `PASS` | 13/13 checks |
| manifest unit tests | `PASS` | `32/32` |
| Secure Boot image fixture | `PASS` | `26/26` |
| schema/coverage/catalog/profile/snapshot | `PASS` | generated checks |
| firmware/QEMU functional | `NOT RUN` | 本轮为 static manifest policy |
| live eFuse / ROM trust chain | `NOT RUN` | 无真机或 boot trace |
| physical hardware | `NOT RUN` | 无 RF、电气或功耗验证 |
| delivery | `PASS` | product `c00fd2e`；CI `40250487931` 两 job 均成功 |

## 验证边界

包内 eFuse summary 仍然是非权威自报证据；本轮只保证其字段不能被畸形值或
status understatement 绕过，不证明 summary 来源、live eFuse 或 bootloader
实际执行。Secure Boot v2 的 signature authenticity、trust root 和
anti-rollback 仍保持 `not-verified`。运行态 ACL/许可、生产 key、真实云端
业务和更多固件族仍是 Backlog。

## 风险与回滚

没有烧录、设备写入、凭据变化或持久迁移。回滚 product commit
`c00fd2eeed4d180931e9390ed80f3e140359ae74` 会恢复旧 manifest policy，并
使本轮 static evidence 与 schema/tool hash 不再匹配；旧 evidence 不应删除
或静默改写。
