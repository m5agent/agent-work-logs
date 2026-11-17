# 原版 Arduventure 的关机与重启

旧 Part 按寄存器读写回传扩展器输出。原版关机长按能画出 POWER OFF，但仍会发送多次关机脉冲，新 Part 按官方原理图的数字语义，将 PI4IOE2 P4 的输出边沿接入原生 EN。

## 验证

使用新的隔离 Device Service 会话导入原始固件。720×1280 DSI 无 ELF 取帧显示原版标题。短按电源图标和外部区域长按均未关机。对电源图标长按 3 秒，HP I²C1 上地址 0x44、寄存器 0x05 首次有效写入 0x99，跟踪捕获 Part 的 EN 拉低请求及 688 ns 后的低电平回报。2.4 秒墙钟观察时串口内容不变。API 和 ZIP 的 power receipt 一致，关机后的触摸得到类型化回执。显式复位后返回原版标题。两个原版会话均释放 Flash 和租约。

配置首次尝试因本地运行时依赖路径缺失未启动。补齐运行资产后发现新 Part 超过旧接收上限。修复后的二次原版对照及独立签入脚本均通过。旧负控的原版结果已保留。

[原版和运行时哈希](evidence/gateway-power-summary.json) · [源码与测试说明](https://github.com/m5agent/m5stack-esp-emulator/blob/2a4edd56d1e7023e7fef30026f3760a4a083b24e/docs/evidence/2026-11-17-tab5-power-latch/README.md)

## 并发回归期间的对照

组合版与全套平台测试并行时，原版再次通过 I²C 和 EN 关机。原生 co-sim 报告传输丢帧，保留的最后完整帧早于关机帧。严格画面断言失败，测试释放会话与 Flash。该次运行的重启验证未执行。[复验摘要](evidence/concurrent-replay-summary.json)

## 边界

本记录验证模拟器 EN 与同会话语义。当前模型跨接数字逻辑，物理供电、背光关断、电流、其他 Tab5 变体和浏览器证据未运行。回退到旧 Part 可禁用本次关机锁存。Burner 未提交。
