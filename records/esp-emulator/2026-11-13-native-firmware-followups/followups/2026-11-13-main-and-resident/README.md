# 原生固件问题处理：main 与常驻验收后续

- 日期：2026-11-13
- 结果：PARTIAL；交付门通过，未完成的原版应用与后端能力单独保留。
- 工作类型：代码修复、同路径虚拟设备验证、服务更新验收。
- 源码：[固定提交 `4f09fcba8364e02cb1f60eeec0422e3cae66db54`](https://github.com/m5agent/m5stack-esp-emulator/commit/4f09fcba8364e02cb1f60eeec0422e3cae66db54)；[完成的 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43414271086)。
- 验证：virtual-device validation；未提交 Burner。

这是[先前候选记录](https://github.com/m5agent/agent-work-logs/blob/ba2cde8849d814474c6bf69a0925d31f68642ae2/records/esp-emulator/2026-11-13-native-firmware-followups/README.md)的追加，保留旧失败、未执行和候选身份。
两轮各 69 个用例、每轮全部实际负载样本至少 10、无重试、清场与来源 pins 均经校验。
部署后 9 条云端/本地编程路径及 5 份原版方向检查已完成；完整身份见
[run.json](run.json) 与[报告](report.md)。这里不公开配对码、设备身份或内部部署拓扑。

整体仍为 PARTIAL：#188/#226 的 P4 后端缺口、#216 的部分原版固件、
#223 的两份原发布 BIN，以及 #225 的应用/Bluetooth 范围没有被交付门改写为通过。
固定源码重建版和原版 BIN 始终分开；历史 I2C 对照仍绑定 e044 运行时。

## 本次原版操作与显示复验

六款 UIFlow2 设备通过八条云端路径取得官方配对码，另有一条本地程序下发成功；九个实际 guest 画面均经过复核。八条云端结果来自第二次验收，编程项在工具修复后独立重测，三次工具失败均单独保留。

原版 Cardputer ADV MP3 Player 列出 SD 卡中的 `TEST.MP3`，真实 Enter 输入后进入播放页并产生与 524 Hz 测试音一致的 PCM。原版 Core2 2048 两轮右、左、上、下共八次输入均符合棋盘滑动、合并与单个合法新方块规则；两份原 BIN 应用字节保持一致。见[实际操作摘要](evidence/original-functional-observations-summary.json)。这些是虚拟设备数据路径验证，物理声学及真机对照未执行，未提交 Burner。

原版 Core2 for AWS 在同一 35c 运行时另行运行 90.024 秒，实际首页文字、时钟和滚动提示可见，单次启动且无致命错误。BMI270 读取错误仍保留，未授予传感器、触摸或云端功能通过；首轮工具路径解析失败亦保留。见[同原版显示复验](evidence/aws-original-final-runtime-summary.json)。
