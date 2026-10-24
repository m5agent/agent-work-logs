# ESP Emulator required/optional capability consistency report

## 背景

FirmwareManifest 已支持 required 和 optional capability 数组，但两套声明
分别归一化，存在三个缺口：

1. 同一 capability 可同时出现在 required 和 optional；
2. 旧 manifest structure validation 不检查该重叠；
3. optional capability 不匹配没有结构化结果。

这会让调用者误以为 optional mismatch 会阻止启动，或让矛盾声明静默通过。

## 实现

### Importer

- 分别规范化和去重 required/optional；
- 计算两者交集；
- 交集非空时抛出 `ManifestError`：
  `capabilities cannot be both required and optional: ...`。

### Manifest structure

- required/optional 允许 alias，但在比较前统一规范化；
- 交集非空时记录
  `manifest.capabilities.required and optional overlap`。

### Compatibility

- required 未知：`unknown_required_capability` warning；
- required 不支持：`unsupported_capability` error，manifest `REJECTED`；
- optional 未知：`unknown_optional_capability` warning；
- optional 不支持：`unsupported_optional_capability` warning，manifest `PASS`；
- detected capability 行为保持不变：compiled-in flag 只 warning。

## 验证

使用静态合成 ESP32-S3 flash 和 StickS3 profile：

```text
required wifi + camera + unknown     -> REJECTED, required error + warnings
required wifi + optional camera      -> PASS, optional warning
required wifi + optional WIFI alias  -> ManifestError overlap
manifest required wifi + optional WIFI -> structure validation error
```

结果：

```text
FirmwareManifest 22/22 PASS
documentation consistency 19/19 PASS
platform suite 350/350 PASS
```

## 验证边界

- 只验证静态 Manifest 声明与设备 profile 的兼容性。
- 不证明二进制代码实际调用、链接或执行 optional capability。
- 不替代 guest runtime、外设数据面或物理硬件验证。

## 风险与回滚

本轮无不可逆操作。回退源码提交
`6e2e7693f8b5edf787d49ecb709bdc00acaaa7f0`。
