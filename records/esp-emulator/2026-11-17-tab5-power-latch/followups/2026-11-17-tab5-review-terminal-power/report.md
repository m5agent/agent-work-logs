# 终端关机审核的时序和状态归因

## 现象

相同原版 BIN、规范化 Flash 与虚拟控制器的旧版对照中，审核在观察开始前发出坐标 (672,53) 的 3 秒长按。来宾关机后 Device Service 返回类型化的 HTTP 409，旧版将其记为普通异常。随后保留帧仍可读取，审核把 60.263 秒带保留帧的窗口记为通过。该现象证明审核侧需要区分已启动来宾和预期关闭。

## 修复和验证

仅本地保存快照的触控计划可给最后一个未绑定 A/B 的长按指定终端关机断言。审核先完成运行观察，再核验同一来宾的实时初始状态、带类型的输入结果、关机后的 EN 状态，以及关机前后位置一致的 RGB 裁剪区。触控释放接受标记保持原始响应值。计划结束时不会追加默认坐标探测。

使用原版 Arduventure 1.0.0，原 BIN SHA-256 `e2f228813b719b81c47a8deaa7576f1b83e61e950c6178c5cf570bfaca7b8616`，规范化 Flash `0922e46d70edc11d285fd3d4023a18f061d4d95fd8e7a1729e00702cc3dba063`，native ST7123 Part `655ee4735028357d21ab9341c9d3a6cf14bc6720b6869be763f29b1458feb0a9`。通过保存快照复审入口，仅执行原版电源图标关机计划，坐标 (672,53) 持续 3 秒。60.257 秒运行窗口取得 13 个样本，随后原版关机帧散列为 `84f04dbb5fa1edffcd6acd0977b33aab77d99b8d03bfc951c38d50217f4c0097`。虚拟 EN 从运行转为锁存关闭，证据 ZIP 中的同会话实时末态及文件摘要一致。

审核实现通过 172 项单元与合约测试。详情页用 Chromium 打开保存的实际审核结果，核对新增状态行从报告读取并显示“通过”。两次复审均释放会话、租约和可写 Flash。

## 混合计划兼容性复验

旧运行时没有锁存支持时，普通触控前缀仍按通常时序取证，终端步骤保留 `NOT RUN` 和缺少锁存的原因。回归测试确认只有普通前缀发出一次触控，没有关机动作或后备输入。更新后 173 项合约和单元测试全通过。同一原版 BIN 在合格 Tab5 上重新执行，完整运行窗口结束后仍取得关机帧、实时锁存及 ZIP 证据。[最终复验摘要](evidence/mixed-plan-final-replay-summary.json)

## 复现和边界

在隔离的 Device Service 配置支持 standby latch 的原生 Tab5，绑定原始固件规范化 Flash。向保存快照的复审入口传入审核仓库的 `docs/examples/tab5-arduventure-terminal-power-off.json`，复核 observation、interactions 和 ZIP。后置画面缺失、不同来宾状态或普通 HTTP 409 只能留下未验证结果。

结果只覆盖指定原版电源图标和原生 ST7123 程序。其他已声明交互未纳入关机断言，整个审核仍为 `E_INTERACTION_CLAIM_PARTIAL`。物理电源、其他变体、并发和 Burner 均为 `NOT RUN`。回退可省略关机断言，继续使用既有的单击、长按与拖动计划。

[原生查证](https://github.com/m5agent/m5stack-esp-emulator/blob/5a87913bf60dcde84420661d279ab5e0c9c9154c/docs/evidence/2026-11-17-tab5-power-latch/README.md)
