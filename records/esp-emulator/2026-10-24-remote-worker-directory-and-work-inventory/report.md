# ESP Emulator 远程 worker 注册目录与工作总整理报告

## 背景

项目在 2026-10-24 已连续完成网络 namespace/egress、Core2 native-HCI
诊断、FirmwareManifest 许可策略、WebBurner、SPIFFS 和双 guest lab fabric
等多项工作。主状态页虽然已分层，但仍有两个问题：

1. 工作树里存在未完成的远程 worker 目录代码，没有 HTTP 路由、契约测试、
   OpenAPI 或文档；
2. `project-status`、`project-backlog`、`workstreams`、代码地图和专题页对
   “远程注册已做/调度未做”的边界表述不一致。

目标不是再新增一份状态摘要，而是把半成品实现收口，并让所有当前入口引用
同一份已测试代码和明确的待办。

## 结论

新增 `platform/tools/worker_directory.py`，持久化
`<state-dir>/workers.json`，并提供：

- 原子写入和 `0600` 权限；
- worker identity、instance、generation 冲突检查；
- ready/draining/drained/stopped 状态、stale 判定和 accepting 计算；
- heartbeat、drain、stop 和 bounded result metadata；
- 128 worker、每 worker 128 active lease、32 recent result、16 KiB
  capability 上限；
- HTTP(S) endpoint 校验，拒绝凭据、query 和 fragment。

Device Service 新增：

```text
GET  /api/v1/workers
POST /api/v1/workers
POST /api/v1/workers/{worker_id}/heartbeat
POST /api/v1/workers/{worker_id}/drain
POST /api/v1/workers/{worker_id}/stop
POST /api/v1/workers/{worker_id}/results
```

OpenAPI/runtime contract 从 `1.14.0` 升级到 `1.15.0`。新路由沿用现有
Bearer token 边界。

## 代码与文档整理

源码整理：

- 把远程目录从 `device_service.py` 的即将继续膨胀区域拆成独立模块；
- 增加 identity/generation、stale replacement、stopped terminal state、
  endpoint/capability/result 上限等单元测试；
- 增加真实 `ThreadingHTTPServer` 路径的注册、list、heartbeat、result、
  drain、stop 和 identity mismatch 契约测试；
- 增加 `/api/v1/workers` 未授权 `401` 和授权 `201` 测试；
- 修复文档测试在完整 suite 中复用外层 `TestLoader` 导致测试计数漂移的问题。

文档整理：

- `project-status`：明确“注册目录已实现、supervisor/队列/re-attach 未实现”；
- `project-backlog`：把 `NET-04`/`SVC-01` 的下一交付从“定义注册”改为
  “supervisor、持久队列和活动接管”；
- `workstreams`：更新网络与服务生命周期工作流；
- `code-map`：登记新模块、测试入口和代码域；
- `device-service-api`/OpenAPI：补齐路由、对象、状态机和边界；
- README、平台 README、AGENTS、服务架构、网络方案和固件审查工作流：
  清除“远程注册完全缺失”的旧表述。

## 执行

环境：

- macOS Apple Silicon；
- Python 3；
- 本地临时 state directory 和 loopback HTTP server；
- 不操作物理设备，不烧录固件。

命令：

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 -m py_compile ...
ruff check --select E,F,I \
  platform/tools/worker_directory.py \
  platform/tests/test_worker_directory.py
ruby -e 'require "yaml"; YAML.load_file("docs/device-service.openapi.yaml")'
git diff --check
```

结果：

```text
platform tests      283/283 PASS
worker directory    9/9 PASS
HTTP contract       PASS
Bearer auth         401 -> 201 PASS
runtime coverage    PASS
peripheral catalog  PASS
QEMU profiles       PASS
OpenAPI YAML        PASS
Ruff selected rules PASS
git diff check      PASS
```

GitHub Actions：

```text
CI run 40047928762
platform-contracts       PASS
network-namespace-policy PASS
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall/py_compile 成功 |
| transport | `PASS` | 真实 loopback HTTP server 执行新路由 |
| device_response | `NOT RUN` | 本次未启动 QEMU 或 esp-emu 设备会话 |
| data_behavior | `NOT RUN` | 本次没有修改设备/网络数据面 |
| visual_or_physical | `NOT RUN` | 本次无画面或物理设备验证 |
| review | `PASS` | 文档索引、链接、旧状态、API 版本和任务 ID 契约 |
| delivery | `PASS` | 源码提交、push 和 CI |

