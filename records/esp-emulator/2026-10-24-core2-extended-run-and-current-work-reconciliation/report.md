# ESP Emulator 当前工作、代码文档与 Core2 extended-run 对账报告

## 背景

- 来源：用户要求完整整理 ESP Emulator 的代码和文档，并梳理当前已完成工作
  与后续待办。
- 现象或需求：多份入口已经记录网络、worker、FirmwareManifest 和 Core2
  native-HCI 的后续成果，但仍存在过期描述；同时最近的 Core2 hold/extended
  run 没有进入状态页、Backlog 和证据台账。
- 目标：以当前代码、生成物和最新运行证据为准，收敛文档事实，并让长稳失败
  可复现、可追踪、不会被 `HCI-4 5/5` 覆盖。

## 结论

- 文档/契约/CI：`PASS`。
- Core2 extended-run/soak：`FAIL`，根因未定位。
- `HCI-4` 的五个独立 `/api/v1` lease 仍是有效的功能基线，不因后续长稳失败
  被删除或改写。
- 总体记录状态为 `PARTIAL`：整理工作完成，但项目当前最重要的 Core2 长稳
  边界仍有真实失败。

## 代码改动

### Core2 runner

`tests/uiflow2/core2_native_hci/run_service_5x.py` 新增：

- `--hold-seconds`，每轮在 network evidence 后保持 guest 运行并轮询状态；
- 先等待 session 真正进入 `running`，避免把 booting 误判为 hold 失败；
- 失败时不直接冒泡，而是继续收集 session、frame、QOM、
  serial、BLE peer、pcap 和 partial evidence；
- 从 serial 提取 panic kind、PC、EXCCAUSE 和关键 marker；
- 从 BLE peer log 区分 GATT timeout 与 notification timeout；
- aggregate JSON 写入 requested/completed/passed/failed、首个失败阶段和
  failure diagnostics；
- 失败 session 停止后再次尝试抓取历史 evidence，避免 running 状态下的
  evidence 500 导致证据丢失。

### 文档与设备档案

- `README.md`、`docs/project-status.md`、`docs/workstreams.md` 和
  `docs/project-backlog.md` 明确区分 `HCI-4 functional PASS` 与
  `CORE2-02 extended-run FAIL`；
- `docs/validation-ledger.md` 追加失败 evidence；
- `docs/core2-native-hci-backend.md` 增加 extended-run 状态、复现边界和
  验收条件；
- `docs/unified-device-runtime.md`、网络方案、API 当前限制、平台入口和
  runner README 同步同一事实；
- `devices/catalog.source.json` 更新后通过生成器刷新 Core2 的
  `device.json`、`firmware.json`、`README.md` 和 catalog；
- `docs/simulator-service-architecture.md` 删除已过期的“remote worker
  directory / durable queue / active QEMU reattach 未实现”描述；
- `docs/firmware-review-and-simulation-workflow.md` 不再把同主机 executor
  当成待办；
- `platform/tests/test_docs_consistency.py` 增加失败 evidence 的 schema、
  task、panic 和文档回归断言；
- 修正 Markdown 表格列数、Ruff 报告和脚本 shebang/mode 不一致。

## Core2 观察

### 功能基线

历史 `HCI-4` evidence 中，五个独立 lease 均通过：

- 320x240 frame；
- 27 节点 QOM；
- WiFi DHCP/HTTP；
- 公网 DNS/HTTP；
- 外部 Bumble NUS GATT；
- pcap；
- session-bound evidence ZIP；
- `gdb_bridge=false`。

### extended-run 失败

三次独立失败观察：

1. 10-attempt / 10-second hold run 连续通过 3 次，attempt 4 在 READY 前
   `InstrFetchProhibited`、`PC=0`；
2. 单 attempt 的失败先观察到 `IllegalInstruction` at `0x40266960`，
   符号化为 `semphr_give_wrapper`
   (`components/bt/controller/esp32/bt.c:677`)；随后
   `InstrFetchProhibited`、`PC=0`、`EXCCAUSE=0x14` reboot loop；
3. 最终 single-lease smoke 再次在 READY 前 `PC=0` panic。

共同范围：

