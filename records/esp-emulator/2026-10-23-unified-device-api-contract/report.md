# Device Service 单实例 API 契约统一报告

## 背景

设备中心已经有单租约、单固件、单 QEMU guest 的 unified profile，但对外
契约仍有三个问题：

1. OpenAPI 的 `Session.runtime` 和 `/logs.runtime` 只允许
   `qemu|network`，与实际的 `qemu-wifi|qemu-ble` 返回值不一致；
2. `qemu-ble` 同时承担 unified 整机入口和无线电专用诊断，名称无法表达
   “完整模拟设备”；
3. `/network` 被描述成 network lane evidence，但 unified session 返回的是
   同一 guest 的 radio slice，frame、input、QOM、PCM 等仍属于同一会话。

## 统一后的契约

| Runtime | 用途 | 整机证据 |
| --- | --- | --- |
| `qemu-unified` | 正式 board + radio 单实例路径 | profile PASS 时成立 |
| `qemu-wifi` | 同 guest 的 board + WiFi 固件 | 仅 board + WiFi |
| `qemu-ble` | unified 兼容入口及无线电诊断 | 取决于 profile |
| `network` | 独立 `esp-emu` 诊断 | 不含 board、frame、input、QOM |

`qemu-unified` 只接受单 guest unified profile：StickS3、CoreS3、
Cardputer ADV、StopWatch、AtomS3R、PaperColor、PaperMono、StackChan、
StamPLC、Core2 unified，以及 Nesso 的 `nesso-unified`。

## 实现

- 新增内部 runtime 集合，统一处理 QMP、radio、session 恢复和 evidence：
  `QEMU_QMP_RUNTIMES`、`QEMU_RADIO_RUNTIMES`、
  `QEMU_SESSION_RUNTIMES`；
- 新增 `QEMU_UNIFIED_RUNTIME=qemu-unified`；
- 保留 `qemu-ble` 兼容路径；
- `qemu-unified` 配合 radio-only profile 时返回
  `qemu_unified_profile_required`；
- 不支持的设备返回 `qemu_unified_not_supported`；
- `/sessions/{id}/network` 响应改用结构化 `NetworkEvidence` schema；
- OpenAPI 用共享 `RuntimeName` 统一 CreateSession、Session 和 logs 的
  runtime 枚举；
- API 文档从逐设备示例到限制说明统一使用 `qemu-unified`，
  `qemu-ble` 只出现在兼容/无线电专用说明中。

## 验证

```text
OpenAPI version: 1.4.0
RuntimeName: qemu, network, qemu-wifi, qemu-ble, qemu-unified
Session.runtime: $ref RuntimeName
platform unit tests: 172 PASS
runtime coverage: PASS
peripheral catalog: PASS
```

实际 HTTP 请求：

```json
{
  "device_id": "sticks3",
  "runtime": "qemu-unified",
  "network": {
    "profile": "uiflow2-sticks3-wifi"
  }
}
```

返回 HTTP `400`：

```json
{
  "error": {
    "code": "qemu_unified_profile_required",
    "message": "'uiflow2-sticks3-wifi' is a radio-specific profile; runtime=qemu-unified requires a single-guest unified profile"
  }
}
```

有效的 `runtime=qemu-unified` + `uiflow2-sticks3-unified` 请求可进入 session
创建流程；测试使用不完整 reference image，因此按预期在完整 8 MiB Flash
校验处失败，但 runtime/profile 选择本身已被服务接受。

## 兼容性与边界

- 现有 `qemu-ble` 客户端无需迁移；
- 新客户端和文档应默认使用 `qemu-unified`；
- physical hardware、RF、功耗和电气验证仍为 `NOT RUN`；
- 本变更不扩大未支持设备的网络能力，也不把 C6 WiFi、Tab5 缺口改成 PASS。

## 回滚

回滚源码 commit `f2ff7a75b473653ec1440e955c0f42c6b7f22203` 即可恢复
旧 runtime 枚举和 `qemu-ble` 单一入口。
