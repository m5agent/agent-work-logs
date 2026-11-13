# C6 普通 GPIO 中断传递修复

- 日期：`2026-11-14`
- 结果：`PARTIAL`（声明范围内的 GPIO 修复通过；完整矩阵与原版应用限定非回归已补充；Honeypot 网络功能与额外 IRQ 模型仍有限制）
- 工作类型：`code_change`
- 问题来源：用户要求模拟器行为与真实固件 API 一致；无新外部 issue 回复。
- 源码版本：`m5agent/m5stack-esp-emulator @ b7a312268389dee1729c70bbbee960672adf393c`；此为受审提交，最终 main 为 `70ef503fc2fb8b2c787fa9065e2952f525c40099`，实际执行源码单独保留。
- 环境：原生 QEMU ESP32-C6；`virtual-device validation`，非实物电气测量。

## 结论

旧 C6 GPIO 模型能更新输入电平，但未把普通 GPIO source 30 传递至 CPU ISR。
修复后，同一 ESP-IDF 固件的 NanoC6 21/21、Nesso 26/26 检查通过；原版 Nesso
UIFlow 可执行分区不变，仅注入 VFS 测试程序，同一会话两轮共 32/32 检查通过。
旧运行时对应 12/21、14/26、20/32 功能 FAIL 完整保留。禁用、保持和实际源电平
负控通过，回调计数只由真实固件 ISR / `machine.Pin.irq` 增加。

## 关键证据

- 构建：新独立 C6 runtime 与固定 ESP-IDF v5.5.4 工程；更早不完整 SDK 构建失败保留。
- 固件：逐板旧新使用同一镜像；UIFlow 原版、VFS 合成和可执行分区哈希分别记录。
- 执行：IDF 走已登记 direct-QEMU 回归；UIFlow 走普通 Device Service session。
- 原始数据：离线复核原始串口、QMP/UART 输入、ZIP 八项文件、Flash 可执行分区、结果帧和清场。
- 来源限制：服务源码绑定为事后审计；基线期间发生仅测试文件的 cherry-pick，不宣称预先冻结。

## 文件

- [report.md](report.md)：根因、实际执行与边界。
- [run.json](run.json)：结构化执行摘要。
- [evidence/](evidence/)：有界脱敏派生摘要；完整原始 ZIP、Flash、输入和串口仅私有保留。
- patch / 可重建代码：使用受审源码内 `tests/firmware/esp32c6_gpio_irq/` 与 `tests/uiflow2/nesso_gpio_irq/`，本记录不复制第三方固件或二进制。

## 未覆盖项

完整原生矩阵 70/70 已独立复核；原版固件非回归已分层追加；线上 Pages、物理硬件、NMI/source31、
睡眠唤醒/过滤器时序、BMI270 IRQ 和 FT6336 脉冲时序不由本记录证明。IDF Service lane
及 UIFlow 在线程序 API 未运行。未提交 Burner。

最终主分支和 CI 已通过，固定最终源码的普通 Service 路径另完成 32/32 功能复验。
本记录只发布功能与产物证据；本地部署操作另存内部记录，原有失败保持不变。

完整原生矩阵 follow-up：70/70，逐case仅一次、无重试；实际执行源码为 `0e00cdcbc99a8210af6485df1bcfd04a514bc8a1`。523个相关实现文件与整合候选逐字节一致，后继候选仅18个docs路径变化。422个产物哈希、70份原app分区、70组帧和77次离线解码重新核对；guest清场为0。详见新增两份bounded审计，不复制超过大小预算的原始aggregate。

原版固件 follow-up：Mesh A 长按/短按 150 秒 8/8，视觉 Welcome→Back→US；Bruce 150 秒 6/6，视觉 Clock→reset WiFi；Honeypot 180 秒 7/7 控制台通过但 AP/HTTP 未运行。Mesh B 150 秒 5/6、选择画面不变的 FAIL，以及更早旋转尺寸/TIME_WAIT 观察器 INFRA 均完整保留。A 正控不覆盖 B 负观察或初次失败。四个完整窗口逐份核对运行中 ZIP、原 app 字节、实际输入、清场和哈希。

最终源码复验：在主分支 `70ef503fc2fb8b2c787fa9065e2952f525c40099` 上，通过普通 Device Service
重新运行同一份原版 Nesso 可执行代码与 VFS 探针。32/32、22 次输入、一次重置、两轮各六次
真实回调及 135×240 绿色 PASS 帧均通过，原 app 分区不变。见
[最终功能证据](evidence/final-main-c6-functional-summary.json) 和
[最终 main CI](evidence/main-ci-completed-summary.json)。

复现入口：[固定源码中的 GPIO 探针与命令](https://github.com/m5agent/m5stack-esp-emulator/tree/70ef503fc2fb8b2c787fa9065e2952f525c40099/tests/firmware/esp32c6_gpio_irq)、
[原版 UIFlow VFS 探针](https://github.com/m5agent/m5stack-esp-emulator/tree/70ef503fc2fb8b2c787fa9065e2952f525c40099/tests/uiflow2/nesso_gpio_irq)。
