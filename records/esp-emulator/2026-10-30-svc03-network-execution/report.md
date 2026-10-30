# SVC-03 network execution parsing boundary report

## 背景

- 来源：`SVC-03` 继续拆分 `platform/tools/device_service.py`。
- 需求：按可回滚边界移动无状态请求解析，保持 HTTP/API 和运行参数不变。
- 目标：把完整 `parse_network_execution` 移出主模块，并锁定原错误码、
  默认值、规范化结果和 public symbol identity。

## 结论

- 状态：`PASS`。
- 关键判断：该 parser 不依赖 session、store、QEMU process 或 handler 状态，
  只依赖设备规格和共享 pure helpers，可独立移动。
- 改动范围：新增 `device_service_network_execution.py`；原模块 import 同一
  函数对象并 re-export。

## 证据

### 代码或配置

```text
moved:
  parse_network_execution

preserved:
  profile defaults and capability checks
  network mode and capture-pcap rejection
  hostfwd and I2C normalization
  WiFi/BLE/TCP booleans and ELF requirements
  PSRAM, marker, credential and port bounds
  returned dictionary and public symbol identity
```

### 执行

- 环境：macOS arm64；Python 3.12；本地平台测试环境。
- 专向 network-execution tests：`4/4 PASS`。
- Device Service：`126/126 PASS`。
- Platform 全量：`1,674` tests，`1,673 PASS + 1 skip`。
- 四个生成器一致性检查和静态检查均 PASS。
- PR CI：`4/4 PASS`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall 与 Device Service import |
| transport | `NOT RUN` | 本次不启动 network transport |
| device_response | `NOT RUN` | 无设备行为改动 |
| data_behavior | `PASS`（平台契约） | 默认值、hostfwd、错误码和 re-export identity 测试 |
| visual_or_physical | `NOT RUN` | 无显示或硬件改动 |

## 验证边界

- 不证明 HTTP handler、network runtime、session、QEMU 或 evidence 新行为。
- network transport、物理硬件、RF、电气和真机 `NOT RUN`。
- `SVC-03` 整体仍未完成。

## 风险与回滚

风险仅为 import/re-export 或 network parser 边界错误，已由 identity、
默认值、负控和 Device Service tests 覆盖。回滚可单独 revert PR #59；
未执行设备写入、烧录、擦除或其他不可逆操作。