## 验证边界

- `PASS` 只覆盖远程 worker 目录、HTTP 边界和文档一致性；
- `workers.json` 是目录，不是任务状态机；不包含队列、租约调度、取消/重试、
  实际 worker 拉起或证据文件上传；
- 服务重启后仍不能接管活动 QEMU 进程；
- 现有双 guest fabric 和 67-case 矩阵沿用旧 evidence，本次没有重跑；
- 所有仿真结论都不是物理硬件、RF、功耗或长期 soak 验证。

## 风险与回滚

风险集中在新增状态文件格式和状态机过严：不兼容 schema 会 fail-closed
返回 `503 worker_directory_invalid`；live instance 或旧 generation 冲突返回
`409`。这是按预期防止错误接管。

回滚源码提交 `a1917eaf410d093d780128696819db7b081b9ae7` 可恢复
`1.14.0` 契约和未注册的本地 worker-only 路径，不会修改物理设备或固件。

## Follow-up：代码、文档与 Core2 诊断再对账

### 背景

用户要求把后续完成的代码和文档重新收口，因为部分状态页仍停留在较早的
Core2 native-HCI 阶段。检查发现两个需要修正的事实：

1. `platform/qemu/profiles.json` 的摘要写成 `13` 台 QEMU ESP32，实际是
   `12` 台 QEMU-backed ESP32 加 Tab5 `esp-emu`；
2. 文档只记录 HLI event，随后实验已通过 HLI 投递 event/ACL 到 NUS
   discovery/subscription 和外部 NUS write，但 guest write/ACK/notification
   仍未完成。

### 改动

- 同步根 README、当前状态、Backlog、工作流、代码地图、网络方案、统一运行时
  和设备矩阵；
- QEMU profile 摘要改为 `12 + Tab5`，`qemu_profiles.py --check` 改为按
  catalog 动态校验计数文字；
- `run_full.py --hli-c2h` 增加事件/ACL counters、BLE failure 快照、TX queue、
  QOM 读取去重和 QEMU 早期退出错误摘要；
- 明确 `--hli-c2h` 依赖 ignored QEMU worktree 的实验 hook，不属于已提交
  `0001`/`0002` patch；
- 新增 Core2 HLI/API-boundary 失败 evidence，并把文档一致性测试扩展到该
  evidence 的关键字段。

### 执行

```text
platform tests                 283/283 PASS
docs contracts                 9/9 PASS
runtime coverage               PASS
peripheral catalog             PASS
QEMU profiles                  PASS
python compile                 PASS
GitHub Actions 40051638039     PASS
Core2 HLI/API repeat           2/2 notification timeout (expected FAIL)
QEMU full matrix               NOT RUN
physical hardware              NOT RUN
```

Core2 同一固件/ELF/QEMU build 两次都完成广播、连接、NUS discovery、
subscription 和外部 NUS write；两次都没有 guest write/ACK marker 或
notification。失败快照中已经各出现一次 H2C `EIO`，peer 断开后写失败累计到
`15`。现有记录没有 packet ID 和单调时间戳，不能判定首个 `EIO` 与
notification timeout 的先后，也不能把 `EIO` 当作唯一根因。

### Follow-up 验证边界

- 文档与 profile 改动没有触碰已提交的 QEMU 设备数据面，因此没有重跑
  67-case 全矩阵；
- Core2 结果是 `virtual-device validation`，不是 RF、controller firmware
  或物理等价性验证；
- 实验 QEMU 二进制 SHA256 已写入 evidence，但实验源码没有进入提交，
  因此不是可发布后端；
- 远程 worker supervisor、持久队列、活动 QEMU re-attach 和外部 IPv6 仍为
  `NOT RUN`。

### Follow-up 回滚

回滚源码提交 `187a7dc9ad823b449b5a88be6e82d60816c753d7` 可恢复
`a1917eaf410d093d780128696819db7b081b9ae7` 的文档与 profile 基线；
不会修改设备、网络或固件产物。
