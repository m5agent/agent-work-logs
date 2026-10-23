# ESP Emulator Core2 native-VHCI ELF 固定符号报告

## 背景

Core2 stock UIFlow2 使用内置 BT controller 构建。为了在没有 bit-exact
controller 的情况下验证真实 firmware/NimBLE 调用路径，现有 bridge 在
`esp_vhci_host_*` 边界把 H2C/C2H 转给 Bumble。

原 bridge 由 GDB 查询三个符号地址。此次目标是：

1. 从上传的匹配 ELF 严格解析地址，缺失、歧义或畸形时不猜测；
2. 把固定地址传给 Device Service 和两个独立 runner；
3. 在 evidence 中记录地址来源；
4. 重新对齐 README、状态、Backlog、代码地图、API/OpenAPI 和专题页；
5. 明确区分“符号查询不再依赖 GDB”和“整个 guest 控制仍依赖 GDB”。

## 改动

### ELF 解析

新增 `platform/tools/xtensa_elf_symbols.py`：

- 校验 ELF32、little-endian、Xtensa machine 和 section table；
- 只接受 function/object 的 local/global/weak symbol；
- 缺失或同值仍然歧义时结构化失败；
- 所有 section span 先与真实文件长度比较，拒绝超大表项读取；
- 支持 CLI `--require` 和 `--json`，用于人工核对。

新增单测覆盖：

- function/object 地址解析；
- missing/ambiguous symbol；
- section 声明长度超过文件大小的 malformed ELF。

真实 UIFlow2 ELF 的解析结果：

```text
API_vhci_host_send_packet   0x403064d8
esp_cpu_wait_for_intr       0x40093578
vhci_env_p                  0x3ffcc0a4
```

三项与 GDB 自身解析值一致。

### Device Service

`core2-native-vhci` 启动前解析 ELF，并把
`M5_NATIVE_VHCI_SEND_PC`、`M5_NATIVE_VHCI_ENV_PTR`、
`M5_NATIVE_VHCI_IDLE_PC` 传给 bridge。Session event 记录
`native_vhci_symbols`。

BLE/unified profile 的默认 readiness timeout 从 30 秒提高到 90 秒；
显式 `ready_timeout_seconds` 仍可覆盖。

### 独立 runner

standalone runner 默认 `--symbol-source pinned`，保留 `gdb` 作为对照。
unified runner 使用同一 ELF 解析器。两个 runner 的 evidence 都记录固定地址。

### 未保留的失败实验

中途尝试把 C2H 改为每次 idle breakpoint 只注入一个 packet，并复用同一
breakpoint 实例。该未提交行为在首个 Device Service lease 中出现
`Cannot execute this command while the target is running`、guest
`InstrFetchProhibited` 和重启循环。

该实验没有进入结果提交。结果版本保留此前有 standalone `5/5`、unified
`3/3` 和 Device Service 单 lease 证据的注入行为；当前工作树另完成一次
standalone `1/1`。重复 lease 稳定性仍单列为 `CORE2-01` 的下一道门禁。

## 文档对账

同步更新：

- `README.md`、`docs/README.md`、`docs/project-status.md`；
- `docs/workstreams.md`、`docs/project-backlog.md`、`docs/code-map.md`；
- `docs/device-service-api.md`、`docs/device-service.openapi.yaml`；
- `docs/unified-device-runtime.md`、`docs/network-simulation-plan.md`；
- `docs/qemu-device-adaptation-matrix.md`；
- Core2 standalone/unified runner README。

文档统一采用以下边界：

```text
symbol lookup                    ELF pinned
guest pause / callback injection GDB
synthetic send-frame return      GDB
bit-exact BT controller          NOT RUN
```

## 验证

本机结果提交：

```text
platform tests                 243/243 PASS
xtensa ELF parser tests        3/3 PASS
runtime coverage               PASS
peripheral catalog             PASS
QEMU profiles                  PASS
current standalone Core2      1/1 PASS
pinned-symbol standalone      5/5 PASS
pinned-symbol unified         3/3 PASS
```

GitHub Actions run `40003866186` 的 `platform-contracts` 与 Linux
namespace/network policy 两个 job 均 PASS。

## 验证边界

- 本轮证明的是 firmware 自报的 VHCI host API 边界，不是 ESP32 BT
  controller/baseband 指令级执行；
- QEMU/Bumble 路径不是 RF、天线、WPA2/WPA3、距离、功耗或共存模型；
- standalone `5/5` 与 unified `3/3` 证明固定符号下功能路径可重复；
- Device Service 只完成单 lease PASS，未完成同 commit 固定次数重复 lease；
- 物理硬件和真机 BT 行为为 `NOT RUN`。

## 风险与回滚

- 回滚到 `829d64e99ae318c6d78de0729bb6a75f8455373c` 可恢复 GDB 符号查询，
  不修改物理设备；
- GDB bridge 仍是 trusted-host 诊断实现，不适合作不可信固件隔离边界；
- 后续应先完成重复 lease 门禁，再替换 GDB 控制面。
