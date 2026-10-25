# ESP Emulator Core2 equal-deadline timer fix and current-state refresh

- 日期：`2026-10-26`
- 结果：`PARTIAL`（minimal probe timer 与文档/契约 PASS；legacy UIFlow 与
  hardware validation `NOT RUN`/`FAIL`）
- 工作类型：`code_change`
- 问题来源：用户要求完整整理代码和文档，结合后续 Core2 timer/WDT 工作修正
  过期页面，并说明当前工作与待办
- 源码版本：
  [m5stack-esp-emulator @ c3193b9](https://github.com/m5agent/m5stack-esp-emulator/commit/c3193b92cc46b41a7dc8574089fc2b95df37caa4)
- Base commit：`1b923f83d6906545879e16262aaa3b3e10cc7c74`
- 环境：macOS arm64；Python 3.13；ESP-IDF 5.5.4；Core2 QEMU
  virtual-device；物理硬件 `NOT RUN`

## 结论

最小 `core2_flash_ipc` probe 在 `CORE2_FLASH_IPC_READ_START` 后捕获到一个
generic Xtensa timer 缺陷：timer ISR 在最后相等窗口写入
`CCOMPARE == CCOUNT` 时，旧 QEMU 把下一次到期算成 `2^32` ticks。在 Core2
上这约为 `26.8 s`，超过 interrupt-WDT 窗口。

新增业务补丁只处理相等期限：`CCOMPARE == CCOUNT` 安排到下一 cycle，其他
delta 继续保留原有 32 位回绕语义。补丁不包含 IRQ ring、trace、timeout 放宽、
retry 或 QOM pause。修复版四批合计 `40/40` 首启动完成全部 CPU1 partition
reads；更新后的真实 Device Service runner 再测 `3/3 PASS`，旧错误镜像被默认
SHA 门禁在上传前拒绝。

该修复没有关闭 legacy UIFlow。同一公开固件仍出现
`TG0WDT_SYS_RESET`/`TG1WDT_SYS_RESET`、reset CPU PC `0` 和同一 black frame。
`RUNTIME-03` 因此保持 `OPEN`，下一项是 legacy TG watchdog feed/clear、
IDLE/service task 饥饿及 flash-cache/IPC/DPORT 交接。

## 关键证据

- Image SHA256：
  `c2762e5f34d513e34a47739174fd452567f2f3ec87164a4d421a1a7141c68359`；
- ELF SHA256：
  `7636c3e5aa182621f9998e12938a2e037adf99689f7d1b7e5c154a7892aaf88b`；
- 修复版 `40/40 PASS`，`0` interrupt-WDT、`0` spinlock assertion、`0`
  reboot；包含 trace 开关与 `icount shift=5/auto` 对照；
- 新版 runner `3/3 PASS`；旧镜像 SHA 不匹配时 exit `2`，未上传；
- 平台测试 `500/500`，所有生成/契约/静态检查 PASS；
- 产品补丁在 clean base 上 forward/reverse apply check PASS；
- 产品 CI
  [`40218210901`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40218210901)
  的 `platform-contracts` 与 `network-namespace-policy` 均 PASS；
- legacy 17 个采样帧均为同一 302-byte black PNG，仍发生 TG0/TG1 reset。

## 文件

- `report.md`：根因、修复、验证、边界与回滚；
- `run.json`：机器可读结果；
- `evidence/equal-deadline-summary.json`：脱敏的 pre/post、runner、legacy
  和验证摘要；
- `patches/0001-xtensa-ccompare-equal-deadline.patch`：可重放的最小 QEMU
  业务补丁。

## 未覆盖项

- legacy UIFlow 的 TG0/TG1 watchdog 根因仍未定位；
- 相同 legacy firmware 仍未产生非空应用帧；
- 没有执行 Core2 全量外设矩阵或其他设备矩阵；
- physical timer/cache/PSRAM、RF、功耗、电气和真机均为 `NOT RUN`。
