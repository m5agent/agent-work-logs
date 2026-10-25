# Core2 WDT-off late state and current-state reconciliation

- 日期：`2026-10-26`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 源码版本：
  [m5stack-esp-emulator @ 8d7122b](https://github.com/m5agent/m5stack-esp-emulator/commit/8d7122b79bd6afe43f035e59697f91f8a3e3abc3)
- Base commit：`b07464052a915780e014a12fe6b3ad0f016d8162`
- 环境：macOS arm64；Python 3.13；Node `v22.14.0`；QEMU virtual Core2；
  physical hardware `NOT RUN`

## 结论

`0041` 为 exact-time handoff pause 增加 A0-A15、PS、对象前向指针和有界
stack dump。WDT-off 仅作为诊断 control：45 秒和 120 秒两个独立快照都停在
CPU0 `waiti` `0x4026306e` 与 CPU1 spin `0x40100049`。Flash/SSI 计数在两次
快照间不变，最后活动约在 `43.91-44.00 s`；cross-core writes 继续增长。
因此“Flash 扫描没有终点”和“TG1 feed 停止”不再是当前有效解释，剩余门禁是
late-loop flag/object、normal-WDT TG0 stage-1 reset 和 matching ELF/MAP。

本轮同时重整了当前状态、Backlog、工程交接、代码地图、QEMU/固件矩阵和测试
说明。Backlog 只保留一句已满足基线、当前阻断和五步下一门禁；旧结论
“应用初始化未在 TG0 deadline 完成”和“累计 Flash 吞吐是当前瓶颈”已加入
stale-claim 门禁，避免重新写回当前入口。

## 关键证据

- virtual-device late-state：
  [`core2-wdt-off-late-state.json`](https://github.com/m5agent/m5stack-esp-emulator/blob/8d7122b79bd6afe43f035e59697f91f8a3e3abc3/tests/firmware/core2_handoff_trace/evidence-2026-10-26-core2-wdt-off-late-state.json)
- diagnostic patch：
  [`0041-esp32-handoff-register-stack-dump.patch`](https://github.com/m5agent/m5stack-esp-emulator/blob/8d7122b79bd6afe43f035e59697f91f8a3e3abc3/patches/qemu-m5stack-peripherals/0041-esp32-handoff-register-stack-dump.patch)
- normalized public firmware SHA256：
  `152127c808b9212e3a5b55dd9e0a2d24e71b902e225452b67db381c76caba1cc`
- QEMU binary SHA256：
  `b7ed19e7502e2a04ef48287c3622061ee640077bacc469e571ece5b6f802c1ea`
- source evidence SHA256：
  `0d65913aeeb22bda878d22f4d8fc37f737744670987593393966156e14f648bc`
- platform tests：`522/522 PASS`
- focused docs/Core2 contracts：`36/36 PASS`
- Node UI smoke：`1/1 PASS`；SHA/upload units：`2/2 PASS`
- product CI：
  [run 40244649705](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40244649705)
  的 `platform-contracts` 与 `network-namespace-policy` 均 `PASS`

45/120 秒快照来自同一工作链此前生成并已绑定的 evidence。本次 consolidation
没有重新启动 45/120 秒 QEMU 运行；它验证了 evidence schema、QEMU binary
SHA、patch reverse apply、文档契约和全平台回归。

## 文件

- `report.md`：背景、改动、验证边界和回滚；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：提交、检查、artifact 绑定和 CI。

## 未覆盖项

- 没有新的 45/120 秒 QEMU rerun；
- 没有 matching `UIFlow_Core2 v1.15.4` ELF/MAP；
- normal-WDT legacy 仍无 REPL、无非空应用帧；
- 没有重跑完整 UIFlow2 matrix；
- 没有真机、RF、功耗、物理 cache/PSRAM timing 或电气验证。
