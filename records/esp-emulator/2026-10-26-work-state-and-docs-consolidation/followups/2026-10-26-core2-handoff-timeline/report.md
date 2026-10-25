# ESP Emulator Core2 unified handoff timeline report

## 背景

前一轮已经用 `0036` 把 Core2 legacy 的 QIO 数据面改为保留 m25p80 状态的
批量读取，但正常 WDT 下仍失败。已有 cross-core、DPORT、TIMG 和 SSI
诊断分别存在，缺少的是同一 virtual-time/CPU/guest-PC 时间轴。文档里也仍有
“下一步增加统一时间轴”和旧 patch replay 说明，与后续结果不一致。

目标是把统一 trace、WDT-disabled 对照、双核 PC 候选路径和当前待办写回
同一事实源，同时验证 trace-off UIFlow2 回归没有被诊断代码破坏。

## 结论

`0037` 新增默认关闭的 `M5SW_ESP32_HANDOFF_TRACE`：

- cross-core level write；
- DPORT APPCPU/cache control/cache sync；
- TIMG watchdog config/feed/arm/timeout；
- ESP32 UART enable/clear/status transition；
- ESP32 SPI transaction 和 receive-data phase。

每行记录 QEMU virtual time、当前 CPU、guest PC 以及四个组件字段。常规事件可
用 `M5SW_ESP32_HANDOFF_TRACE_SAMPLE` 降采样，WDT timeout/interrupt/reset
始终保留。可选的 1 ms 双核 PC 采样默认关闭，因为实测会改变调度。

两次 normal-WDT 运行都复现了最后一个 TG1 feed 到 stage-0 timeout 的固定
`800,000,000 ns` 间隔，timeout PC 不同。canonical run 的 stage-1 timeout
在 `2.4 s` 后出现；replicate 的 `-no-reboot` 截断只保留 stage-0。关闭 WDT
时，`sample=1024` 与 trace-off 得到相同 507-byte banner-only Serial，说明
该采样级别没有改变序列结果。

1 ms PC 控制把 reset 提前到约 `3.148 s`，但仍保持 800 ms feed gap。最终
800 个样本只出现 6 个 CPU0/CPU1 PC 对：

- CPU0：`0x400843ac`、`0x400843af`、`0x400843b1`；
- CPU1：`0x4008649c`、`0x4008649e`。

本地 ELF 将这些地址映射到 `uart_rx_intr_handler_default` 和
`mp_execute_bytecode`，但 ELF 未证明与 public BIN byte-identical。该窗口
没有 UART `INT_ENA`、`INT_CLR` 或 RX register event，因此结论只有
“CPU0 中断/服务饥饿候选”，不是已证 UART storm。

## 文档与代码整理

- 新增 `0037` patch、summarizer、evidence metadata、契约测试和 pending
  documentation references；
- 回写顶层 README、项目状态、Backlog、工作流、工程交接、代码地图、QEMU
  矩阵、运行时缺口、公开固件矩阵、验证台账、patch README 和生成快照；
- PC symbolization 从 evidence 内手工块拆成独立 metadata，并由 summarizer
  显式接收，避免重跑时丢失；
- 修正历史调查中的第二轮 feed count `11,891` → `12,045`，并加入
  evidence-to-doc 断言；
- 修正 patch replay 承诺：`0003` 已包含后续 PCM 状态；实测
  `0004` 在当前 `0003` 后失败，且 `m5_i2s_esp32.c` 只存在于 retained
  target tree。后续编号 patch 因此明确标为 predecessor-bound，而不是
  raw-upstream clean-room recipe。

## 执行

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'

python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check

python3 -m compileall -q platform tests
ruff check platform/tools platform/tests --select E9,F
node platform/tests/test_sha256.mjs
node platform/tests/test_firmware_upload.mjs
python3 tests/network/worker_tls/run_fleet_migration_test.py \
  --out /tmp/m5-fleet-credential-migration-final.json
```

`0037` apply check 使用 retained target tree 的 `0037` 后状态：

1. 复制 `0037` 影响的 7 个文件；
2. reverse `0037` 得到 `0036` 后前序状态；
3. forward check/apply；
4. reverse check。

该检查通过，但不能表述为“`0037` 能直接应用到裸上游 `da100c9`”；后者实测
失败。

QEMU source baseline：
`da100c909249926b9f4458f18e4f2d216d08f51a`。实际 patch 前序还要求
`0036` 及 retained target tree 中的文件状态。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU Xtensa 已重建；compileall、Ruff、patch predecessor forward/reverse check PASS |
| transport | `PARTIAL` | unified trace 正常产生 cross-core/DPORT/SSI/UART/TIMG 事件；legacy application 未启动 |
| device_response | `PARTIAL` | 两次 normal-WDT 固定 800 ms feed gap；timeout PC 可变 |
| data_behavior | `PASS` | WDT-disabled sample=1024 与 trace-off Serial 字节/SHA 相同；PC 窗口分类可重复计算 |
| regression | `PASS` | Core2 UIFlow2 `6/6`、完整 UIFlow2 `67/67`，零 retry |
| documentation contract | `PASS` | 平台 `504/504`、docs `41/41`、profile `19/19` |
| delivery | `PASS` | 产品 commit `8391958`；CI `40234012879` 两个 job PASS |
| legacy UIFlow | `FAIL` | 正常 WDT reset、reset PC `0`、black frame、无非空应用帧 |
| visual_or_physical | `NOT RUN` | 物理 cache/PSRAM/Flash/timer/WDT、RF、电气和真机 |

## 验证边界

- trace 是默认关闭的 diagnostics，不是产品修复；
- PC 符号化来自未绑定 public BIN 的本地 ELF；
- PC 高频采样会扰动调度，只能作为独立 control；
- 固定 800 ms 现象不等于 UART storm，也不能指定唯一 CPU0 临界区；
- `M5SW_DISABLE_WDT`、bulk bypass 和 accelerator control 都不能形成固件 PASS；
- 所有功能结论都是 virtual-device validation，不是物理 RF、电气或真机证据；
- retained QEMU dirty worktree 包含既定板级修改，不能 reset/clean。

## 风险与回滚

没有烧录、擦除或持久设备状态变更。`0037` 默认关闭，未设置环境变量时不输出
handoff trace。若 trace ABI 或 KVM/TCG 行为出现回归，可单独回退 `0037` 并
重建 QEMU；不应 reset retained target tree，否则会丢失前序板级修改和可重放
前序状态。
