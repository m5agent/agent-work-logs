# FirmwareManifest 静态审查报告

## 背景

现有 FirmwareManifest 已覆盖镜像规范化、SoC/Flash/PSRAM/capability mismatch
和安全状态 `unknown`，但静态审查仍缺：

- URL、凭据和私钥材料的结构化输出；
- 高熵编码载荷识别；
- SPDX/CycloneDX SBOM 摘要；
- 将 finding 与兼容性 validation 分层，同时避免把敏感值写进 manifest。

## 实现

### Review 契约

新增 `platform/tools/firmware_static_review.py`，输出：

```json
{
  "schema_version": 1,
  "status": "CLEAN | REVIEW_REQUIRED",
  "coverage": {},
  "urls": [],
  "encoded_blobs": [],
  "findings": [],
  "sbom": {},
  "limits": {}
}
```

Manifest 中的 `review` 保持可选，以兼容旧 v1 客户端；新导入器始终写入。

### 脱敏规则

- URL 不保存 userinfo、query、fragment 或 path 原文；
- host/port 可供审计，URL/path 只提供 SHA256；
- 凭据和私钥 finding 只保存类别、severity、offset 和指纹；
- 高熵块只保存 encoding、entropy、offset、length 和 SHA256；
- `%s`/`%d` 等模板 host 被跳过，非法端口降级为无 port，不让格式化字符串
  中断 manifest 导入。

### SBOM

- SPDX JSON：读取 spec version、packages 数量和 licenseDeclared/
  licenseConcluded；
- CycloneDX JSON：读取 spec version、components 数量和 license id/name；
- 缺失、超限或非法 JSON 分别产生结构化 warning。

### Validation 分层

- 结构、SoC、Flash、PSRAM、capability 和安全模式继续决定
  `validation.status=PASS/REJECTED`；
- 静态 review finding 通过 `validation.warnings` 提醒，
  并以 `review.status=REVIEW_REQUIRED` 单独表示人工复核；
- 缺 SBOM、review limit 触发等情况不会被伪装成恶意行为。

## 真实样本

使用三个现有公开 M5Burner 样本：

| firmware_id | artifact SHA256 | validation | review | URLs | credential findings | blobs |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `1897200000000001693` | `04b522f6…` | PASS | REVIEW_REQUIRED | 22 | 3 | 1 |
| `1897200000000003332` | `30070338…` | PASS | REVIEW_REQUIRED | 0 | 0 | 2 |
| `2108939572843147265` | `d291e77f…` | PASS | REVIEW_REQUIRED | 4 | 3 | 6 |

完整 SHA256、manifest hash 和 coverage 见 evidence。

第一次真实 round-trip 暴露了 URL 模板端口（例如 `:%d`）会让
`urlsplit().port` 抛异常。修复后，此类 URL 降级为无 port 记录；真实样本
继续 PASS。

## 验证

```text
platform tests                 221/221 PASS
firmware static review tests   3/3 PASS
firmware manifest tests        9/9 PASS
fetch integration test        PASS
three public round-trips      PASS
runtime coverage              PASS
peripheral catalog            PASS
QEMU profiles                 PASS
JSON / py_compile             PASS
git diff --check              PASS
```

脱敏扫描：

```text
raw credentials in manifests        0
raw URL queries in manifests        0
encoded blob values in manifests    0
host absolute paths in manifests    0
```

## 边界

静态 finding 是启发式审查，不等于恶意证明。SBOM 存在也不验证版本或
license 真实性。LittleFS/SPIFFS/FAT 内容、敏感文件权限、许可策略、证书链、
生产 eFuse/secure boot key 和真机路径仍未完成。

## 回滚

回滚源码提交 `4dea5236b21d2165e70d34fc0bae70fd8a75a540` 可移除 review
生成、SBOM 摘要和 fetch 集成；旧版无 review 的 manifest 不受影响。
