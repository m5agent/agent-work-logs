# ESP Emulator PR #14 合并与 Core2 启动复验报告

## 背景

- 来源：公开 issues #2/#3 与 PR #14。
- 需求：合并解决剩余 Core2 issue 的 PR，然后在新版模拟器上独立确认问题是否
  已解决。
- 基线：`a0ad8150b112afe1273100514c7ef0808bd4477b`。
- 合并：`47af9e76f89912028db6d9dee0b0bcc5425c852`。

## PR 审阅

PR #14 增加：

- Core2 无显式 NIC 时仍实例化 radio-disabled 的片上 WiFi
  MAC/MMIO/DMA/IRQ；
- 普通 Core2 session 使用与 radio session 相同的 deterministic TCG/icount；
- SPI panel DMA 仅在 `USR` transaction 消费 descriptor/FIFO，避免
  `OUT_LINK` 与 `USR` 双消费；
- 对真实 UIFlow2 display、Widgets、LVGL、offline network，以及显式 WiFi
  两 session 的可见 Device Service runner。

首轮 CI 的 `platform-contracts` 失败为 test-only C harness：

```text
error: operand of '?:' changes signedness ... [-Werror=sign-compare]
```

Contributor follow-up `d0bdd33f` 将 MIN helper 两个条件结果都转为
`uint64_t`，未修改 runtime。之后 Linux CI 两 job 全绿，PR mergeable/CLEAN。

## 独立冷构建

从合并版源码重新 clone 固定 QEMU commit，并按 `bootstrap-unit-runtime.py`
重放 17 patches：

```text
QEMU base: 40edccac415693c5130f91c01d84176ae6008566
patches: 17
source files: 109
runtime SHA256: bcd439bc57bae37834b784933585c697e3e5d9e7226955159fc7cd2272931dbc
source receipt SHA256: bc9b3986b7622740bfe8a892abb0ae81e30fee75c4b7ef21220a5dbae380fdcd
```

`bootstrap-unit-runtime.py --check` 返回 `source_status=verified`，QEMU
`-M help` 包含 `m5core2`。

## 执行

独立 Device Service 使用新的状态目录启动，并显式设置合并版 QEMU binary 与
ROM 目录。所有 guest 执行都创建 `/api/v1` 可见 session。

### 启动矩阵

`run_service_test.py --case all`：

| Case | 状态 | Session | Frame |
| --- | --- | --- | --- |
| display | PASS | `663a03a419fe401abdd58ba6e710e128` | 320×240，16 colors，`b42b50d7…` |
| widgets | PASS | `60fee63cb7d645dc921f9b2dd5ffa1dc` | 320×240，30 colors，`114719e1…` |
| LVGL | PASS | `60706ac5dcce449fad51dc97257d6b7a` | 320×240，正常字形，`591fae89…` |
| network | PASS | `90abdefdb3af488ca03051bebde1b4c5` | 320×240，16 colors，`479ae992…` |

LVGL screenshot 已人工打开检查，画面为：

```text
Core2 LVGL first frame
```

offline network serial：

```text
CORE2_STARTUP:network:ACTIVE True elapsed_ms 181
CORE2_STARTUP:network:CONNECTED False
CORE2_STARTUP:network:NTP_ERROR OSError(118,) elapsed_ms 1
CORE2_STARTUP:network:READY
CORE2_STARTUP:network:DONE
```

### 显式 WiFi

`run_radio_service_test.py --execute`：

| Attempt | 状态 | Session | Pcap |
| --- | --- | --- | --- |
| 1 | PASS | `994adbdcf6d244dda1199d32347ab1b4` | 35 packets，DHCP DORA，2 TCP flows |
| 2 | PASS | `838cfdac40474a7b8f58a3daf4115da9` | 35 packets，DHCP DORA，2 TCP flows |

两次 session 使用同一 firmware、不同 session/process，均通过 scan、
association、DHCP、受控 HTTP、双向 payload、ZIP、历史保留、Flash release 和
PID cleanup。

radio headless probe 的 framebuffer 仍是 issue #2 的 302-byte 黑帧
SHA `57580743…`，但该 runner 不把 headless framebuffer 当显示 PASS；显示
由 startup 的 display/Widgets/LVGL cases 独立证明。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | fresh clone、17 patch replay、cold Xtensa build、receipt check |
| flash | `PASS` | 指定 stock UIFlow2 base 的 merged image 可由 service 装载 |
| transport | `PASS` | UART markers、WiFi scan/associate、DHCP、HTTP、pcap |
| device_response | `PASS` | WLAN active/isconnected、LVGL/Widgets 完成 marker |
| data_behavior | `PASS` | QOM radio state、bounded NTP error、DHCP/TCP payload |
| visual_or_physical | `PASS`（virtual visual） | 非黑 frame 与实际可读 LVGL 标题 |
| delivery | `PASS` | PR #14 合并；public record 固定 |
| private_complete_apps | `NOT RUN` | archives unavailable |
| full_matrix_independent_rerun | `NOT RUN` | not repeated in post-merge run |
| physical_hardware | `NOT RUN` | virtual-device validation only |

## 验证边界

- 公开最小 startup 路径已经闭环，因此 issue #2/#3 的 simulator boundary
  可以关闭。
- 不声明四份私有完整应用的业务逻辑、外部 LAN endpoint 或全部初始化路径。
- 不把虚拟 WiFi 数据面当 RF、天线、信道、速率、功耗或电气验证。
- 旧 UIFlow1 LVGL7 `RUNTIME-03` 仍是独立问题。

## 风险与回滚

所有 session 已停止，Flash 未保留；历史 session/serial/frame/evidence ZIP
保留在本地状态目录。物理设备未改动。源码回滚可 revert merge
`47af9e76f89912028db6d9dee0b0bcc5425c852`；runtime 由 source receipt 和
17-patch 栈重建。
