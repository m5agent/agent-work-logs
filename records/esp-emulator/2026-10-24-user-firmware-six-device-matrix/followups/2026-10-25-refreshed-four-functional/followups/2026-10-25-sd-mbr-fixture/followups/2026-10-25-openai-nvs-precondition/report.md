# ESP Emulator OpenAI NVS 前置条件与状态文档重整报告

## 背景

公开 OpenAI Voice Assistant 在通用 Device Service session 中持续黑屏。
上一轮 SD fixture 已让同一批四个公开样本达到
`3 PASS / 1 PARTIAL / 0 FAIL`，但 OpenAI 样本仍缺少可解释的首次启动数据。

本轮目标：

1. 判定黑屏属于固件缺陷、display/NVS controller 缺陷，还是外部运行时前置条件；
2. 用 guest 实际读取的 partition/NVS 数据面复现和对照；
3. 把结果回写到当前状态、Backlog、验证台账、API 和代码地图；
4. 明确后续 P0 工作，不只优化这一份固件。

## 根因

公开 BIN 的 `data/nvs` 分区为：

- label：`nvs`；
- offset：`0x9000`；
- size：`0x6000`（24 KiB）；
- 全部字节：`FF`。

应用读取 `config/wifi_ssid`、`config/wifi_password` 和
`config/openaikey`。缺少这些项时，固件输出
`main: Failed to load user data` 和
`main_task: Returned from app_main()`，没有进入后续联网或 UI 路径。

因此空 NVS 是确认的外部首次启动配置前置条件。它不能直接证明 display、
通用 NVS controller 或 firmware WiFi 路径失败。

## 改动

### NVS fixture

`platform/tools/nvs_image.py` 生成确定性的 NVSv2 page、namespace 和 string
entries。支持范围只覆盖当前审查所需的字符串配置；编码结果与 ESP-IDF
`nvs-partition-gen 0.3.0` 对照。两种 fixture：

- Open auth：空 `wifi_password`；
- WPA2：非空 `wifi_password`。

Device Service 新增请求：

```json
{
  "nvs": {
    "partition_label": "nvs",
    "image_artifact_id": "<fixture-sha256>"
  }
}
```

服务行为：

1. 解析 firmware partition table；
2. 只匹配 `type=data/subtype=nvs` 且 label 相同的分区；
3. fixture 大小必须严格等于 partition size；
4. 只写 session-isolated Flash 副本；
5. 记录 source/normalized/base/effective Flash SHA 和 fixture SHA；
6. retry 前恢复 clean flash，再应用同一 fixture；
7. evidence ZIP 包含 `nvs/summary.json`。

该字段只接受 `qemu`、`qemu-wifi`、`qemu-ble` 和 `qemu-unified`。
`runtime=network` 和 Tab5 不执行同一条 guest Flash 路径，返回
`409 nvs_not_supported`，避免静默忽略。

### Generic S3 WiFi observe

`runtime=qemu-wifi/profile=generic-observe` 现在可用于任意 QEMU ESP32-S3。
它运行完整 compatible image 和 S3 WiFi NIC，不要求 UIFlow/HCI marker、
UI frame 或 BLE。它适合 headless/network-first 固件，但不能替代
`qemu-unified` 的 board + WiFi + BLE 验收。

### 文档重整

本轮同步了：

- `project-status.md`、`project-backlog.md`、`workstreams.md`；
- `validation-ledger.md`、`runtime-model-gap-register.md`；
- `device-service-api.md`、OpenAPI 和固件审查工作流；
- `code-map.md`、热门用户固件矩阵、README 和自动项目快照；
- `test_docs_consistency.py`，锁定 NVS runtime 边界、OpenAI 对照和
  `RUNTIME-05`。

## 对照结果

### Open fixture

guest 输出：

- `NVS: WiFi SSID: myssid`；
- `wifi:connected with myssid`；
- `got ip:`；
- HTTPS request 失败，因为使用的是 synthetic key。

网络证据：

- status `PASS`；
- `37` packets；
- DNS query `api.openai.com.`；
- TCP/443 flow 数量 `1`；
- pcap SHA256
  `ab8c5f61077634b7de136e91ea96539c9fb4503ee90a33821058af823edd4295`。

### WPA2 fixture against current Open-auth QEMU AP

guest 输出：

