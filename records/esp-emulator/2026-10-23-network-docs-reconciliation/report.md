# ESP Emulator Host Allowlist Fixture 与文档对账报告

## 背景

项目近期连续加入统一 QEMU runtime、Core2 native-VHCI、网络 namespace、
FirmwareManifest 和热门固件矩阵。主入口虽然已经有过两轮整理，但继续核查后
仍存在以下漂移：

- README 和项目状态页仍记录 `221` 个平台测试；
- Device Service 新加入的 allowlist 配置没有进入 OpenAPI；
- Core2 native-VHCI 文档同时存在“未进入 unified lease/Device Service”和
  “已经进入并完成 lease”的矛盾描述；
- StickS3 UI 页面仍停留在“首帧黑屏 WIP”；
- Core2 OpenMAC 页面仍写默认重试五次和“启动 panic 仍间歇”，与后来
  deterministic TCG/icount、零重试首轮证据不一致；
- TLS/Host allowlist 已有工作树接线，但没有实际判定和明确 blocker。

目标是把代码、契约、当前状态、专项文档和待办重新对齐，同时给未完成的 TLS
路径留下可复现证据。

## 改动

### Device Service 与网络 fixture

- `network.policy.egress` 增加 `allowlist`；
- `allowed_hosts` 必须是 1–32 个规范化 Host；
- 只允许带受控 HTTP fixture 的 profile 使用 allowlist，其他 profile 返回
  `allowlist_not_supported`；
- allowlist 只过滤受控 gateway 的 HTTP `Host`，不声称是目标 IP/端口级别的
  通用 egress allowlist；
- `ControlledHttp` 支持 TLS、Host 允许/拒绝日志和 200/403 决策；
- isolation evidence 记录 policy、allowed hosts 和 TLS gateway 状态；
- Device Service Markdown 与 OpenAPI 升级到 `1.8.0`。

### TLS fixture

新增 ESP32-S3 UIFlow2 fixture：

1. guest 加入 QEMU 虚拟 AP 并取得 DHCP；
2. 载入临时生成的测试 CA；
3. 通过 namespace-capable HTTPS gateway 发起允许和拒绝请求；
4. 要求允许 Host 返回 200、拒绝 Host 返回 403；
5. 保留请求决策、pcap 和结构化 evidence。

证书和私钥仅在临时目录生成，不进入仓库。

### 文档与防漂移

- README、项目状态、Backlog、网络方案、诊断 lane、服务架构和代码地图同步；
- `docs/README.md` 登记 TLS fixture；
- 修正 Core2 native-VHCI、StickS3 UI 和 Core2 OpenMAC 的旧结论；
- `test_docs_consistency.py` 增加 TLS evidence、API allowlist 字段和更多旧陈述
  检查；
- `core2_openmac_wifi` 默认改为单次 attempt，诊断重复必须显式指定。

## 执行

环境为 macOS Apple Silicon，使用仓库现有 QEMU 与 StickS3 UIFlow2 缓存镜像。

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'

python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check

PYTHONPATH=.work/py python3 tests/network/tls_allowlist/run_test.py \
  --qemu .work/M5StopWatch-QEMU/build/qemu/build/qemu-system-xtensa \
  --rom-dir .work/M5StopWatch-QEMU/build/qemu/pc-bios \
  --out-dir <temporary-directory> \
  --timeout 45
```

平台与契约检查全部通过。TLS fixture 返回 `FAIL`。

## TLS 执行时间线

1. 第一次运行包含一个无关的 `esp.random()` 探针；guest 在该调用后停住，
   尚未进入 TLS。该探针被移除。
2. 第二次运行完成 WiFi/DHCP、测试 CA DER 解码，然后停在
   `ssl.SSLContext(...)` 创建。
3. QEMU 同步输出 `[AES] Error reading from GDMA buffer`。
4. pcap 中存在 DHCP/DNS 等 guest 背景流量，但没有 TLS gateway 的连接，
   请求决策日志为空。

结论是当前 blocker 位于 TLS context 创建之前的 ESP32-S3 AES/GDMA 数据面，
而不是 HTTPS gateway 的允许/拒绝逻辑。该判断仍需在修复 AES/GDMA 后用同一
fixture 复测确认。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | UIFlow2 TLS probe image 构建成功 |
| transport | PARTIAL | WiFi 关联和 DHCP 成功；TLS TCP 未发出 |
| device_response | FAIL | `ssl.SSLContext` 未返回，AES/GDMA read error |
| data_behavior | FAIL | 允许/拒绝请求和 Host 决策未执行 |
| review | PASS | 文档、OpenAPI、代码地图与当前实现对齐 |
| visual_or_physical | NOT RUN | 本轮不验证真机显示、RF 或电气行为 |

## 验证边界

- 记录的 TLS QEMU 运行使用 trusted-host，不是已完成的 Linux namespace 运行；
- Host allowlist fixture 不能证明任意公网 destination allowlist；
- TLS fixture 的 gateway 单测通过，不替代 ESP32-S3 guest TLS；
- 本轮未修改共享 QEMU 板级控制器，因此没有重复运行 20–30 分钟全矩阵；
  最近 `67/67`、`274/274` 结果仍作为未改控制器代码的功能基线；
- 没有物理 M5Stack 设备证据。

## 风险与回滚

源码回滚点为 `4dea5236b21d2165e70d34fc0bae70fd8a75a540`。回滚
`dd705e8b8dfdb3bab927e9f4d1a7561a684466bc` 会移除 allowlist 契约、TLS
fixture 和本轮文档对账，但不会恢复任何已经证明通过的 TLS 能力，因为该能力
目前并不存在。
