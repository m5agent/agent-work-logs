# ESP Emulator Core2 legacy status/CAS correlation report

## 背景

Core2 官方 legacy `UIFlow_Core2 v1.15.4` 在 WDT-off 下可以继续执行
到 BOARD/APIKEY 和 boot script，但 normal-WDT 会在约 `17.25 s` 触发
TG0 stage-1 system reset。此前 `0071-0073` 已把预算收窄到
`0xBB/64 -> 0x05/1 -> 0xBB/64`，但仍不知道 status 返回值、cache
状态和 guest 锁路径的关系。

目标是验证：

1. `RDSR` 的 WIP/BUSY 位是否长期为 1；
2. `0xBB/64` 后到 status read 前的 gap 与 cache counter 如何变化；
3. `s32c1i` 的 old-owner、锁地址和调用者是否表示 CAS 语义错误；
4. 失败 CAS 上主动让出 TCG slice 是否改变 normal-WDT 边界。

## 实现

新增 `0075-esp32-legacy-status-cas-correlation.patch`：

- 在 `RDSR(0x05)` 完成后记录 status byte；
- 记录前序命令、`0xBB/64` 地址、RX prefix 和 status gap；
- 记录两次 status read 间的 cache sync/state/invalidate delta；
- 记录 PS intlevel 与 `interrupt_request`；
- 对 `s32c1i` 建立有界 PC、caller A0、lock address、old-owner、
  current CPU 和跨核 holder-PC bucket 表；
- runner 增加 `ssi_rdsr_profile` 和 `s32c1i_profile`；
- 默认关闭的 `M5SW_XTENA_CONTENDED_CAS_YIELD` 只作为负向控制。

所有表都有 overflow counter。新增计数只在
`M5SW_ESP32_HANDOFF_TRACE=1` 下启用，输出只发生在显式 freeze。

## 执行

环境：

- firmware source SHA256：`18d77e28adfacf7e719a167bd0c3450b78357d13cb1d2f2a8b7bccc2248a909a`
- normalized flash SHA256：`4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- QEMU SHA256：`d60e6fb0e24e025ff19a521b34debbb9c16d9e5e427d35c8d22596ad98de42fa`
- runtime：`qemu-wifi`
- accelerator：`tcg,thread=single,tb-size=128`
- icount：`shift=5,align=off,sleep=off`

关键命令：

```bash
PYTHONPATH=platform/tools:.work/py312 .work/py312/bin/python \
  tests/firmware/core2_handoff_trace/run_pause_sweep.py \
  --image .work/runtime03-original-vfs-probe/image.bin \
  --qemu .work/M5StopWatch-QEMU/build/qemu/build/qemu-system-xtensa \
  --pause-seconds 20 --disable-wdt --runtime qemu-wifi \
  --expected-image-sha256 4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4 \
  --pc-sample-ns 5000000 --service-port <isolated-port> \
  --out-dir /tmp/m5-core2-status-cas
```

normal-WDT 和 failed-CAS-yield 控制使用同一 QEMU/firmware。唯一差异是
第二个运行设置 `M5SW_XTENA_CONTENDED_CAS_YIELD=1`。

## 证据

### RDSR 与 cache

20 秒 WDT-off：

- `RDSR` 总数：`12,093`
- status `0x00`：`4,278`
- status `0x02`：`7,815`
- bit0 WIP/BUSY：全部为 `0`
- 前序 `0xBB/64`：`11,904`
- status gap 总时间：`17.074056543 s`
- 最大 status gap：`1.923178656 s`
- status read 的 PS intlevel/IRQ request：全部为 `0`

cache delta：

| Counter | 非零区间 | 总 delta | 最大 |
| --- | ---: | ---: | ---: |
| sync calls | `11,954` | `55,316` | `120` |
| sync pages | `3` | `5,655` | `4,708` |
| state updates | `11,954` | `55,350` | `154` |
| invalidates | `3` | `84` | `70` |
| illegal reads | `0` | `0` | `0` |

### s32c1i

- total：`6,288,123`
- success：`537,482`
- raw old-value non-free：`5,750,641`
- real cross-core contention：`5,737,336`
- `0x3ffbf2cc`：`5,482,913` CAS、`253,241` success
- holder overflow：`0`

old-owner 常见值：

- free `0xB33FFFFF`：`537,437`
- `0x0000ABAB`：`4,832,401`
- `0x0000CDCD`：`918,240`
- 其它：`45`

最高 failed-CAS 调用：

| CPU / caller A0 | CAS site | Lock | Count |
| --- | --- | --- | ---: |
| CPU0 `0x8009655c` | `0x40095b2e` | `0x3ffbf2cc` | `3,254,878` |
| CPU0 `0x80095833` | `0x40094a5a` | `0x3ffbf2cc` | `1,010,213` |
| CPU1 `0x80095833` | `0x40094a5a` | `0x3ffbf2cc` | `767,177` |

holder-PC 以 256-byte 桶记录，热点覆盖
`0x400958xx-0x400961xx`、`0x40096dxx` 和
`0x40097axx-0x40097bxx`。没有 matching legacy ELF/MAP，禁止把
这些地址解释成精确函数。

### normal-WDT control

| 控制 | stage-0 | stage-1 | first reset | TG1 timeout |
| --- | ---: | ---: | ---: | ---: |
| normal WDT | `7.248411234 s` | `17.248411265 s` | `17.248490561 s` | `0` |
| failed-CAS yield | `7.248929759 s` | `17.248929760 s` | `17.248930720 s` | `0` |

两者均为 `BOOTLOADER_TG0_STAGE1_RESET_WITH_TG1_LIVE`。serial 只有 banner，
frame 仍为 302-byte black PNG。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU rebuild、compileall、Ruff E9/F |
| controller diagnostic | `PASS` | RDSR/CAS sparse table totals 完整，overflow 0 |
| virtual-device data behavior | `PASS` | status、cache delta、CAS owner/caller/holder 可观测 |
| normal-WDT boot | `FAIL` | 约 `17.249 s` TG0 stage-1 reset |
| visual_or_physical | `NOT RUN` | 无真机、RF、电气或物理 timing |
| delivery | `PASS` | product `66af02cc`；CI `40783815160` 两 job PASS |

平台测试：`1432 OK, 1 skip`；`runtime_coverage`、`peripheral_catalog`、
`qemu_profiles`、`project_snapshot`、compileall、scoped Ruff 和
`git diff --check` 均 PASS。

## 结论与边界

本轮否定了两个假设：

1. Flash WIP/BUSY 位长期让 guest 等待；
2. QEMU `s32c1i` old-owner 结果损坏。

当前主要预算位于 scheduler/list 跨核锁竞争和 guest 在 status read
之间执行的工作。失败 CAS 上退出 TCG slice 不改变 WDT 边界，不能作为
产品修复。

未定位的仍包括：tick/IRQ 频率是否异常、`0x3ffbf2cc` 最长持有区间、
matching source/ELF/MAP、startup UI、setup/REPL 和非空应用帧。

## 风险与回滚

没有硬件写操作、凭据、生产配置或持久数据迁移。诊断表只在显式环境开关下
累计并在 freeze 输出；默认关闭的 CAS yield 仅用于负向控制。

回滚 `66af02cc6061bded00659ee13632f5e3a9a397dc` 或 revert `0075` 可移除
诊断和负向控制，既有 `0071-0074` SPI/panel 行为不变。
