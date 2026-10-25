# Core2 exact-time handoff freeze and PC-symbol audit

- 日期：`2026-10-26`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 源码版本：
  [m5stack-esp-emulator @ c9cd5a9](https://github.com/m5agent/m5stack-esp-emulator/commit/c9cd5a93c1ef2ac0046566299879ea69b6d478c9)
- Base commit：`839195866b9cbf82e4e6b0d1a4ed802ea5ce4b9e`
- 环境：macOS arm64；Python 3.13；QEMU 9.2.2 virtual Core2；
  physical hardware `NOT RUN`

## 结论

新增默认关闭的 `0038-esp32-handoff-pause.patch`。它在指定 QEMU virtual time
输出 pause marker 后向 QEMU 自身发送 `SIGSTOP`，从而在不启用高频 PC sampling
的情况下读取两核 PS、INTENABLE、INTSET、interrupt request 和 guest PC。

两段 exact-time 对照得到不同结果：

- `14.800033 s` 早窗口没有固定 PC；
- `15.301447 s` 晚窗口为 CPU0 `0x40087980`、CPU1 `0x40084484`；
- 晚窗口 CPU1 `INTSET=0x40`、`interrupt_request=CPU_INTERRUPT_HARD`；
- 两轮 Serial 都是相同的 507-byte banner-only，SHA 相同。

同一轮还完成了 public BIN 与 local ELF 的同 VMA 字节审计。local
UIFlow2 v2.5.3 ELF 与 public UIFlow_Core2 v1.15.4 BIN 在三个 CPU0 采样地址
上全部 mismatch，因此此前把高频样本映射到 UART ISR/MicroPython VM 的
`REJECTED_BY_BIN_BYTES` 是正式结论。

晚窗口的 BIN 控制流与旧 ESP-IDF Flash block/cache handshake 源码形态一致，
但没有 matching ELF/MAP，不能把 source-pattern candidate 写成已绑定函数。
`RUNTIME-03` 仍为 `OPEN`，legacy 应用仍无同 SHA 非空帧。

## 关键证据

- pause patch SHA256：
  `54a1f6ad5720723cb9c92bc05d60925db330f5977f3ef43477917821cec992b4`
- QEMU binary SHA256：
  `076894c2944205c983f2e19784ac1f9d8ae7a0efda9aa65a8dd648076335cd37`
- pause evidence SHA256：
  `d93568865e79e4430368be866e0785c5c8082cab5e5c2ae6ba4c42155ded5bd2`
- mapping-audit evidence SHA256：
  `1d1d3d063e528595b6d4c85a88b8acbd9d8e19d735ec32f2b21849ff8dbc54fe`
- Core2 UIFlow2 定向回归：`6/6 cases`、`24/24 checks`、零 retry；
- 平台测试：`508/508 PASS`；
- product CI：
  [40236725065](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40236725065)
  的 `platform-contracts` 与 `network-namespace-policy` 均 PASS。

## 文件

- `report.md`：改动、执行、分类、边界和回滚；
- `run.json`：机器可读结果；
- `evidence/core2-handoff-pause.json`：脱敏 freeze、serial 和控制器状态；
- `evidence/core2-pc-mapping-audit.json`：BIN/ELF 同 VMA 字节比较；
- `evidence/verification.summary.json`：验证与 CI 汇总；
- `patches/0001-esp32-handoff-pause.patch`：产品仓库 `0038` 的相同 patch。

## 未覆盖项

- `0038` 后没有重跑完整 UIFlow2 `67-case` 矩阵；
- 没有取得 matching UIFlow_Core2 v1.15.4 ELF/MAP；
- 没有证明具体 cache restore、SSI 或 DPORT 操作是否返回；
- `Core2FactoryTest` 修复后重跑、normal-WDT 非空应用帧和真机都是 `NOT RUN`；
- 物理 cache/PSRAM/Flash timing、RF、电气和 bit-exact BT controller
  不在本记录范围内。
