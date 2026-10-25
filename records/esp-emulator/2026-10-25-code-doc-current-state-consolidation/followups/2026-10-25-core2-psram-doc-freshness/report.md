# ESP Emulator Core2 guest PSRAM 与当前代码/文档重整报告

## 背景

Core2 此前已有 QOM evidence，证明 `m5core2` machine 在 CLI `-m 0` 下仍
解析出 4 MiB memory / `has_psram=true`。但该证据只证明机器配置，不能证明
guest 能分配并稳定读写 PSRAM。

同时，项目文档虽然已有“当前状态 / Backlog / 证据台账 / 专题页”分层，
但 README 和设备元数据仍重复维护部分状态，Core2 PSRAM 也仍只写成 QOM
观察。用户要求把代码、文档、当前工作和待办重新对齐到后来的实际进展。

## 实现

### Guest PSRAM probe

`tests/uiflow2/unified_core2/main.py` 新增：

1. `esp32.idf_heap_info(esp32.HEAP_DATA)` 读取 guest heap；
2. 选择最大的 4 MiB 外部堆；
3. 分配 1 MiB `bytearray`；
4. 每 4 KiB 写入确定性 pattern 和前两字节地址 tag；
5. 初始化后校验；
6. READY 后执行三次全缓冲读回；
7. 串口输出 ALLOC/INIT/SWEEP/STRESS 结果。

第一次 smoke 的 `mismatch at 0` 是测试代码缺陷：地址 tag 会覆盖 pattern
前两字节，旧校验却比较整块。修正后分别验证 `offset+2:end` 的 pattern 和
前两字节 tag；失败时停止重复 sweep，避免刷屏。

### Device Service gate

`run_service_5x.py` 新增 opt-in `--require-psram`：

- 要求 4 MiB 外部堆存在；
- 要求 1 MiB 分配让 heap free 至少下降请求大小；
- 要求且只要求一次 INIT PASS；
- 要求 sweeps 序列为 `[1,2,3]`；
- 要求一次 STRESS PASS；
- 任一 `PSRAM_ERROR` 或 `PSRAM_STRESS_ERROR` 都判 FAIL；
- 旧镜像没有新 marker，因此不默认启用，避免历史镜像假失败；
- 同时修复 session 未创建时空 manifest 被误判为 binding PASS 的假阳性。

## 执行结果

真实 `/api/v1` 创建 3 个独立 lease，参数：

```text
runtime=qemu-unified
profile=core2-native-hci
attempts=3
hold=20s
ble-reconnect-cycles=1
require-psram=true
```

结果：

| Lease | PSRAM | WiFi/公网 | NUS GATT | frame/QOM | pcap/evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | PASS | PASS | PASS | PASS | PASS |
| 2 | PASS | PASS | PASS | PASS | PASS |
| 3 | PASS | PASS | PASS | PASS | PASS |

每轮 outer heap 总量 `4,194,304 B`，guest allocation `1,048,576 B`，
heap free reduction `2,228,232 B`。三轮 frame SHA256 一致，QOM 均 34
nodes，HLI errors/queue/dropped/panic 均为 0。

## 代码与文档整理

- README 删除会重复漂移的静态设备能力表，改为指向生成快照；
- `project-status.md` 增加 guest PSRAM 当前结论和物理边界；
- Backlog 只保留物理 8 MiB/cache timing，不再保留已完成的虚拟 4 MiB
  guest 分配/读回；
- `workstreams.md`、`code-map.md`、Core2 专题、UIFLOW2 README、
  user-firmware matrix、validation ledger 和 freshness index 同步更新；
- `catalog.source.json`、QEMU profile、设备 JSON/README 增加机器可读和
  generated memory-validation 字段；
- 新增文档契约测试，锁定 evidence、runner hash、1 MiB/3 sweeps、
  同实例功能状态和“物理 8 MiB NOT RUN”边界。

## 验证

```text
Core2 guest PSRAM gate       3/3 PASS
platform contracts           417/417 PASS
documentation contracts      23/23 PASS
Node upload/SHA/UI           3/3 PASS
runtime coverage             PASS
peripheral catalog           PASS
QEMU profiles                PASS
project snapshot             PASS
compileall                   PASS
Ruff fatal checks            PASS
git diff --check             PASS
GitHub Actions 40148745338   PASS
```

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、哈希绑定、QEMU profile/catalog checks |
| transport | `PASS` | native HCI/HLI 与 Device Service API |
| device_response | `PASS` | frame/QOM、WiFi/公网、NUS GATT |
| data_behavior | `PASS` | 1 MiB guest allocation、pattern/tag、3 sweeps |
| visual_or_physical | `NOT RUN` | 无物理 PSRAM/cache timing、RF 或真机测量 |

## 未覆盖与风险

- QEMU effective PSRAM 是 4 MiB，不是板载 8 MiB；
- 不验证真实 SPI PSRAM 时序、cache miss 延迟、带宽或电气行为；
- 不证明 bit-exact BT controller/baseband；
- 不覆盖长时并发/吞吐、active-stop 之外 teardown、物理 RF 和真机；
- Core2 native-HCI hook 仍只对已验证的 UIFlow2 v2.5.3 build 成立。

## 回滚

先回滚文档提交 `b4b793127dd3351ed4a7b398ab1e0de810d17ab0`，再回滚功能提交
`785101915939795f2fb91ed2d9871ff420fd7e84`，即可移除 PSRAM probe、
证据、生成元数据和文档契约。回滚不涉及物理设备、凭据或不可逆状态。
