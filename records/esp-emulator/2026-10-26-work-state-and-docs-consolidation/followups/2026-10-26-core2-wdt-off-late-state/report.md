# Core2 WDT-off late-state and documentation reconciliation report

## 背景

此前的 three-run WDT liveness 证明 TG0 stage-1 触发首次 reset 时 TG1 仍在
feed，但当前文档很快又把下一问题写成“应用初始化为何未在 15 秒前完成”。
后续 45/120 秒 WDT-off 快照又显示 Flash/SSI 工作约在 44 秒结束，随后 CPU1
进入同一 late loop。多个当前入口仍保留旧阶段结论，导致用户需要手工判断
哪一份文档代表现状。

目标是把最新 late-state 作为当前调查边界，统一当前状态、Backlog、工作流、
代码地图、固件矩阵和测试说明，并用自动门禁阻止旧结论回流。产品目标
`legacy UIFlow` 正常启动仍未达成。

## 改动

### 诊断代码与 evidence

- `0041` 扩展 exact-time pause，输出 A0-A15、PS、对象前向指针和最多 64-word
  stack window；环境变量默认关闭，stack 读取有上限；
- `run_pause_sweep.py` 解析寄存器、对象偏移和可选 stack events，支持
  `--disable-wdt` 诊断 control；
- `run_wdt_liveness.py` 暴露受限 `--trace-sample` 参数；
- 新增 late-state evidence 和 contract test；
- QEMU profile blocker 更新为当前 late-loop 边界。

### 文档

- 当前状态统一为：normal-WDT 首 reset 来自 TG0 stage-1；WDT-off 45/120 秒
  在约 44 秒 Flash/SSI 活动后停在 CPU1 `0x40100049` flag/object wait；
- Backlog 收敛为一句可重放基线、当前阻断和五步最小执行顺序；
- Engineering Handoff 删除重复的逐次运行时间线，只保留稳定边界和权威链接；
- 历史调查补入 WDT-off 章节，并把旧 “remaining question” 明确标为当时状态；
- 公开固件矩阵、QEMU 矩阵、平台/测试说明和代码地图同步同一结论；
- `stale_doc_claims.json` 新增五条退役说法，并把相关固件/补丁/profile 页面
  纳入自动扫描；
- 文档契约不再要求 Backlog 复制 `0035-0040` 历史编号，改为验证当前 late
  state、链接归属和动态事实位置。

## 诊断结果

| 项目 | 45 秒快照 | 120 秒快照 |
| --- | ---: | ---: |
| CPU0 | `0x4026306e` halted `waiti` | 相同 |
| CPU1 | `0x40100049` running spin | 相同 |
| cache-sync calls | 49,848 | 49,848 |
| changed pages | 45,847 | 45,847 |
| SSI transactions | 22,554 | 22,554 |
| last Flash/SSI activity | 约 43.91-44.00 s | 约 43.91-44.00 s |
| cross-core writes | 123,476 | 139,094 |

CPU1 观测到 `A2+24=1`、`*(A3)=A10`、`A10+28=0`。Serial 在两个快照中保持
同一 507-byte banner-only hash，没有 setup/REPL。当前无法把对象命名为
RTOS、MicroPython、显示、PMIC 或其他驱动，因为现有 local ELF 与 public BIN
字节不一致。

## 验证结果

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
npm test
npm run test:units
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
python3 -m compileall -q platform/tools platform/tests \
  tests/firmware/core2_handoff_trace
ruff check --select E9,F platform/tools platform/tests \
  tests/firmware/core2_handoff_trace
git diff --check
```

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、Ruff `E9/F`、Node units |
| generated contracts | `PASS` | coverage、catalog、profile、snapshot |
| platform regression | `PASS` | `522/522` |
| documentation/Core2 contracts | `PASS` | `36/36`；stale claims 禁止回流 |
| virtual-device late-state evidence | `PASS` | committed 45/120 秒 artifact-bound evidence |
| new QEMU 45/120 rerun | `NOT RUN` | 本轮为 consolidation，没有再次启动该长时 control |
| legacy application | `FAIL` | normal-WDT reset、banner-only、black frame |
| visual_or_physical | `NOT RUN` | 无真机、RF、光学、电气或物理 timing |
| delivery | `PASS` | product commit `8d7122b`；pushed to `origin/main`；CI `40244649705` 两个 job 均 PASS |

## 验证边界

- 所有 virtual-device 结果只覆盖当前 machine/profile、public firmware SHA、
  QEMU binary SHA 和观察窗口；
- WDT-off 是诊断 control，不是产品修复；
- TG1 live、Flash/SSI counter 停止增长和 CPU1 spin 只描述当前 failure path，
  不是 physical controller、cache/PSRAM timing 或 RF 结论；
- 没有 matching ELF/MAP 时不能使用不同版本固件符号；
- late-state evidence 不是新的 45/120 秒 rerun。

## 风险与回滚

没有烧录、擦除、生产配置或持久设备状态修改。诊断 runner 使用 Device
Service 临时 lease，并保留历史 session 供复查。回滚 product commit
`8d7122b79bd6afe43f035e59697f91f8a3e3abc3` 可恢复上一版代码、文档和
stale-claim 门禁；回滚后旧文档冲突会重新出现，但不会改变任何外部设备状态。
