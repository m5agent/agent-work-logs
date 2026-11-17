# StickS3 All day watch v0.3.8 看门狗留存复核

## 历史原版证据

三份 StickS3 原生虚拟设备证据使用同一个 1,840,512 字节的原版 BIN、同一个标准化 Flash 和同一 QEMU。旧执行固定于模拟器 `2db3851c0b7a4980210034d05130224a2ecf6455`，QEMU SHA256 为 `99da5cb681e44dfdf332f8af01b8d5d36bbb2801b30ca7e0ca6be21af4c0ecff`。本次对留存 ZIP 只读回放，三个用例的来宾执行都发生在历史运行中。

| 历史输入 | 来宾结果 | 阶段零距最后 SYSTIMER 报警 | 阶段零距最后对应 SYSTIMER 确认 |
| --- | --- | --- | --- |
| 第一组长按 | CPU1 中断看门狗，七帧回溯，一次重启 | 0.003 / 0.003 ms | 300.454 / 300.466 ms |
| 第二组长按 | CPU1 中断看门狗，七帧回溯，一次重启 | 1.519 / 1.519 ms | 300.699 / 300.755 ms |
| 快速松开 | 约 65 秒窗口内未观察到 panic 或重启 | 未观察到阶段零 | 未观察到阶段零 |

两次异常的首个阶段零记录均显示 SYSTIMER 刚产生报警，最近的来宾确认已过去约 300 ms，距最后喂狗分别为 300.423 ms 和 300.674 ms。已核对实际 ZIP、原 BIN 与标准化 Flash 身份、同一会话的诊断回执、串口与后端输出摘要。三条历史记录均已停止，活动租约为零。 [原版和对照的有界摘要](evidence/watch-retained-watchdog-summary.redacted.json)

## RTC 等待位置与模拟器缺口

两次 CPU1 panic 的现场 PC 均为 `0x4037cb95`。读取原 BIN 中对应指令，已确认该段设置唤醒与拒绝条件、清除已有标志、请求 RTC sleep，随后等待唤醒或拒绝原始状态位。这个寄存器序列与 ESP-IDF 的 ESP32-S3 `rtc_sleep_start` 一致。原固件没有匹配的 ELF，函数名和 SDK 版本保持未确认。 [ESP-IDF v5.4.1 RTC 实现](https://github.com/espressif/esp-idf/blob/v5.4.1/components/esp_hw_support/port/esp32s3/rtc_sleep.c#L269-L284) · [唤醒和拒绝状态位定义](https://github.com/espressif/esp-idf/blob/v5.4.1/components/soc/esp32s3/register/soc/rtc_cntl_reg.h#L822-L833)

历史 QEMU 与已审计的 `7e63fc22` 原生构建在 RTC 控制器和 GPIO pad 辅助实现上逐字节一致。RTC 模型在该状态读取路径返回零，未产生来宾可见的唤醒或拒绝完成。该缺口与历史采样一致，是看门狗异常的候选解释。证据没有覆盖中断何时开始失去确认，也没有验证补齐 RTC 完成事件后原版是否继续运行。 [原版指令与实现审计摘要](evidence/watch-retained-watchdog-summary.redacted.json)

## 审核取证改动

在 Device Service `541871f6fb6f48a4bda9b8846a9fb3054074f207` 的解析结果上，Reviewer API 0.14.0 将匹配同一会话和固件的首个看门狗阶段零时序带入诊断详情。该字段记录距最后喂狗、SYSTIMER 报警及确认的虚拟时间，缺项保留空值。固件身份不匹配的回执被排除。两个异常均记为 `guest_failure_observed`，固件归因均为 `UNRESOLVED`。快速松开保留为未观察到异常的单次对照。

Reviewer 主分支为 `ea64e80e3d88e2761b5627545376a1de400cf34f`，222 项测试通过。模拟器主分支 `c8a40dee575b944195ed52c7f8dfb8a16a51a8cf` 收录本次有界证据，文档 51 项、项目快照、相关生成校验和改动范围检查通过。远程 CI 在归档时仍待完成。 [对应源码与证据摘要](https://github.com/m5agent/m5stack-esp-emulator/blob/c8a40dee575b944195ed52c7f8dfb8a16a51a8cf/tests/firmware/crash_diagnostics/watch-retained-rtc-timing-summary.json)

当前原生运行时的原版来宾执行、修正 RTC 模型后的回放、实机、浏览器、常驻部署及 Burner 提交均为 `NOT RUN`。
