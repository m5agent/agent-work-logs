# ESP Emulator 固件上传可靠性、代码与文档总整理报告

## 背景

- 来源：用户指出主状态页之外的代码和文档仍未完全吸收近期网络、Core2、
  固件审查和 Device Service 工作。
- 现象或需求：需要完整整理代码与文档，明确当前成果、证据级别和待办。
- 目标：先把未提交的 resumable upload backend 收口，再以当前代码、
  generated artifacts、evidence 和测试结果统一口径。

## 结论

- 状态：服务契约、回归和文档层 `PASS`；设备功能与真机不变。
- 关键判断：文档漂移主要有四类：
  1. 测试数、CI run 和源码行数被写成易漂移的当前事实；
  2. `platform/README.md` 仍把已经通过的 `HCI-3a` 混在未完成的
     `HCI-3` 中；
  3. 网络 CI 与双设备 fabric 被放在同一个 `IN PROGRESS` 格里；
  4. resumable upload 只有 happy path，缺少失败回滚和 staging GC。
- 改动范围：Device Service、HTTP API、OpenAPI、上传证据、平台测试，
  以及状态、Backlog、工作流、代码地图、网络和专项文档。

## 代码改动

### Resumable upload

- staging 文件以 `r+b` 从已确认 offset 追加；
- 写入长度、`fsync` 和 metadata 提交任一失败，都截断回原 offset；
- upload metadata 使用临时文件加原子 replace；
- 增加 `upload_write_failed` 和 `upload_rollback_failed` 错误边界；
- `DELETE` 清理 abort，storage janitor 按 grace period 清理：
  - 中断的 `.part/.json`；
  - 无 metadata 的孤立 `.part`；
  - 临时 metadata 文件；
  - 过期的 completed upload 记录。

### HTTP / OpenAPI

新增并测试：

```text
POST   /api/v1/artifact-uploads
GET    /api/v1/artifact-uploads/{id}
POST   /api/v1/artifact-uploads/{id}/chunks
POST   /api/v1/artifact-uploads/{id}/complete
DELETE /api/v1/artifact-uploads/{id}
```

请求体限制为 `8 MiB/chunk`，最终 artifact 上限保持 `96 MiB`。
API 从 `1.11.0` 升为 `1.12.0`。

### 测试

- 两个 chunk 的 service round-trip；
- HTTP create、chunk、GET resume、complete、metadata 和 abort；
- 错误 offset；
- chunk hash mismatch；
- incomplete complete；
- final SHA256 mismatch；
- oversized chunk；
- simulated `fsync` failure 后回滚；
- abandoned staging GC。

## 文档对账

- `README.md`：更新平台测试快照、上传证据和 staging GC；
- `docs/README.md`：更新文档新鲜度和三组 P0 的实际位置；
- `docs/project-status.md`：新增“能力成熟度”，分开虚拟验证、服务化和真机；
- `docs/project-backlog.md`：`FW-04` 改为 backend 已通过，剩余 Web UI；
- `docs/workstreams.md`：同步固件上传和 Device Service 的真实边界；
- `docs/code-map.md`：移除易漂移行数，增加 upload 运行链和证据入口；
- `docs/device-service-api.md` 与 OpenAPI：记录 rollback、GC 和错误语义；
- `docs/network-simulation-plan.md`：拆开 Linux policy CI（DONE）和双设备
  fabric（OPEN），补充 Core2 native-HCI 阶段；
- `platform/README.md`：明确 `HCI-3a PASS`、`HCI-3b/HCI-4 OPEN`；
- 文档一致性门禁增加动态测试计数、上传证据检查和旧计数/旧行数拒绝项。

## 执行与证据

本机：

```text
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
Ran 249 tests in 8.339s
OK

runtime_coverage.py --check       RUNTIME_COVERAGE_OK
peripheral_catalog.py --check     PERIPHERAL_CATALOG_OK
qemu_profiles.py --check          QEMU_PROFILES_OK
OpenAPI parse                     PASS (3.1.0 / 1.12.0 / 37 paths)
git diff --check                  PASS
```

GitHub Actions `40021209492`：

```text
platform-contracts           success
network-namespace-policy     success
Ran 249 tests in 12.599s
OK (skipped=2)
```

## 当前工作与待办

| 工作流 | 当前已形成的能力 | 下一道门禁 |
| --- | --- | --- |
| 网络 | namespace、DNS/TLS allowlist、exact IPv4 egress、pcap、错误密码、radio/AP 恢复、DHCP renewal、Linux CI | `NET-03` 双设备 fabric、`NET-04` QEMU worker、`NET-05` IPv6 |
| Core2 | deterministic TCG/icount、OpenMAC WiFi、公网、GDB native-VHCI 单 lease、`HCI-3a` 5/5 | `HCI-3b` 完整 HCI/GATT、`HCI-4` repeated lease、移除 GDB 控制面 |
| 固件 | Manifest、静态/security、LittleFS/FAT、resumable upload backend | WebBurner UI、SPIFFS、权限/许可、跨厂商样本、真机 eFuse |
| Device Service | lease、存储、GC、历史恢复、容量、evidence | worker 生命周期、活动进程接管、warm pool、多机调度 |
| 真机 | 无 | `HW-01` 同固件 SHA、同测试计划 |

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compile、OpenAPI parse、平台测试 |
| transport | `PASS` | chunk HTTP round-trip、resume、complete、abort |
| device_response | `NOT RUN` | 本次没有启动新的设备会话 |
| data_behavior | `PARTIAL` | 上传与 GC 数据面 PASS；设备数据面沿用既有证据 |
| visual_or_physical | `NOT RUN` | 没有重跑 UI 或物理设备 |
| review | `PASS` | 文档、链接、API、Task ID 和旧状态门禁 |
| delivery | `PASS` | 源码、CI 和公开工作记录 |

## 验证边界

- 本次没有修改 QEMU 控制器或设备探针，因此没有重跑 67-case 全矩阵；
- resumable backend 通过不等于 WebBurner 页面已接入；
- Core2 `HCI-3a` 单包 callback PASS 不等于完整 BLE controller/GATT；
- Linux namespace/egress PASS 不等于恶意固件 VM 或 RF 模型；
- 所有结果都是 virtual-device/static evidence，不是物理硬件测量。

## 风险与回滚

- 未执行烧录、擦除、OTA 或物理设备操作；
- 风险集中在上传 staging 状态机和文档门禁；
- 回滚源码提交 `0ffaf07b334a09690e2ad62b23078c04ea8b134c` 可恢复旧
  backend 与文档，不影响既有 QEMU、固件、网络策略或会话历史。
