# ESP Emulator 声明级固件许可策略报告

## 背景

FirmwareManifest 已经能解析 provenance、文件系统 SPDX 和 SBOM，但此前这些
许可声明只作为描述字段存在，没有形成可执行的 allowlist/denylist 决策。
简单搜索 `MIT` 或 `GPL` 文本也不能证明法律合规。

本次目标是把可观察声明变成可审计策略，同时明确证据边界。

## 实现

### Manifest

新增可选 `license_policy`：

```json
{
  "schema_version": 1,
  "status": "PASS",
  "decision": "allowlisted",
  "allowed_licenses": ["MIT"],
  "denied_licenses": [],
  "discovered_licenses": ["MIT"],
  "sources": [{"source": "filesystem:storage", "license": "MIT"}],
  "findings": [],
  "coverage": {},
  "limits": []
}
```

`sources` 保留 provenance、filesystem 和 SBOM 来源；声明先去空、去重并保留
规范化显示值。`manifest_id` 包含策略结果。

### CLI

```bash
python3 platform/tools/firmware_manifest.py firmware.bin \
  --out-dir /tmp/m5-firmware \
  --allow-license MIT \
  --allow-license Apache-2.0 \
  --deny-license GPL-3.0-only
```

### 状态机

| 条件 | license_policy | Manifest validation |
| --- | --- | --- |
| allowlist 存在且所有声明匹配、无需人工确认 | `PASS` | 可保持 `PASS` |
| denylist 命中或声明不在 allowlist | `REJECTED` | `errors` + `REJECTED` |
| 无 allowlist、无声明、`NONE`/`NOASSERTION`/`unknown` | `REVIEW_REQUIRED` | warning |

结构校验还要求：

- `license_policy.schema_version=1`；
- 列表和 coverage 类型正确；
- policy 为 `REJECTED` 时 Manifest validation 必须同步为 `REJECTED`。

## 验证

```text
allowlisted MIT + Apache-2.0             PASS
denylisted GPL-3.0-only                 REJECTED
no allowlist                            REVIEW_REQUIRED
no declarations                         REVIEW_REQUIRED
SPIFFS BSD-3-Clause allowlist import    PASS
manifest schema/type validation          PASS
platform tests                           272/272 PASS
GitHub Actions 40047172520               PASS
```

## 边界

- 只评估包内声明，不证明声明真实、完整或适用于所有文件；
- 不进行版权归属或源码级依赖分析；
- 不提供法律意见；
- 文件系统权限仍为 `not-recorded`；
- 不使用真机 secure boot、eFuse 或 key 证据。

## 风险与回滚

回滚源码 `21d26c93055a65b9952a3d5611838bcbb3f2dc10` 会移除
`license_policy`、CLI 参数和对应测试；不会改写已生成的镜像或物理设备。
