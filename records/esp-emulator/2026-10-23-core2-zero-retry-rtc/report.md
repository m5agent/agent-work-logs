# Core2 zero-retry 与 RTC 虚拟时钟报告

## 背景

在 `7823bef` 的共享 Core2 BB idle readback 补丁之后重跑 67-case 矩阵，
runner 返回 `67/67 PASS`。审计日志时发现：

```text
core2-audio/serial.attempt-1.log:
Guru Meditation Error: Core  / panic'ed (Cache error).
Rebooting...
```

矩阵因为 case 配置了 `retries=2`，首轮失败后自动重跑，最终把第二轮 PASS
汇总为整体 PASS。这条结果不能作为零重试稳定性证据。

## 根因与修复

### 1. 测试基础设施掩盖失败

- Core2 6 个 peripheral case 配有 2 或 5 次 retry；
- Core2 device-matrix UI 也配置了 2 次 retry；
- `run_profile_ui_test.py` 只对 radio/unified runner 使用 deterministic
  scheduler，普通 peripheral/UI runner 没有使用。

修复：

- profile UI runner 增加显式 `--deterministic`；
- Core2 6 个 peripheral case 和 UI device-matrix 全部启用；
- 删除 Core2 retry 配置；
- peripheral/device matrix 默认拒绝声明 `retries` 的 case，只有显式
  `--allow-retries` 才允许诊断重跑；
- summary 记录 `attempts` 和 `retry_used`。

### 2. RTC 使用 host wall clock

确定性 guest 的 `time.sleep_ms(1200)` 按 QEMU 虚拟时间推进，而
RX8130/PCF8563 原先用 host `time(NULL)`。guest 的 1.2 秒可能远快于 host
1.2 秒，PCF8563 探针因此报 `did not advance`，red frame marker 会被误判为
touch/power 问题。

修复：

- device realize 时保存 host epoch；
- RTC now = boot epoch + `QEMU_CLOCK_VIRTUAL` elapsed；
- QOM `unix-time` 和 `rtc-offset` 语义保持不变。

新增 QEMU patch：

```text
patches/qemu-m5stack-peripherals/0026-m5stack-rtc-virtual-clock.patch
```

patch 对当前 QEMU worktree 的 reverse-check `PASS`。

## 执行

最终 QEMU：

```text
accel: tcg,thread=single
icount: shift=auto,align=off,sleep=off
memory: -m 0
binary sha256: cb648115dcbc59184663eb15882d2f65960f48d397805f2605dff0a6a945050d
```

最终测试：

```text
UIFlow2 peripheral matrix   67/67 cases, 274/274 checks, all attempts=1
Core2 peripheral group      6/6 PASS, all attempts=1
Core2 peripheral repeat     5/5 PASS, retry_used=false
Core2 UI                    1/1 PASS, flash verified, attempts=1
platform tests              216/216 PASS
runtime coverage            PASS
peripheral catalog          PASS
QEMU profiles               PASS
OpenAPI 3.1 / 1.7.0         PASS
```

Core2 UI 串口证据：

```text
CORE2_LOOP
CORE2_TOUCH 159 182 1
```

Core2 peripheral 串口证据：

```text
CORE2_PERIPHERAL_MAIN
CORE2_RTC 2026-10-22 06:07:08
CORE2_TOUCH 219 189
CORE2_PWR 1
```

最终 matrix 日志扫描未发现 `Guru Meditation`、panic、Traceback、`FAIL` 或
forbidden serial text。

## 边界

本次是 virtual-device validation。它证明当前 QEMU 配置在已覆盖的
Core2 固件/用例上可零重试通过，不证明：

- 物理 ESP32 cache/PSRAM 时序；
- bit-exact Espressif BT controller/baseband；
- RF、coexistence、功耗、声学或光学行为；
- 任意 Core2 或 ESP32 firmware 都具备相同稳定性。

## 回滚

回滚源码提交 `1ef7f0a081cfdc968a816741ca0ed52e18e6b967` 可恢复旧 runner、
retry 配置和 host-clock RTC 模型；没有修改物理设备。
