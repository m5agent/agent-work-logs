# ESP Emulator Core2 stateful SSI batch report

## 背景

- 来源：
  [m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)
- 需求：完整整理近期 Core2、WiFi/BLE、网络和固件审查代码/文档，并把
  SSI 批量数据面、legacy WDT 失败、当前假设和下一门禁区分清楚。
- 目标：替换临时 `blk_pread` 诊断快路，在保留 m25p80 状态机的控制器
  data plane 内实现批量读取，并重新验证共享控制器回归。

## 结论

- `0036` 新增通用 SSI byte-buffer 接口；没有 callback 的器件保持原逐字节
  行为；
- m25p80 仅在 `STATE_READ` 批量读取，地址递增与回绕、CS、command、
  address 和 dummy phase 保持原语义；
- ESP32 SPI 只在 receive-only data phase 调用批量接口；
- `512` 个采样 `64-byte` 批次与原实现完全一致；
- 重建 QEMU 后，Core2 UIFlow2 定向和共享控制器完整矩阵均通过；
- 同一 legacy firmware 仍以 interrupt-WDT/reset 和 black frame 失败；
- cross-core handshake 会反复完成，旧“永久死锁”判断撤回；当前假设是
  累计同步 Flash/cache/DPORT handoff 吞吐不足。

## 改动范围

- 新增
  `patches/qemu-m5stack-peripherals/0036-ssi-transfer-buf.patch`；
- 新增 `tests/firmware/evidence-2026-10-26-core2-ssi-transfer-buf.json`；
- 更新 README、文档索引、当前状态、Backlog、工作流、交接、QEMU 矩阵、
  代码地图、运行时缺口登记、公开固件矩阵、验证台账、历史调查、patch
  索引、生成快照和文档契约；
- 撤回旧 QIO evidence 中“REPL 可稳定到达”和“cross-core 永久死锁”
  的过强表述，保留当时观察并标注后续复测结果；
- 未移动 `device_service.py`；`SVC-03` 仍按原计划独立推进。

## 执行

```bash
ninja -C .work/M5StopWatch-QEMU/build/qemu/build qemu-system-xtensa

git apply --check \
  patches/qemu-m5stack-peripherals/0036-ssi-transfer-buf.patch
git apply --reverse --check \
  patches/qemu-m5stack-peripherals/0036-ssi-transfer-buf.patch

PYTHONPATH=.work/py python3 tests/uiflow2/run_peripheral_matrix.py \
  --device core2 --out-dir /tmp/m5-uiflow2-core2-ssi-final

PYTHONPATH=.work/py python3 tests/uiflow2/run_peripheral_matrix.py \
  --out-dir /tmp/m5-uiflow2-ssi-transfer-buf-final

PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'

python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
ruff check --select E9,F platform/tools platform/tests
```

QEMU patch base：`da100c909249926b9f4458f18e4f2d216d08f51a`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU Xtensa 重建、patch forward/reverse check、compileall、Ruff `E9/F` |
| transport | `PARTIAL` | SSI batch 字节等价；legacy 正常 WDT 与 WDT-disabled control 仍失败 |
| device_response | `PARTIAL` | flash-op 与 cross-core reason 反复完成，但没有非空 legacy 应用帧 |
| data_behavior | `PASS` | `512 x 64-byte` 与原逐字节路径零 mismatch |
| documentation contract | `PASS` | docs `41/41`、platform `501/501`、QEMU profile `19/19` |
| delivery | `PASS` | product commit `3d75d30`；CI run `40226918011` |
| visual_or_physical | `NOT RUN` | 物理 SPI/cache/PSRAM/timer/WDT、RF、电气和真机 |

## 验证边界

- SSI 批量路径保留现有状态机，但不证明物理 Flash timing；
- Core2 与完整 UIFlow2 矩阵是 virtual-device validation，不是任意固件
  兼容性证明；
- legacy UIFlow 仍为 `FAIL`，`RUNTIME-03` 继续 `OPEN`；
- WDT disable、accelerator override、temporary bulk read 和单次 REPL
  marker 都不是产品修复；
- 物理 Flash、cache、PSRAM、timer/WDT、RF、电气和真机均未执行。

## 风险与回滚

没有烧录、擦除或持久设备状态变更。回滚产品提交 `3d75d30` 会同时移除
`0036` 和本轮文档对账；更小回滚点是只移除 `0036` 并重建 QEMU，但这会
恢复逐字节 SSI 成本和旧文档歧义。retained dirty QEMU 工作树包含既定板级
修改，不能 reset/clean。
