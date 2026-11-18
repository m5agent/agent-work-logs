# Tab5 原版的缓存窗口、双核等待与设备画面

## 版本和验收范围

固定 Device Service 源码 80a3b5eda5f50c4a8cced04e31021fc8363593ab、esp-emu 1.1.0 633a35f993300a765634ed78a2dbcfd5ffcd5c3f2f354a2dddabeb6108240828、P4 ROM 及 C6 伴生固件。机型是 Tab5 GT911/ILI9881C。98TAB5 和 M5TabOS 使用内置识别寄存器，UserDemo 的新诊断使用与其会话身份绑定的 GT911 Part。七轮 M5TabOS 与 UserDemo 会话均通过原版应用分区逐字节读回、ZIP CRC 和成员哈希检查。[固定源码](https://github.com/m5agent/m5stack-esp-emulator/tree/80a3b5eda5f50c4a8cced04e31021fc8363593ab) · [esp-emu 发布说明](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0)

## 98TAB5

原版 Flash 的 DROM 启动函数表包含预期入口。只读检查在 CPU0 应用入口和 CPU1 ROM 交接时均读到正确值。在部分启动时序中，其后 DROM、IROM 和启动函数表可见值均变为零。随后的实际 CPU1 加载及跳转可触发指令访问异常。A9 和 A12 捕捉到 CPU0 ROM 的缓存同步和失效操作与该窗口重叠，同时保存了 CPU0 的 Cache error。缓存实现故障和唯一原因仍待验证。[98TAB5 六轮原版回执](evidence/98tab5-cache-window-summary.json)

| 直接对照 | 实际时长 | 软件复位 | 完整取帧 | 诊断 |
| --- | ---: | ---: | ---: | --- |
| A11 无调试器自然启动 | 64.005 秒 | 33 | 0 | 暂无自然启动成功证据 |
| A10 只读断点并正常分离 | 64.002 秒 | 4 | 21 | 分离后 20 次同哈希的有效非黑帧，显示无启动盘提示 |

20 次稳定帧采样覆盖第 24.655 至 63.723 秒，分辨率 720×1280。该对照保留原版固件、Flash、eFuse 和来宾数据，断点改变了执行时序。A8 的调试断开未完成，仅用于保留探索经过。正常启动、带盘启动及真实输入仍开放。

## M5TabOS 与官方 UserDemo

| 原版 | 观测 | 下一步 |
| --- | --- | --- |
| M5TabOS 0.9.1 | 75.010 秒自然观察仅上电一次，零软件或 LP 看门狗复位，零完整 DSI 帧。旧 CSR 指令在 1.1.0 从 0x4ff0255a 正常前进至 0x4ff0255e。两核在三个重复时点均停在 WFI 之后，未见待确认暂停。 | 识别 WFI 调用者后，检查时钟或跨核中断的产生、路由和投递。 |
| 官方 UserDemo V0.4 | 三个重复时点的两核读回均见 PMU 请求域 0x00860000，HP 状态寄存器为零。CPU0 指令在等 CPU1 暂停确认位。历史同原版、同 esp-emu 1.1.0 审核另有一次 LP 看门狗复位。 | 使用匹配 ESP-IDF 的双核探针，核对 CPU1 活动、暂停确认与解除后的进展，再回归原版。 |

GDB 未提供所需的中断 CSR 值，M5TabOS 等待原因仍开放。官方 UserDemo 的短诊断轮为 25 秒，历史 60 秒原版看门狗证据单独保留。三份原版均保持各自原始字节。[分路径回执](evidence/tab5-startup-paths-summary.json) · [ESP-IDF 暂停确认实现](https://github.com/espressif/esp-idf/blob/v5.4.2/components/hal/esp32p4/include/hal/cpu_utility_ll.h#L30-L49)

## 复现与清理

使用回执固定的原 BIN、规范化 Flash、C6 固件和板级配置，在独立 Device Service 上传并导入原版，再创建新会话。每份原版先保留无输入且无调试器的自然启动，按相同窗口取串口与 DSI 帧。另启诊断会话，以回执的 GDB 硬件断点只读来宾地址、双核 PC 和状态寄存器，分离后继续采样。核对原版应用分区、ZIP 和同会话清单，停机并清退两个所属进程，释放可变 Flash 和租约。

公开报告保留摘要及哈希。设备、会话、宿主唯一标识和原始证据均留在受控目录。这批诊断无需回滚源码，未修改常驻服务。
