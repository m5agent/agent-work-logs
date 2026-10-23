# Core2 native HCI 完整 sequence 诊断

- 日期：`2026-10-24`
- 结果：`FAIL`（`HCI-3b` 门禁）；transport/C2H 切片仍为 `PASS`
- 工作类型：`code_change` / diagnostic
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码基线：`9aa3fd71e9ad0b0002cd3e06f4e12038a833d703`
- 基线诊断提交：`32862edf3998cae4d4b62464c51af295761c330d`
- safe-point follow-up：`b6aa8c8231111d1ef40cd31f40d103445ebb49d0`
- controller-entry follow-up：`07df1ffd6f3385a0dedf4c8e7bf663aa81785f73`
- baseline CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40025648490>
- controller-entry CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40026818206>
- 环境：macOS Apple Silicon；QEMU m5core2；stock UIFlow2；Bumble controller/peer

## 结论

新增了无 GDB、真实 Bumble controller/peer 的完整 native-HCI 诊断：

- 广播发现 PASS；
- BLE connect PASS；
- 首个 ATT Read By Group Type request/response 双向通过；
- Bumble 发出第二个 ATT request；
- guest 随后报告 `NimBLE: HCI process ack returned 12`；
- guest 再发 HCI Reset `01030c00`；
- Bumble 最终 `GATT timeout for ATT_READ_BY_GROUP_TYPE_REQUEST`。

因此 `HCI-3b` 没有完成，不能宣称完整 HCI/GATT。

## 根因收敛

本次排除了几个原假设：

- H4 RX parser 没有错位；
- 所有已交付 callback 都返回 status 0；
- 有效完整 H2C 包和 Bumble C2H 包都走到了正确 transport 侧；
- QOM `malformed-packets` 中的 73 次来自 VHCI length 字段的非最终写入，
  不是 C2H/H4 数据损坏；
- 单纯固定 CPU0、允许任意 CPU0 safe point、或取消 RX 丢弃都没有修复。

剩余失败边界是 controller response transaction，以及进入 firmware callback
时使用的 vCPU safe point/context。下一步需要建立与真实 controller-to-host
通知等价的事务生命周期，而不是继续加 sleep 或 retry。

### Safe-point follow-up

在任意 CPU0 safe point 调用 callback 前，额外保存/恢复 `SAR`、`LITBASE`、
循环寄存器、`M0-M3`、`THREADPTR`、`ATOMCTL`、`CPENABLE` 等
caller-saved 特殊寄存器仍未解决。guest 在 BLE 初始化阶段两次
`ack returned 12`，随后 `LoadProhibited` 崩溃。实验已回退，说明问题不是
遗漏少量 CPU 寄存器，而是 direct nested callback 不具备通用
controller-to-host 注入语义。

### Controller-entry follow-up

进一步定位到 firmware 的真实 C2H 路径：

```text
r_eif_send -> vhci_send -> registered notify_host_recv -> VHCI flow
```

把 `r_eif_send` 当作 nested guest RPC 调用时，即使提供真实 completion stub，
guest 仍触发 `Cache disabled but cached memory region accessed`，callback
没有正常返回。实验已回退。

因此最终实现必须是设备/IRQ 事件或 in-process controller，不能从 QEMU device
callback 同步调用 guest controller 内部函数。

## 关键证据

- 新增 runner：`tests/uiflow2/core2_native_hci/run_full.py`；
- diagnostic evidence：
  `tests/uiflow2/core2_native_hci/evidence-2026-10-24-hci3b-diagnostic.json`；
- firmware SHA256：
  `906ba16439f8f8b421adb9ba3817ebf91d677498b0096c38e851a63570a8b680`；
- ELF SHA256：
  `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`；
- QEMU SHA256：
  `ea8ea3a121a8e069686e06c7c267264ec04511cbb34be0e485799dd925a99fb0`；
- transport `11/11 checks PASS`；
- 恢复基线后的 HCI-3a 单包 C2H callback PASS；
- QEMU native-HCI source 与仓库 patch reverse-check PASS。

## 文件

- `report.md`：完整实验、对照和结论；
- `run.json`：结构化失败记录；
- `evidence/verification.summary.json`：transport、C2H、HCI-3b 和 CI 聚合；
- `evidence/followup-safe-point-audit.json`：特殊寄存器 audit 和 guest crash；
- `evidence/followup-controller-entry-audit.json`：真实 C2H 内部入口与 cache fault；

## 未覆盖项

- complete HCI/GATT、NUS subscribe/write/notify；
- Device Service repeated lease；
- bit-exact ESP32 BT controller/baseband；
- 物理硬件。
