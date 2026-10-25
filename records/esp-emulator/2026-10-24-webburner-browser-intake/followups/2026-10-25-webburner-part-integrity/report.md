# ESP Emulator WebBurner part integrity report

## 背景

WebBurner ZIP 的分段列表通常包含 `path` 和 `offset`。部分包还会声明文件
大小或摘要，但原 importer 只校验路径、偏移、重叠和 Flash 边界，没有验证这些
声明。若单个 part 被替换或损坏，只要偏移仍合法，包仍可能被规范化。

## 实现

`firmware_manifest.py` 新增 `_web_part_integrity()`：

- 支持 `parts[].size`、`sha256`、`sha1`、`md5`；
- 支持同名声明放入 `parts[].integrity`；
- 文件流式复算，不把大文件整体读入内存；
- size 支持十进制或 `0x` 字符串；
- digest 接受大小写十六进制并规范化为小写；
- mismatch、非法 digest、重复声明冲突和未知 integrity 字段直接拒绝；
- 成功 segment 只记录 `status=verified`、算法集合和 `weak_digest`。

`firmware_manifest.schema.json` 和运行时 `validate_manifest_structure()`
同步约束 `declared_integrity`，避免手写 manifest 绕过结构检查。

## 验证

阳性样本：

- 合成 8 MiB 结构镜像拆成 3 个 part；
- 每个 part 声明 size、SHA-256、SHA-1、MD5；
- 3/3 segment 复算通过并写入 verified 元数据；
- 完整 manifest structure 校验为 PASS。

负向用例：

| 用例 | 结果 | 错误 |
| --- | --- | --- |
| SHA-256 不匹配 | REJECTED | `sha256 mismatch` |
| size 不匹配 | REJECTED | `size mismatch` |
| 非法 SHA-256 | REJECTED | `invalid sha256` |
| 顶层与 integrity SHA-256 冲突 | REJECTED | `conflicting sha256 values` |
| 未知 integrity 字段 | REJECTED | `unsupported integrity fields` |

```text
WebBurner part integrity      PASS
platform contracts           419/419 PASS
documentation contracts      23/23 PASS
compileall                   PASS
Ruff fatal checks            PASS
runtime coverage              PASS
peripheral catalog            PASS
QEMU profiles                 PASS
project snapshot              PASS
git diff --check              PASS
GitHub Actions 40151571675    PASS
```

## 证据分层

- 可以证明：声明值是否与本地包内 bytes 一致；
- 不能证明：谁发布这些 bytes、是否由可信 key 签名；
- 不能证明：partition flag 或镜像声明的安全状态是否真的执行；
- 不能证明：boot、网络、外设、RF、功耗或物理硬件行为。

SHA-1/MD5 会被标记为弱摘要；即使同时存在强 SHA-256，也不把弱摘要升级为
签名或认证。

## 回滚

回滚 `10df26ece0b605a3a8bb36a3661b53494fdae9a0` 即可恢复只校验
`path`/`offset` 的上一版行为。该改动没有关键数据迁移，也没有物理设备状态。
