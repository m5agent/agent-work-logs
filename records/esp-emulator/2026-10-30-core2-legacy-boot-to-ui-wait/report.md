# M5Stack ESP Emulator Core2 legacy boot-to-UI attribution 报告

## 背景

- 来源：public `UIFlow_Core2 v1.15.4` 的 `RUNTIME-03`
- 现象：normal WDT 在 BOARD/APIKEY 前 reset；WDT-off 不产生 factory UI
- 目标：区分 deterministic timing 预算、Flash/cache handoff 和 boot.py
  之后的 guest 应用等待

## 结论

- 状态：`PARTIAL`
- 交付：PR #47 merged as `f1cc974bd6922551141b9d478d6dc8ec7a13f06c`
- 根因或关键判断：boot.py 已可通过 normal WDT；下一阻断位于 legacy
  WiFi 配置/UI 初始化，而非无终点 Flash scan
- 改动范围：仅文档与证据，未修改默认 simulator timing

`shift=2` + `1 us` 是当前最快的诊断控制，但不作为产品修复，因为
factory UI、REPL 和非空应用帧仍失败。

## 证据

### 代码或配置

```text
M5_CORE2_ICOUNT_MAX_PERCPU_NS=1000
-icount shift=2,align=off,sleep=off
runtime=qemu-wifi
network.profile=core2-openmac
```

默认产品路径仍为 `shift=5` + `10 us`。

### 执行

- 环境：Device Service `/api/v1`; virtual Core2; matching LittleFS2 VFS
- 命令：`run_pause_sweep.py --pause-seconds 15 --capture-frame --uart-trace --runtime qemu-wifi --icount-shift 2`
- 结果：BOARD/APIKEY `4.659620404/4.660179256 s`; boot.py
  `8.340878020-8.504887849 s`; final frame black

WDT-off 15/20 秒快照均为双核 Waiti `0x4026306e`，serial SHA
`923380826ceb9be6107e6437dcb690be6a67bdccaade80164ab6537b7f458d0d`。
最后 Flash/cache sync 为 `9.358926093 s`。FRC timer trace 仍记录到
`9.277506536 s` callback。

显式 UART 诊断在 guest virtual `9.267433433 s` 捕获：

```text
wifiWebCfg.py:84 _thread_task
menu/wifi.py:22 __init__
m5stack_ui.py:526 __init__
KeyboardInterrupt
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `NOT RUN` | docs-only change |
| transport | `PARTIAL` | UART diagnostic input and MTD/QEMU session path executed |
| device_response | `PARTIAL` | BOARD/APIKEY and boot.py pass; no REPL/main application |
| data_behavior | `PARTIAL` | Flash/cache counters and FRC timer callback evidence |
| visual_or_physical | `FAIL` | 302-byte black frame; physical hardware `NOT RUN` |
| review | `PASS` | platform `1581 OK + 1 skip`, docs/generator checks and four PR CI jobs pass |

## 验证边界

本记录是 virtual-device validation。它不证明 physical timing、RF、
electrical、cache/PSRAM equivalence 或 hardware behavior。UART FIFO
input 只用于采样已有等待栈，不是产品输入路径。

## 风险与回滚

未修改固件、QEMU、服务或默认 timing；回滚为 revert PR #47 的文档提交。
