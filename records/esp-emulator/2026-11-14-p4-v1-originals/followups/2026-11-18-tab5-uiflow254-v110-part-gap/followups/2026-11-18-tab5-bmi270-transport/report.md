# Tab5 原版 UIFlow2 BMI270 大请求与面板路径

## 背景

此前同一份 Tab5 UIFlow2 V2.5.4 在原生 esp-emu 1.1.0 的 GT911 与 ST7123 Part 中均因主机编码长度 8,205 超过 1,024 字节缓冲而退出。实际 I²C 载荷在当时未解码。 [此前精确固件对照](https://github.com/m5agent/agent-work-logs/blob/5a6d032a13e35523cd59034c27372d09c5131287/records/esp-emulator/2026-11-14-p4-v1-originals/followups/2026-11-18-tab5-uiflow254-v110-part-gap/README.md)

## GT911 的有界对照

使用相同原版与规范化 Flash，保留原生 P4、ROM、C6 和 eFuse 哈希。隔离 Part 把缓冲扩大到 16,384 字节，并通过目标 I²C 控制器检查事务。模型对地址 `0x68` 的 `INIT_DATA` 寄存器 `0x5e` 解码出 8,192 字节，逐字节匹配已固定的 BMI270 配置。此回放把此前长度报错与一笔真实的配置传输关联起来。

拒绝和接受两个诊断 Part 分别运行 32.000 秒和 108.001 秒，均捕捉一笔相同配置载荷。接受模式在零配置地址、完整匹配和 `INIT_CTRL=1` 后对 `0x21` 提供初始化完成状态，实测出现一次状态读取。拒绝模式未出现状态读取。两轮均没有新的超长致命报错。

两轮仍各出现一次上游 DSI 零值读回和 GT 面板检测失败，均无有效非黑帧。该对照把 BMI270 配置传输与 GT 的 DSI 读回问题分开。两个证据 ZIP 均验证，隔离会话清零。 [同次对照摘要](evidence/tab5-bmi270-display-comparison-summary.json)

## ST7123 的有界对照

首个 161,506 字节的诊断 Part 超出 147,456 字节的准入上限，在启动客体前被拒绝。编译优化把候选缩至 122,547 字节，保留原准入上限。后续测试使用独立的优化后 Part 和相同原版 Flash。

候选在 108.006 秒内捕捉到 8,192 字节且散列相同的传输，接受模式出现一次初始化状态读回。这轮取得 54 个非黑采样，其中同会话 720×1280 的启动页包含 `UIFlow2`、`V2.5.4`、`Offline`、`Develop` 和 `WEB IDE`，有 628 种颜色和 870,334 个非黑像素。该轮日志没有 DSI 零值读回告警。四个 ZIP，包括准入拒绝对照，均核对哈希与 CRC。

## 复验与边界

使用清单固定原版、规范化 Flash、P4 和 C6 原生运行时。对 GT911 分别选择拒绝与接受 Part，对 ST7123 使用同一上限下的优化接受 Part。隔离会话走实际 I²C 控制器、原生 DSI 与常规 Device Service 证据路径，无用户输入。初始化成功状态是有限的诊断模型，只在完整命中配置和启动控制之后提供。实际传感器行为、触摸、配对、浏览器、实体设备和生产部署尚未执行。所有来宾和服务退出，Flash 与租约释放。 [结构化证据](evidence/tab5-bmi270-display-comparison-summary.json)

## 固定源码证据

主分支的对照摘要保留相同输入和各轮证据。 [版本固定的验证记录](https://github.com/m5agent/m5stack-esp-emulator/blob/9df926ec45ffe1c7d9f91f4b98c58d8b23a40769/docs/evidence/2026-11-18-tab5-stock-frame-comparison/uiflow254-bmi270-diagnostic-summary.json)
