# Core2 exact-time handoff freeze report

## 背景

public `UIFlow_Core2 v1.15.4` 在 Core2 QEMU 中只输出启动 banner，随后进入
watchdog reset 和黑帧。`0037` 已把 cross-core、DPORT/cache、SSI、UART 和
TIMG WDT 统一到 virtual time，但此前的 1 ms PC sampler 会改变调度，不能
证明固定 PC 簇是真实停滞位置。

本轮目标是：

1. 在指定 guest virtual time 无损冻结 QEMU；
2. 读取两核 CPU 状态和 controller register；
3. 验证 local ELF 是否与 public BIN 字节相同；
4. 拒绝任何没有 artifact-bound 的符号结论；
5. 保持 trace-off 默认运行路径和 Core2 UIFlow2 回归。

## 实现

`0038-esp32-handoff-pause.patch`：

- 默认关闭；
- `M5SW_ESP32_HANDOFF_PAUSE_NS` 接受指定 virtual-time deadline；
- deadline 到达后输出 machine-readable pause marker；
- 对 QEMU 自身发送 `SIGSTOP`，保留 LLDB/QMP 可读取状态；
- 不启用 PC sampling，不修改 WDT、SSI 或 cache 行为；
- patch 以 `0037` 后 retained target tree 为前序，不声称可 apply 到裸上游。

新增 `audit_elf_bin_mapping.py`：

- 按 ESP application image segment/VMA 从 normalized 16 MiB flash 提字节；
- 找 local ELF 同 VMA section；
- 输出 BIN/ELF bytes、SHA256、match 和全局 classification；
- 对样本地址先做 artifact hash 校验，避免跨固件复用符号。

## 执行

冻结 batch 使用 public firmware SHA
`18d77e28adfacf7e719a167bd0c3450b78357d13cb1d2f2a8b7bccc2248a909a`，
normalized flash SHA
`152127c808b9212e3a5b55dd9e0a2d24e71b902e225452b67db381c76caba1cc`。

两个 pause target：

| target | event | CPU0 PC | CPU1 PC | 分类 |
| --- | ---: | --- | --- | --- |
| `14.800000 s` | `14.800033 s` | `0x40095aaa` | `0x400977e0` | 无固定 PC |
| `15.300000 s` | `15.301447 s` | `0x40087980` | `0x40084484` | Flash block/cache handshake candidate |

晚窗口 CPU1 的 `INTSET=0x40`，`interrupt_request=CPU_INTERRUPT_HARD`。
两轮 Serial 均为 507 bytes、banner-only，SHA
`e996276519b4f8882739ff1c494dcecba313c99278857a53a984c1c9986a1b62`。

## 地址审计

public BIN 与 local ELF 在以下 VMA 的 16-byte window 全部 mismatch：

- `0x400843ac`
- `0x400843af`
- `0x400843b1`

local ELF SHA：
`5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`。
因此此前映射到 `uart_rx_intr_handler_default` 和
`mp_execute_bytecode` 的结论被拒绝，不再进入当前运行状态。

## BIN 源码形态

只记录 source-pattern candidate：

- CPU0 `0x40087958` 附近清零 `0x3ffc7ec8`、置位 `0x3ffc7ec9`、循环等待
  `0x3ffc7ec8`，与旧 IDF `spi_flash_op_block_func` complete/can-start
  handshake 形态一致；
- CPU1 `0x40084478` 附近清零 `0x3ffc7750/54`，caller `0x40087aec`，
  与 cache handoff 路径形态一致。

这些不是 ELF-bound function names，也不能证明哪一个 cache restore 或
SSI/DPORT 操作未返回。

## 验证

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU patch 后 binary 固定 SHA；compileall、Ruff、Node、profile checks |
| transport | `PARTIAL` | pause marker、LLDB state、serial 和 trace 均取得 |
| data_behavior | `PASS` | exact-time register/PC state 和 BIN/ELF byte mismatch 可重复计算 |
| regression | `PASS` | Core2 UIFlow2 `6/6 cases`、`24/24 checks`，零 retry |
| documentation contract | `PASS` | 平台 `508/508`、docs `41/41`、QEMU profile `19/19` |
| legacy application | `FAIL` | normal WDT reset、banner-only、无非空应用帧 |
| delivery | `PASS` | product commit `c9cd5a9`；CI `40236725065` 两 job PASS |
| full matrix | `NOT RUN` | `0038` 后只跑 Core2 定向组 |
| physical hardware | `NOT RUN` | 无真机、电气、RF 或物理 cache/PSRAM 测量 |

## 验证边界

- 所有结果都是 `virtual-device validation`；
- `SIGSTOP` 是读取状态的唯一诊断扰动，不进行高频采样；
- 早窗口和晚窗口状态不同，不能把先前 sampler PC 簇当作固定事实；
- source-pattern 不能替代 matching ELF/MAP；
- `M5SW_DISABLE_WDT`、bulk bypass、accelerator override 和 probe PASS
  都不是 legacy 应用 PASS；
- 没有物理 cache/PSRAM/Flash timing、RF、功耗或电气结论。

## 风险与回滚

没有烧录、擦除或持久设备状态修改。`0038` 默认关闭；仅显式设置
`M5SW_ESP32_HANDOFF_PAUSE_NS` 时暂停 QEMU。回滚 product commit
`c9cd5a93c1ef2ac0046566299879ea69b6d478c9` 可恢复正常运行路径。
retained QEMU worktree 含既定板级修改，不能 reset/clean。
