# ESP Emulator Core2 HCI-3b API-Boundary 报告

## 背景

`HCI-3b` 的目标是让 stock Core2 固件通过 QEMU 内的 VHCI backend 完成完整的
外部 Bumble HCI/GATT 序列，不依赖 GDB callback injection 或 synthetic return。

此前 native-HCI 在第二个 ATT request 后触发 `HCI process ack returned 12` 并
Reset；直接 safe-point callback 和 nested `r_eif_send -> vhci_send` 都已证伪。
本阶段要回答：为什么 GDB 诊断桥能跑到完整 GATT，而 QEMU device 路径不能。

## 发现

### H2C 所有权冲突

GDB bridge 在 `API_vhci_host_send_packet` 入口截获 H2C，然后立即跳过原函数。
因此固件内部 controller 不处理该 packet，HCI controller 只由 Bumble 表示。

原 native-HCI 只监听 VHCI shared-memory length write。它虽然捕获了相同字节，
但固件内部 controller 同时继续执行，于是两个 controller 状态机竞争同一
transaction。该差异比 H4 字节解析或 C2H queue 抖动更早发生。

### Xtensa 返回语义

API 断点位于函数 `entry` 指令之前：

- PC：`0x403064d8`；
- wrapper call site：`0x402670a8`；
- breakpoint 前后 `WINDOW_BASE` 都是 `0xf`；
- 返回地址位于 next window，但当前 live window 仍属于 caller。

第一版 QEMU hook 在 pre-entry 点执行 Xtensa window rotation，随后出现
`Cache disabled but cached memory region accessed`。修正后只读取 next window
中的返回地址并恢复 live window，返回语义与 GDB 一致。

### 实验性 API hook

修正返回语义后，使用 QEMU CPU 内部 hook 完成：

1. 在真实 API entry 读取 `(data_pointer, length)`；
2. 从 guest memory 复制 H4 packet；
3. 发送到 Bumble；
4. 返回 wrapper call site；
5. 在同一 transaction 内暂停 guest，等待匹配 C2H；
6. 交付 C2H 并调用 send-available；
7. 恢复 CPU。

最好的一次运行已经完成 advertisement、connection、NUS service discovery 和
CCCD subscription，Bumble 也发出了 NUS write。该轮没有 H4 malformed packet
或 dropped packet，但最后一个 guest write/notification callback 未完成。

不同 callback 预算和 send-available 调度策略只改变失败点，没有实现稳定 GATT。
因此实验代码未保留，也没有把 partial 结果提升为 `HCI-3b PASS`。

## 验证结果

| 检查 | 状态 | 依据 |
| --- | --- | --- |
| 原 internal-controller relay | FAIL | 第二个 ATT request 后 ACK 12/Reset |
| API MMIO `retw` overlay | FAIL | Xtensa cache-disabled panic |
| pre-entry API hook + correct return | PARTIAL | 广播/连接/NUS discovery/subscription PASS |
| NUS write | PARTIAL | peer 已写入；guest ACK/notify 未完成 |
| H4 parser/drop in best API-hook run | PASS | malformed 0、dropped 0 |
| platform suite | PASS | `264/264` |
| GitHub Actions | PASS | run `40041254086`，head `e5fbf39` |
| physical hardware/RF | NOT RUN | 无真机验证 |

## 验证边界

- 实验性 QEMU patch 未提交，因为完整 `HCI-3b` 仍失败；
- 本轮只记录可复现的边界和计数器，不把部分 ATT 交互当作完整 GATT；
- 没有设备服务 repeated lease；
- 没有 bit-exact controller/baseband 或 RF 行为。

## 风险与回滚

本轮只提交 evidence 和文档。QEMU 实验改动已移除，tracked QEMU 文件恢复为
实验前状态；没有设备、Flash 或外部服务状态变更。

## 下一实现

实现显式 controller transaction 状态机：

1. 在 API entry 建立 H2C transaction ID；
2. QEMU device 队列保存 H2C/C2H packet、status 和 flow-control；
3. guest ISR/task 消费 controller-to-host queue，而不是嵌套 `cpu_exec()`；
4. `notify_host_recv` 与 `notify_host_send_available` 只在该 transaction
   生命周期内调用；
5. 完整 GATT 稳定后提交 QEMU patch，再做 `HCI-4` Device Service `5/5`。
