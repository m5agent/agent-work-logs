# M5Stack ESP Emulator Core2 WiFi IRQ cache gate 报告

## 背景

- 来源：`RUNTIME-03` legacy Core2 normal-WDT 启动。
- 现象：boot markers 后偶发 `Cache disabled but cached memory region
  accessed`，MCU reset 且 frame 保持黑色。
- 目标：区分 guest 代码问题、cache 模型问题与外部 IRQ 注入时机，并修复
  共享控制器边界。

## 结论

- 状态：`PARTIAL`。
- 根因或关键判断：WiFi MAC level 可在 CPU 的 instruction cache disabled
  Flash handoff 窗口内断言。旧 INTMATRIX 立即向 CPU 输出该 level，IRQ
  进入 cached ISR，命中 cache-disabled 保护并 panic。
- 改动范围：DPORT 输出 per-CPU cache-ready；INTMATRIX 在 gate 为低时暂存
  `ETS_WIFI_MAC_INTR_SOURCE`，恢复后重算输出。

不门控：

- cross-core handoff IRQ；
- timer source；
- cache-illegal-access source；
- watchdog 控制或 timeout。

## 证据

### Pre-fix

Diagnostic QEMU：

```text
54d31e90e2eff273b17f11388015e9bf16a1cf6877fbf7681c207eb73b68286f
```

同一 firmware 与 config overlay 到达 BOARD/APIKEY/boot markers 后出现：

```text
Cache disabled but cached memory region accessed
```

frame 为 302-byte black PNG。

### Post-fix

Final QEMU：

```text
a4cfa2b8c3aa7e62b11423fa456c57ec01da7c7e43086a90bdded0eec6241249
```

运行条件：

```text
runtime=qemu-wifi
profile=core2-openmac
icount shift=2
per-vCPU budget=default
watchdog=normal
```

结果：

- BOARD/APIKEY/boot start/boot done 均出现；
- 无 cache-disabled panic；
- `320x240`、`75,559` nonblack pixels、`512` colors；
- frame SHA256
  `737df08a0c5d21fe23a46e38f79b7a580508f8dfa7c63c9bc552be19a3106c96`；
- 画面是原厂 API Key/setup page；
- 后续为独立的 `TG0WDT_SYS_RESET`。

### 回归

- Core2 UIFlow2 device group `6/6 PASS`；
- peripherals/audio/mic/power monitor/IMU/AXP192；
- attempts 1，retry false；
- matrix summary SHA256
  `432504a9561a3e3cb4156817edd9c0565848dae8a18f64cb92a09cd2476ac419`；
- WiFi IRQ cache-gate source tests `3/3 PASS`；
- docs contracts `50/50 PASS`；
- platform full suite `1,599`，`1,598 PASS + 1 skip`；
- generators、compileall、Ruff `E9/F` 与 diff check PASS。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | source patch forward/reverse dry-run 与 QEMU rebuild |
| transport | `PASS` | `/api/v1` firmware/config/session 和串口 |
| device_response | `PARTIAL` | 默认 budget 到原厂 API Key 页面；normal-WDT 随后 reset |
| data_behavior | `PASS` | retained WiFi level、cache-ready gate 与 Core2 设备组 |
| visual_or_physical | `PARTIAL` | virtual-device frame；physical display `NOT RUN` |
| review | `PASS` | source/platform/docs contracts |

## 验证边界

该修复消除了本次 WiFi IRQ/cache handoff panic，但不证明 normal-WDT
startup、WiFi 连接、DHCP、setup/REPL 或用户应用稳定。没有执行物理硬件、
RF、电气和物理 cache/PSRAM timing 测试。

## 风险与回滚

门控只作用于 WiFi MAC source，level 保持到 cache 恢复；其他 handoff 与
exception source 不被隐藏。回滚为 revert source commit `4b99fa0a`，
回滚后原 WiFi IRQ/cache panic 路径重新出现。
