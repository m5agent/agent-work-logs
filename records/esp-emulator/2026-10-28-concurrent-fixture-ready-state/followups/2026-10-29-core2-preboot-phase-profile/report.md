# Core2 legacy pre-boot phase profile 报告

## 背景

- 来源：`RUNTIME-03` normal-WDT reset 继续阻断 legacy UIFlow；
- 现象：WDT-off 可以继续推进，但没有 matching ELF/MAP，
  既有 PC 采样只得到少量地址簇；
- 目标：把 PC、UART virtual time、SSI 和 cache/cross-core 活动绑定到
  同一 80 秒 WDT-off 控制，并验证立即切核是否可行。

## 结论

- 状态：`PARTIAL`，诊断里程碑；
- guest 在 80 秒内没有永久 deadlock，完成了 banner、BOARD/APIKEY 和
  `boot.py`；
- 主要 CPU0 样本落在 Flash/cache handoff 簇；
- SSI 有约十万个 transaction，最后 payload 为 64 bytes；
- normal-WDT reset 仍远早于 BOARD NAME；
- 所有立即切核控制都没有改善，未进入主线；
- `RUNTIME-03` 保持 `OPEN`。

## 工具修复

`run_pause_sweep.py` 新增：

```text
--pc-sample-ns
--uart-trace
phase_profile
```

此前 runner 会解析 UART TX 行，但正式执行没有打开
`M5SW_UART_TRACE`；外部环境设置 PC sampling 时，evidence 仍固定写为
`NOT RUN`。本次把两者改成显式控制，并加入合同测试。

## 执行

```bash
PYTHONPATH=.work/py python3 \
  tests/firmware/core2_handoff_trace/run_pause_sweep.py \
  --image .work/runtime03-original-vfs-probe/image.bin \
  --expected-image-sha256 4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4 \
  --pause-seconds 80 --disable-wdt --runtime qemu-wifi \
  --icount-shift 5 --pc-sample-ns 50000000 --uart-trace \
  --timeout-seconds 300 \
  --out-dir /tmp/core2-preboot-phase-profile
```

同一固件另跑 normal-WDT liveness：

```bash
PYTHONPATH=.work/py python3 \
  tests/firmware/core2_handoff_trace/run_wdt_liveness.py \
  --image .work/runtime03-original-vfs-probe/image.bin \
  --expected-image-sha256 4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4 \
  --qemu .work/M5StopWatch-QEMU/build/qemu/build/qemu-system-xtensa \
  --observe-seconds 60 --attempts 1 --trace-sample 1024 \
  --runtime qemu-wifi --icount-shift 5 \
  --out-dir /tmp/core2-normal-wdt
```

## 观察

### UART virtual timeline

| Marker | Virtual time |
| --- | ---: |
| banner complete | `2.7724 s` |
| BOARD NAME | `54.9924 s` |
| APIKEY | `54.9971 s` |
| boot.py start | `77.8622 s` |
| boot.py done | `78.3712 s` |

### PC profile

50 ms sampling，共 `1,599` 点：

- CPU0 `0x4026306e` waiti 形态：`496` 点，`31.0%`；
- CPU0 `0x40087980..8e` handoff 簇：`965` 点，`60.4%`；
- CPU1 高频地址集中在中断分发/SSI 路径，缺少 matching ELF/MAP，
  不作函数名声明。

### Controller counters

| Counter | Value |
| --- | ---: |
| SSI transactions | `103,058` |
| SSI RX bytes | `3,181,984` |
| Last SSI command | `0xBB` |
| Last SSI payload | `64` bytes |
| DPORT cache-sync | `215,836` |
| Changed pages | `5,911` |
| Cross-core writes | `428,205` |

### normal WDT

- stage-0 timeout：`7.2536 s`；
- stage-1 timeout：`17.2536 s`；
- first reset：`17.2537 s`；
- TG1 `14,998` feeds，max interval `3.927 ms`，`0` timeout。

## 否定控制

所有以下修改都已丢弃：

1. high-priority memw/retw 全部立即退出 TB；
2. 仅 CPU1 handler 首次立即退出；
3. cross-core 写时退出当前 TB；
4. SPI `TRANS_DONE` 时退出当前 TB。

负控说明 simple scheduler tweak 不是产品修复；下一步应针对
64-byte read cadence 本身的 guest/controller 来源。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | 主仓 CI `40732335677` 两 job 成功 |
| transport | `PASS` | 真实 ESP32 I2C/SPI controller trace、UART VTX、SSI counters |
| device_response | `PARTIAL` | WDT-off 达到 BOARD/APIKEY/boot.py；normal-WDT 提前 reset |
| data_behavior | `PARTIAL` | 64-byte read-class transaction cadence 定位，来源仍未区分 |
| visual_or_physical | `NOT RUN` | 无完成应用帧；物理边界不验证 |

## 验证边界

PC sampling 会改变宿主调度，WDT-off 也不是产品配置。本记录只提供
virtual-device 诊断；没有 matching ELF/MAP，也没有证明物理 Flash、
cache、PSRAM、RF、电气或真机时序。

## 风险与回滚

本次主线改动只修改 runner、合同测试和文档；QEMU 实验性调度修改均已
回滚，不进入产品 runtime。若需回滚文档/工具提交，可反向提交
`419235e9`；旧 evidence 不覆盖。
