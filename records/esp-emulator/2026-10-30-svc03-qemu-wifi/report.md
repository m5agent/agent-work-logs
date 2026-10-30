# SVC-03 QEMU WiFi semantic boundary report

## 背景

- 来源：`SVC-03` 继续拆分 `platform/tools/device_service.py`。
- 需求：一次移动一个无状态或有明确语义的边界，保持外部 API 不变。
- 目标：把 QEMU WiFi security parsing 与 runtime env projection 移出主模块，
  并锁定 same-object re-export 和原有安全语义。

## 结论

- 状态：`PASS`。
- 关键判断：两个函数不依赖 session/store/handler 状态，只负责 WiFi 安全参数
  规范化及 QEMU runtime env key/value 投影，适合独立维护。
- 改动范围：新增 `device_service_qemu_wifi.py`；原模块 import 同一组函数。

## 证据

### 代码或配置

```text
moved:
  parse_qemu_wifi_security
  apply_qemu_wifi_environment

preserved:
  open and wpa2-psk validation
  credential normalization and SSID bounds
  unsupported security status/code
  classic ESP32 env projection
  S3-only M5SW_S3_WIFI_TRACE=1 for wpa2-psk
  public symbol identity through device_service.py
```

### 执行

- 环境：macOS arm64；Python 3.12；本地平台测试环境。
- 专向 boundary tests：`4/4 PASS`。
- Device Service：`126/126 PASS`。
- Platform 全量：`1,678` tests，`1,677 PASS + 1 skip`。
- 生成器检查和静态检查均 PASS；PR CI `4/4 PASS`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall 与 Device Service import |
| transport | `NOT RUN` | 本次不启动 network transport |
| device_response | `NOT RUN` | 无设备行为改动 |
| data_behavior | `PASS`（平台契约） | open/WPA2、负控、env projection 和 re-export identity |
| visual_or_physical | `NOT RUN` | 无显示或硬件改动 |

## 验证边界

- 不证明 WiFi 数据面、QEMU controller、session 或 evidence 新行为。
- RF、电气、物理硬件和真机 `NOT RUN`。
- `SVC-03` 整体仍未完成。

## 风险与回滚

风险仅为 import/re-export 或安全参数投影错误，已由 identity、正负控和
env tests 覆盖。回滚可单独 revert PR #61；未执行设备写入、烧录、擦除或
其他不可逆操作。
