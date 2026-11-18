# Tab5 原版 UIFlow2 V2.5.4 在 esp-emu 1.1.0 的双 Part 对照

## 背景与目标

已有 Tab5 原版启动记录。本轮将同一份 V2.5.4 BIN 和同一份规范化 Flash 放入两个全新的 Device Service 会话，使用冻结的原生 esp-emu 1.1.0 验证 GT911/ILI9881C 与 ST7123 两套 Part 配置的首次终止点。 [既有问题](https://github.com/m5agent/m5stack-esp-emulator/issues/188)

## 观察

两轮均产生一次 ROM 启动横幅，然后在 Part I²C 传输中退出，退出状态均为 1。主机日志报告控制器端口 1、地址 `0x68` 的**编码请求长 8,205 字节**，超过配置 Part 的 1,024 字节缓冲区。8,205 是主机封装值。客体实际发送的总线事务字节数未测量，首次长度异常由客体还是传输层引入仍待定位。

GT911/ILI9881C 轮报告面板未检测到，帧端点没有可用画面。ST7123 轮取得一张 720×1280 的全黑 DSI PNG。两轮均未出现 MicroPython 横幅，也没有记录客体 panic。早期旧 CSR 字样在这段短窗口未出现，CLIC 兼容性仍保留。

## 复验步骤

1. 使用清单所列原版与规范化 Flash 哈希固定输入，并固定 P4 runtime、ROM、C6 配套镜像、eFuse 和每套 Part。
2. 通过 Device Service 分别启动两个隔离 Tab5 原生 DSI 会话，记录启动串口、Part stderr、帧采样和终态。
3. 把运行时失败保留为 `failed`，核对 ZIP 校验与文件清单，确认来宾进程消失、可写 Flash 释放和租约清零。

## 验收与边界

镜像准入通过。Part 传输和原版应用持续运行失败。可用画面未达标，触摸、浏览器及实体设备为 `NOT RUN`，Burner 未提交。原始回放的终态观察器一度使用了过严的终止枚举，留存的失败历史与独立回读确认两轮实际终态和清理。当前记录属于原样复跑，无产品改动需要回滚。 [结构化证据](evidence/tab5-v110-comparison-summary.json)

## 固定源码证据

执行结果和公开数据快照对应同一组固件与运行时哈希。 [主分支验证记录](https://github.com/m5agent/m5stack-esp-emulator/blob/174c6d42048bf12f315e8b572948f17638d0bb77/docs/evidence/2026-11-18-tab5-stock-frame-comparison/uiflow254-v110-summary.json)
