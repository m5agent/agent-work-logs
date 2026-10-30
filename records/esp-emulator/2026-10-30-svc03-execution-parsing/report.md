# SVC-03 storage/NVS parsing boundary report

## 背景

- 来源：`SVC-03` 持续拆分 `platform/tools/device_service.py`。
- 需求：一次只移动一个无状态边界，保持 `/api/v1`、错误码、返回结构和
  public symbol identity 不变。
- 目标：把 storage/NVS execution request parser 移出编排主模块，并增加
  same-object re-export 与 fail-closed 契约。

## 结论

- 状态：`PASS`。
- 根因或关键判断：`parse_storage_execution` 与 `parse_nvs_execution`
  只依赖 `ServiceError`、SHA256 validator 和 `DeviceSpec`，无 session、
  store、runtime 或 HTTP handler 状态，是可独立移动的无状态边界。
- 改动范围：新增 `device_service_execution_parsing.py`，搬迁两个函数；
  `device_service.py` 直接 import 并以同一对象 re-export。

## 证据

### 代码或配置

```text
moved:
  parse_storage_execution
  parse_nvs_execution

preserved:
  invalid_storage / storage_not_supported codes and statuses
  invalid_nvs code and status
  unknown-field rejection
  SD capability check
  NVS partition-label bounds
  returned dictionaries
  public symbol identity through device_service.py
```

### 执行

- 环境：macOS arm64；Python 3.12；本地平台测试环境。
- 专向测试：`5/5 PASS`。
- Device Service：`126/126 PASS`。
- Platform 全量：`1,670` tests，`1,669 PASS + 1 skip`。
- 四个生成器检查和静态检查均 PASS。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall 与 Device Service import |
| transport | `NOT RUN` | 本次不启动 QEMU 或网络 transport |
| device_response | `NOT RUN` | 无设备行为改动 |
| data_behavior | `PASS`（平台契约） | parser 输入/输出、错误码和 re-export identity 测试 |
| visual_or_physical | `NOT RUN` | 无显示或硬件改动 |

## 验证边界

- 不证明 API handler、session、QEMU 或 evidence 新行为；本次不改变这些路径。
- 物理硬件、RF、电气和真机 `NOT RUN`。
- `SVC-03` 整体仍未完成。

## 风险与回滚

风险仅为 import/re-export 或 parser 边界错误，已由 identity、异常和
Device Service tests 覆盖。回滚可单独 revert PR #58；未执行设备写入、
烧录、擦除或其他不可逆操作。
