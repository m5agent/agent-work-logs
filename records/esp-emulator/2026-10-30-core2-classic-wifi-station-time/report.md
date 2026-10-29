# M5Stack ESP Emulator Core2 classic WiFi station timing and data path 报告

## 背景

- 来源：`RUNTIME-03` legacy Core2 normal-WDT 启动。
- 现象：boot.py 后 WiFi 配置/UI 线程停在连接阶段；classic WiFi 模型的
  timer 使用 host realtime，而 guest scan、DHCP、watchdog 和 frame
  timestamp 使用 virtual time。
- 目标：补齐 classic station 的确定性 timing 和双向数据面，并确认
  legacy normal-WDT 是否因此闭环。

## 结论

- 状态：`PARTIAL`。
- 根因或关键判断：classic WiFi beacon/inject/timestamp 与 deterministic
  guest timebase 脱节；station 分支还包含不转发 guest DHCP 的 synthetic
  path 和 unimplemented host-to-station branch。
- 改动范围：
  - `0093` 将 classic WiFi timer 和 generated 802.11 timestamp 切到
    virtual time，并增加默认关闭的 `M5SW_CLASSIC_WIFI_TRACE`。
  - `0094` 让 `ASSOCIATED`/`STA_DHCP`/`STA_ASSOCIATED` 的 guest data
    正常转换为 Ethernet，host reply 正常返回 guest，并在 DHCP reply 后
    进入 `STA_ASSOCIATED`。
  - Device Service 将 SSID 与认证配置同时传给 classic 和 S3 QEMU WiFi
    NIC。

## 证据

### 代码

- Source patch 1：
  `patches/qemu-m5stack-peripherals/0093-esp32-classic-wifi-virtual-time.patch`
  SHA256
  `ecf7531849e8cf324d2aef151a4acd1c50689363adaa2426a269cefa029cc770`
- Source patch 2：
  `patches/qemu-m5stack-peripherals/0094-esp32-classic-wifi-station-data.patch`
  SHA256
  `bead73ed6918df1a6cac4e5f40cb69c805a004761cc24bdb03c622f40ddce79e`
- Two-commit patch series applies and reverses against the retained QEMU
  source; reconstructed file hashes match the validated build source.

### 构建

Final QEMU：

```text
3e61aa644074598e7b37e2cd9d4e7c1e194d2073b453f4fd9fdc5ffce62738f8
```

QEMU 9.2.2 `xtensa-softmmu` incremental rebuild PASS。

### Stock Core2 WiFi

Runtime：

```text
qemu-wifi / core2-openmac / tcg thread=single / icount shift=5
```

Base firmware：

```text
b228c0e2d877e77a8a352e917ed84f4da8ea92d15b25e28f431a2999620fe3c4
```

Generated firmware：

```text
b57b196fada9cbfd7e41bd1a4e742e8c63935c25dfcc2c0c51b71f1fd5257220
```

五轮独立首启动均为 PASS：

- scan count `3`，识别 `myssid`；
- authenticated/associated；
- DHCP IPv4 `10.0.2.15`；
- controlled HTTP 返回 `HTTP/1.0 200 OK`；
- `CORE2_WIFI_RESULT: PASSED`；
- trace 同时出现 `host-tx`、`host-rx` 和 `STA_ASSOCIATED`；
- evidence SHA256
  `b2559537f3e8fa972f4904241df9f4df115fb629488a93af1177b3d35875c908`。

### 回归

- Core2 UIFlow2 device group：peripherals/audio/mic/power monitor/IMU/
  AXP192 全部 PASS，`6/6`，attempts 1，retry false；
- matrix summary SHA256
  `3533de10b6e4a24730b06203f25124083d2ff763e7225b5ab00b249aba9b6b02`；
- platform `1,609` run，`1,608 PASS + 1 skip`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall、Ruff `E9/F`、patch apply/reverse、PR scope 和 diff check PASS；
- PR #54 两项 workflow 共四个 job PASS。

### Legacy Core2

Public firmware：

```text
4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4
```

Normal WDT、`shift=2`、诊断 `1 us` per-vCPU cap：

- BOARD/APIKEY/boot start/boot done 出现；
- API Key page：`320x240`、`75,559` nonblack、`512` colors；
- frame SHA256
  `737df08a0c5d21fe23a46e38f79b7a580508f8dfa7c63c9bc552be19a3106c96`；
- 随后仍 `TG0WDT_SYS_RESET`。

WDT-disabled 诊断控制无 reset 到 guest virtual
`457.794095092 s`，保留 `reconnect start/finish` 和 API Key 页面；
serial/frame SHA256 分别为 `f2dfc814…` 与 `a8f77474…`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU rebuild、patch forward/reverse、source hash reconstruction |
| transport | `PASS` | stock guest WLAN controller TX/RX、DHCP 与 HTTP |
| device_response | `PASS` | `STA_ASSOCIATED`、IPv4 和 HTTP 200 |
| data_behavior | `PASS` | `host-tx`/`host-rx` 双向 EtherType 及 DHCP |
| visual_or_physical | `PARTIAL` | virtual Core2 API Key page；physical hardware `NOT RUN` |
| review | `PASS` | source/platform/docs contracts、PR scope 与 CI |
| delivery | `PASS` | PR #54 four checks PASS and merged |

## 验证边界

该结果证明 classic WiFi station 的 virtual-time、DHCP/双向 slirp 和
stock Core2 HTTP 数据面。它不证明物理 RF、天线、电气、cache/PSRAM timing、
WPA3、roaming 或 coexistence。

legacy normal WDT 仍在 boot order 后 reset；WDT-disabled 只是诊断控制。
`RUNTIME-03` 的 stable normal-WDT startup、setup/REPL 和用户应用仍 OPEN。

## 风险与回滚

Patch 只改变 classic WiFi timer clock domain、802.11 timestamp 和 station
数据面分支，没有关闭 WDT、修改 timeout、warp 时钟或伪造 host 状态。
回滚为 revert source commit `7965a01c`，重新引入 realtime WiFi timers 与
旧 station 分支。
