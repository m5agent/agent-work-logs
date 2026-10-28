# ESP Emulator protected WDTFEED 修复与最新 runtime 复测报告

## 背景

- 来源：用户要求继续在 StopWatch、StickS3、Core2 上复测可执行的 UIFlow2
  接口，并把并发测试发现的问题统一解决。
- 现象或需求：设备间并发、设备内串行；保留 stock/matching/candidate
  分层，不把虚拟设备结果外推为物理结论。
- 目标：在包含最新 QEMU 补丁的同一 binary 上重绑系统、外设、协议和候选
  修复，并确认 Core2 legacy startup 是否真正前进。

## 结论

- 状态：`PARTIAL`。`0069` 是通用 watchdog 模型语义修复；UIFlow2
  StopWatch/StickS3/Core2 主路径全部通过，但 Core2 legacy startup 未关闭。
- 根因：classic ESP32 TIMG 旧模型把 `A_TIMG_WDTFEED` 和配置写入一起放在
  `WDTPROTECT` 条件内。ESP-IDF v4.4.8 的 `wdt_hal_feed()` 直接写
  `mwdt_ll_feed()`，合法 feed 不应要求解锁。
- 改动范围：只把 feed 路径移出保护条件；配置寄存器继续要求
  `TIMG_WDT_WKEY_VALUE`。新增从补丁 postimage 提取分支的 C 合同，并修复
  GCC 下内置 `fprintf` 声明冲突。

## 证据

### 代码与配置

- `0069-esp32-timg-wdt-feed-unprotected.patch`；
- C 合同在 protected 状态断言 feed 计数、stage/count 入口和 trace；
- patch reverse-check 对保留 QEMU tree 通过；
- QEMU incremental rebuild 得到 `7855…`。

### 执行

- legacy Core2 public image `4d2d648b…` 在 `runtime=qemu-wifi`、TCG
  `shift=5`、TIMG trace 下观察 60 秒：
  - stage-0 timeout `7.252822559 s`，仍被 mask；
  - stage-1 timeout `17.252822560 s`；
  - 首个 reset `17.252907520 s`；
  - TG1 reset 前 `14,993` feeds，最大间隔 `5.181212 ms`；
  - serial 只有 banner、没有 REPL；frame 仅 `49` nonblack pixels。
- UIFlow2 三台 system/shared：各 `50 PASS + 1 STATE_PASS`、`7/7`；
- 设备组：StopWatch `6/6`、StickS3 `5/5`、Core2 `6/6`，无 retry；
- socket/MQTT/network/EzData 均通过；
- ESP-NOW 与 native ESP-NOW controller DMA loopback 通过；
- StopWatch/StickS3 audio wrapper 通过；Core2 `audio` 不导出；
- requests、Modbus async 和 TLS candidate 在同一 runtime 重新通过；
- Device Service API 和完整平台套件通过。

### candidate 对照

| 项目 | stock | 同 runtime candidate |
| --- | ---: | ---: |
| HTTP `requests2.urlencode` | `15 PASS + 1 FAIL` | `2/2` |
| Modbus async `Loop.sock_recv` | `42 PASS + 8 ERROR` | `50/50` |
| TLS certificate epoch | `3 STATE_PASS + 2 ERROR` | `5/5` |

candidate 是 hash-pinned source 或增量 application 镜像，不替换默认参考
固件。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | patch reverse-check、C 合同、QEMU rebuild、GCC/Linux CI |
| transport | PASS | WiFi/SLiRP owned peers、ESP-NOW controller DMA、audio |
| device_response | PASS | 三台 system/shared/设备组和 serial marker |
| data_behavior | PASS | frame、PCM、协议 peer、QOM、candidate source |
| visual_or_physical | PARTIAL | 虚拟 frame marker PASS；legacy startup 仍黑；物理 NOT RUN |

## 验证边界

全部功能结论是 virtual-device validation。normal-WDT reset 仍存在，不能
把 `0069`、UIFlow2 probe PASS 或单帧非黑描述为 legacy startup 修复。

物理显示、触控、声学、光学、RF、watchdog 电气和真机均为 `NOT RUN`。

## 风险与回滚

`0069` 只调整 feed/configuration 的命令语义，不关闭 watchdog、不改变
timeout 或 reset 时序。回滚功能提交会恢复 protected feed 被丢弃的旧模型
行为；不会影响已经停止并保留的 session 证据。