- WiFi association、受控 HTTP、公网 DNS/HTTP 已 PASS；
- BLE controller 已初始化，peer 已发现/连接；
- 失败发生在 NUS GATT discovery/notification 完成前；
- 失败发生在 `hold_seconds` 被检查前，因此不能归因于“hold 时间过长”；
- 不包含成功 attempt 的自动补跑，不通过 retry 隐藏失败。

当前不能判定：

- 首轮 panic 是 firmware、QEMU HLI/ACL ownership、controller task scheduling
  还是 Bumble teardown 的单一根因；
- 是否与物理 cache/PSRAM 等价性有关；
- 是否具备 bit-exact ESP32 BT baseband/controller 行为。

## 当前工作表

| 工作流 | 已交付 | 仍开放 |
| --- | --- | --- |
| 网络单机与隔离 | namespace、controlled DNS、TLS/Host、exact IPv4、veth/NAT、DHCP renewal、pcap、radio/AP 恢复、双 guest fabric | IPv6、跨主机 worker、生产调度 |
| Worker 服务 | 远程目录、durable queue、claim/lease/retry、同主机 HTTP executor、HMAC、PID/QMP verified local reattach | TLS/mTLS、rotation、跨主机 reattach、companion/evidence continuity |
| Core2 | deterministic TCG/icount、OpenMAC WiFi、公网 HTTP、HCI-offload、native-VHCI 诊断、HCI-4 功能基线 | `CORE2-02` extended-run、bit-exact controller、物理等价性、真机 |
| 固件审查 | Manifest、WebBurner、文件系统清单、静态审查、SBOM、license policy | 运行时权限、完整源码级许可、真机 key/eFuse、跨厂商回归 |
| 设备与 UI | 13 台 simulated、Tab5 partial、CardputerZero separate backend | Tab5 P4 数据面、视觉保真、真机 |

## 执行

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
node --test platform/tests/test_sha256.mjs \
  platform/tests/test_firmware_upload.mjs
python3 -m compileall -q platform/tools platform/tests \
  tests/uiflow2/core2_native_hci
ruff check tests/uiflow2/core2_native_hci/run_service_5x.py \
  platform/tests/test_docs_consistency.py
git diff --check
```

Core2 final single-lease smoke：

```bash
python3 tests/uiflow2/core2_native_hci/run_service_5x.py \
  --base-url <controlled-base-url> \
  --image <matching-unified-firmware> \
  --elf <matching-elf> \
  --qemu <patched-qemu> \
  --attempts 1 --hold-seconds 1 --timeout 60 \
  --out-dir /tmp/m5-core2-native-hci-runner-final-smoke
```

结果：runner 正常输出 aggregate `FAIL`，保留 partial evidence，并完成
session stop；没有留下 QEMU 或服务进程。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、Ruff、平台测试 |
| documentation contract | `PASS` | 9 项文档一致性测试、0 个 Markdown 表格列数错误 |
| runtime catalog | `PASS` | runtime coverage、peripheral catalog、QEMU profiles |
| browser upload client | `PASS` | Node SHA256/upload `2/2` |
| CI | `PASS` | `83ad249` 的 CI run `40058746740` 全部 job 成功 |
| Core2 short functional baseline | `PASS` | 历史 `HCI-4` 五 lease evidence，本轮未重跑 |
| Core2 extended-run | `FAIL` | final single-lease smoke 与 `CORE2-02` evidence |
| full peripheral matrix | `NOT RUN` | 本轮为文档/runner 整理 |
| physical hardware | `NOT RUN` | 没有真机执行 |

## 验证边界

- `HCI-4` functional PASS 不等于 soak PASS；
- extended-run FAIL 不等于已经证明物理 cache/PSRAM 缺陷；
- 当前 QEMU/Bumble 路径是 `virtual-device validation`，不是 RF 或真机；
- 文档整理不会自动提升任何设备、外设、控制器或安全结论。

## 风险与回滚

- 没有删除历史 evidence，也没有把失败记录改写成 PASS；
- 没有写入或擦除物理硬件；
- 没有提交固件、ELF、QEMU 二进制、session ID、MAC、内网地址或凭据；
- 回滚源码提交 `83ad2492b1ea95f83071a599fc29490e729b7e13` 可恢复旧文档和
  runner，但会同时移除本次 Core2 失败固化和 current-work 对账。
