# ESP Emulator WebBurner 可恢复固件导入报告

## 背景

- 来源：P0 通用固件审查工作流。
- 现象或需求：resumable chunk API 和 FirmwareManifest CLI 已存在，但浏览器
  没有 package upload → manifest import 的完整入口。
- 目标：完成 WebBurner 页面的流式上传、进度、重试、取消、刷新恢复和
  normalized firmware 创建，并保留 capability/security 边界。

## 根因与设计

缺口不在 manifest parser，而在两层连接：

1. Device Service 没有接受“已上传 package artifact”并运行 importer 的 HTTP
   入口；
2. 浏览器没有流式 SHA256、chunk upload 状态机和 import 展示页。

实现没有引入第二种下游固件格式。package 只用于 import 输入，最终仍发布
content-addressed merged-flash artifact，并由现有 FirmwareStore 创建
flash-sized firmware。

## 改动

### HTTP / Device Service

新增：

```http
POST /api/v1/firmware/import
Content-Type: application/json
```

```json
{
  "device_id": "sticks3",
  "artifact_id": "<package-sha256>"
}
```

支持 artifact 名称后缀：

- `.bin`
- `.zip`
- `.m5burner`
- `.webburner`

服务端将 artifact 复制到 isolated import workspace，调用现有
`import_package()`，执行：

- archive-safe extraction；
- WebBurner/M5Burner/ESP-IDF 导入；
- segment composition/padding；
- static review、security metadata 和 filesystem inventory；
- target capability check；
- normalized merged artifact publication；
- manifest_id 重算和 FirmwareStore 创建。

失败 package 返回 `400 invalid_firmware_package`；capability 不足返回
`409 unsupported_firmware_capability` 和 `issues[]`。

### Browser

新增 `/platform/web/firmware.html` 及：

- `firmware-upload.js`：chunk upload、retry、checkpoint、abort 和 API client；
- `sha256.js`：增量 SHA-256；
- `firmware.js`：页面状态、进度、manifest 展示、刷新恢复和 session 创建；
- `firmware.css`：M5Stack 风格页面。

浏览器完整 SHA256 使用 4 MiB 读取窗口；chunk 上传同样为 4 MiB。
Indexed/local browser state 只保存 upload ID、预期 size/hash、artifact 和
firmware/session ID，不保存固件内容。

刷新恢复规则：

- upload 已完成：读取服务端 artifact，无需重新上传；
- upload 未完成：重新选择同名同大小文件，浏览器重新计算 SHA256 并校验
  expected hash，然后从服务端 `received_bytes` 继续；
- cancel：abort 当前请求并 DELETE upload，服务端返回 404 表示 staging 已清理。

## 执行与证据

### 自动化

```text
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
Ran 253 tests
OK

npm run test:units
SHA256_OK
FIRMWARE_UPLOAD_OK

runtime_coverage.py --check       RUNTIME_COVERAGE_OK
peripheral_catalog.py --check     PERIPHERAL_CATALOG_OK
qemu_profiles.py --check          QEMU_PROFILES_OK
OpenAPI parse                     PASS (3.1.0 / 1.13.0 / 38 paths)
```

GitHub Actions `40022859936`：

```text
platform-contracts           success
network-namespace-policy     success
Ran 253 tests
OK (skipped=2)
SHA256_OK
FIRMWARE_UPLOAD_OK
```

### 真实浏览器

输入包：

```text
size: 9441052 bytes
source sha256: 39c02eae0969b8bd0876976413193d84b3554ff7bf8fce5bd402ad652b4e08c3
chunks: 3
source format: web-manifest
```

结果：

```text
normalized flash: 8388608 bytes
normalized from: segmented-flash
manifest validation: PASS
page errors: 0
```

刷新恢复探针：

- 第一次 import 被故意强制返回 500；
- upload 已 completed，artifact ID 保留；
- 刷新页面后不选择文件，直接继续 import；
- firmware ID 与后续成功运行一致。

取消探针：

- 3 chunk 包在第一个 chunk 后取消；
- 上传状态查询返回 404；
- browser checkpoint 清空；
- UI 显示 staging 已清理。

## 当前工作顺序

- 已完成：`FW-04` package import/browser intake；
- 下一步：`FW-01` SPIFFS/权限/许可、`FW-03` 跨厂商语料、`FW-02` 真机安全；
- 另一条 P0：Core2 `HCI-3b → HCI-4`；
- 网络：`NET-03` fabric、`NET-04` worker、`NET-05` IPv6。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compile、Node syntax、OpenAPI parse |
| transport | `PASS` | browser chunk → Device Service HTTP |
| data_behavior | `PASS` | normalized hash、manifest、capability 和 cancellation cleanup |
| visual | `PASS` | Chromium WebBurner 页面、进度和 manifest cards；无 page error |
| virtual device boot | `NOT RUN` | 合成镜像未作为应用运行 |
| physical | `NOT RUN` | 无真机测量 |

## 风险与回滚

- package import 仍是 trusted-local 服务能力，不是恶意固件 VM 沙箱；
- refresh 后未完成上传必须重新选择文件，这是浏览器安全模型和内容校验要求；
- import 为同步 HTTP 操作，大包静态审查会占用请求时长；
- 回滚源码提交 `9aa3fd71e9ad0b0002cd3e06f4e12038a833d703` 可移除新入口；
- 未执行物理烧录、擦除或 OTA。