- NVS config 已读取；
- `authmode threshold changes from OPEN to WPA2`；
- 未出现 `wifi:connected with myssid`；
- 未获得 DHCP。

当前 QEMU S3 AP 只广告 Open auth，没有 WPA2/RSN、EAPOL/4-way 和密码验证
数据面。因此该路径分类为 `RUNTIME-05/runtime_model_gap`，不是该固件的
WiFi FAIL。

## 当前工作状态

### 已经有同路径虚拟设备证据

- 14 台登记设备，13 台可由 Device Service 创建；
- S3/C6/Core2 单 guest 板级、WiFi 和 BLE/HCI 路径；
- Core2 native-HCI 多轮重连、active-BLE 两小时和 bounded TCG；
- Linux namespace、controlled DNS、TLS/Host、exact IPv4/IPv6 egress、
  pcap、错误密码、断线重连、双 guest lab fabric；
- worker queue、HMAC、HTTPS/mTLS、rotation/drain、同主机 reattach 和
  worker namespace-local QEMU；
- FirmwareManifest、WebBurner、capability mismatch、静态/SBOM、文件系统和
  session-isolated SD/NVS fixture。

### 仍未完成

- `NET-04` / `SVC-01`：物理跨主机 QEMU executor、worker 自动发现、跨主机
  reattach、companion/evidence continuity、生产多机调度和恶意固件隔离；
- `CORE2-02`：物理 cache/PSRAM、bit-exact BT controller/baseband、
  吞吐/teardown 和真机；
- `FW-01`：运行态 ACL/权限、完整许可与法律审批；
- `FW-02`：真机 secure boot、Flash Encryption、eFuse 和生产 key 流程；
- `FW-03`：headless/cloud 执行预期、更多设备和 firmware family；
- `RUNTIME-02`：C6 Zigbee commissioning；
- `RUNTIME-03`：Core2 legacy I2C controller/board-bus routing；
- `RUNTIME-04`：Core2 for AWS ATECC608；
- `RUNTIME-05`：S3 AP WPA2/RSN、EAPOL/4-way 和正确/错误密码；
- `HW-01`：代表设备同固件 SHA 的 physical hardware validation；
- P1：`SVC-02/03`、`TAB5-01`、`UI-01`、`CZ-01`。

CIDR/domain-set、真实公网任意目标、RF/PHY、功耗、光学、声学、机械和电气
等价性仍不在这组证据范围内。

## 验证

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall、376 项平台测试全部导入通过 |
| transport | `PASS` | QEMU guest 串口、DHCP、controlled DNS 和 TCP/443 pcap |
| device_response | `PASS` | NVS 编码/分区校验、session overlay、flash SHA 和 evidence ZIP |
| data_behavior | `PASS` | 同一 BIN 的 Open/WPA2 fixture 产生不同 authmode 与关联结果 |
| visual_or_physical | `NOT RUN` | 该固件无可用前置配置 UI；未接物理硬件 |

命令：

```text
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
python3 -m compileall -q platform/tools platform/tests \
  tests/firmware/openai_nvs_precondition
ruff check --select E9,F,I <changed Python files>
git diff --check
```

结果：

- platform tests：`376/376 PASS`；
- documentation contracts：`20/20 PASS`；
- Node：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`；
- compileall、selected Ruff、diff check：`PASS`；
- CI run `40132242654`：两个 job 均 `PASS`。

## 验证边界

- 本记录不证明真实 OpenAI 账号、Realtime/WebRTC、音频或云端成功；
- synthetic key 只用于证明请求路径到达 HTTPS，不代表认证通过；
- 非空密码对照只证明 `RUNTIME-05` 缺口，不证明物理 WPA2；
- 没有重跑完整 67-case UIFlow2 外设矩阵，因为本轮没有修改共享外设控制器；
- 没有物理硬件、RF、功耗、声学、光学或电气测量；
- QEMU/Device Service 清理已检查，无残留执行进程或 namespace。

## 风险与回滚

回滚源码提交 `3f4bf92b96d5854f0804d7f7014c4a9c244da99e` 会移除 NVS
fixture API、generic S3 observe 扩展和当前文档对账；不会修改用户上传的
firmware、NVS artifact 或外部运行环境。

回滚后需要重新验证 Device Service API、OpenAPI、项目快照和文档契约。
