# ESP Emulator：UIFlow2 原版启动与云端配对

- 日期：`2026-11-13`（Asia/Shanghai）
- 结果：`PASS`（限定本记录范围）；原版配对、实际网页与本地编程通过，源码已发布 main、完整检查与 CI 通过，更新后用户路径已独立复测。
- 工作类型：`code_change`
- 问题来源：用户报告刷入 UIFlow2 后一直没有配对码，要求恢复官方启动体验；不是新增公开 Issue。
- 源码版本：[m5stack-esp-emulator @ 8598b1f603ae6638a3f6d27824431781429b9e49](https://github.com/m5agent/m5stack-esp-emulator/tree/8598b1f603ae6638a3f6d27824431781429b9e49)（已发布 main 并回读确认）；逐文件 SHA 已在摘要保留。
- 环境：原生 QEMU 与 Device Service，真实官方 UIFlow2 BIN；网页只作为原生设备的控制入口。无物理设备或 browser-WASM 联网声明。

## 结论

原入口把 UIFlow2 当作本地编程环境，安装 UART REPL bootstrap，未进入官方
自动联网和配对页面。新增明确的官方云端模式，以固定原版 SHA、完整合法 NVS
和真实 Wi-Fi 控制器运行原厂启动代码。服务不合成配对码，不改写原应用、
`boot.py` 或 `main.py`。

CoreS3、StickS3、Core2、AtomS3R、StopWatch、Cardputer ADV 的最终独立会话
均有真实 MQTT 配对回包及官方六位 Access Code 画面。真实网页 CoreS3/StickS3
入口也分别验证通过；独立本地编程对照仍能在 guest 产生串口输出和实际绘图。
所有这些会话均先取证，再停止、释放 lease 并保留历史。

## 关键证据

- 运行：原生运行时 SHA、逐设备原始/规范化固件 SHA、NVS SHA、源码文件 SHA。
- 行为：DHCP/DNS/SNTP/MQTT 脱敏计数、实际非空配对回复、逐帧人工复核结果。
- 对照：旧编程入口的全黑帧；初次 cloud API 的三个未补齐 Flash 长度失败保留。
- 来源保护：规范化只补尾部 `0xff`，独立 artifact 不覆盖已有同 SHA 的 manifest；参考 pin、原请求幂等、重启历史与网络策略回归通过。
- 交付：源码已发布 main；Python 全平台 2098 项（1 skip）、Node contracts 与四项 validators 通过。更新后八次原版配对与一次本地编程对照复测通过，CI 两项作业通过。

## 文件

- [report.md](report.md)：根因、修改、复现、边界和回滚。
- [run.json](run.json)：结构化执行、源码交付与后续复测。
- [validation-summary.json](evidence/validation-summary.json)：已审白名单摘要，与源码证据中的当前摘要逐字节相同。
- [source-checks-summary.json](evidence/source-checks-summary.json)：最终完整检查、main 回读及两轮失败摘要导航。
- [发布后原版用户路径](followups/2026-11-13-published-source-paths/README.md)：八次配对、一轮编程、清理和保留的观察脚本失败。
- [CI 摘要](evidence/ci-summary.json)：固定源码的两项作业回读。
- `patches/`：不适用；最终修复通过公开源码固定提交引用，不复制整个补丁集。
- `code/`：不适用；回归测试与实现保留在公开源码仓库，固定链接见报告。

## 未覆盖项

browser-WASM 云端联网、物理 RF/电气/功耗/声学、其它型号/固件及长期在线稳定性
未验证。初次编程对照的阶段限制保留；发布后的编程重跑见独立 follow-up。未提交 Burner；公开记录不包含内部服务拓扑或运维配置。
