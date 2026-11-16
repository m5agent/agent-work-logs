# Cardputer 原版缓存启动、板型探测与按键

- 日期 2026-11-16
- 结果 PASS（原版启动、显示、键盘和 70/70 原生矩阵）
- 工作类型 issue
- 来源 [#229](https://github.com/m5agent/m5stack-esp-emulator/issues/229)、[#230](https://github.com/m5agent/m5stack-esp-emulator/issues/230)
- 执行源码 f2f26604a5e8c8df898aa5ba2354364e6f1911d5
- 环境 macOS arm64 独立 native Device Service，QEMU 9.2.2

原版 M5Apps 2.7 越过 ROM 缓存占用，启动后可休眠、唤醒并进入主菜单。Cardputer 与 ADV 四份原版执行映像通过面板探测、显示和各一条实际键盘行为。详见 [完整报告](report.md)、[运行记录](run.json)、[复现入口](code/README.md)。

- [干净重建](evidence/combined-build-summary.json)、[组合版本原版用例](evidence/combined-targeted-summary.json)
- [矩阵摘要](evidence/matrix-summary.json)、[合并前 CI](evidence/pr-ci-summary.json)、[平台套件](evidence/platform-suite-summary.json)
- [缓存阶段](evidence/cache-stage-summary.json)、[板型阶段](evidence/board-stage-summary.json)

证据为 virtual-device validation。未验证真机、WASM、M5Apps 联网/存储和各固件的全部功能。原始 ZIP、固件和帧留在私有测试环境。
