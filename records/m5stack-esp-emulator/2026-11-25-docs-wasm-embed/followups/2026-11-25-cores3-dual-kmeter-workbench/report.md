# CoreS3 原 DualKmeter 在 0050 标准工作台

完整源码锁重新编译所有 QEMU 对象。WASM `8067a6b8d599f81bfe454da0318377fcb783c8ee4198fc69d3a042c1311d2c1e`，本地标准导出 `e5f0cf5f7fbd15581b813223293e418bfe45b556aec1a71d1192cd87f2473396`。核对全部 2,186 个导出资源。两台都是 CoreS3，使用同一官方 v2.5.3 工作台组合镜像 `b9fe8334…2d49`，各用独立 Chromium 进程。完整原 `.m5f2` 的 Python 仍为 `6765c65a…fb37`，与官方编辑器两次独立生成的内容逐字节相同。[源码生成与默认早期对照](https://github.com/m5agent/agent-work-logs/tree/580797bfabda169ac3c8885da753059a4ef3a2fb/records/m5stack-esp-emulator/2026-11-25-docs-wasm-embed/followups/2026-11-25-cores3-blockly-source-preview)

普通 `本地 MicroPython 编程` 使用同一镜像，隐藏温度和原例程加载入口。手动上传同一原程序后，I²C `is_ready()` 再次返回 `OSError: 259`，验证显式选择以外没有挂接。

显式选择 `CoreS3 Dual Kmeter · UIFlow2 v2.5.3`，经页面的例程加载按钮取回同一原脚本，点击编辑器运行。第一次读取显示 `23.5`。随后用页面温度字段输入 `-12.34` 和 `87.65` 并移开焦点提交。原程序经真实 CoreS3 M-Bus I²C 地址 `0x11` 读取就绪和有符号温度，三种画面由原程序直接绘出。工作台同时显示模型读回。

| 模拟温度 | 原来的 320×240 屏幕 | 同一模型 I²C 事务 / 读取字节 / 写入字节 |
| --- | --- | --- |
| 23.50 °C | `23.5` | 14 / 16 / 7 |
| −12.34 °C | `-12.34` | 248 / 310 / 124 |
| 87.65 °C | `87.65` | 496 / 620 / 248 |

三个值的实际 RGB565 哈希也与私有候选的对应输出一致。页面编辑器中断收到同一来宾确认。两个浏览器的 Stop 均正常退出 QEMU，移除 iframe 并关闭各自 6 个 Worker。未观察到页面错误。物理校准、其他通道、整站覆盖和 Pages 未测试。[私有候选正反对照](https://github.com/m5agent/agent-work-logs/tree/a77b2023e946ad02780179470267f27effbdea69/records/m5stack-esp-emulator/2026-11-25-docs-wasm-embed/followups/2026-11-25-cores3-dual-kmeter-private) · [正式源码构建和来宾摘要](evidence/dualkmeter-workbench.summary.json)

## 复现

1. 以标准锁定配方构建 0050 runtime，使用项目 LittleFS 运行物，按 `platform/tools/build_public_site.py` 导出 `/showcase/` 的本地站点。记录本次固件、ROM、runtime、站点与原例程哈希。
2. 在真实浏览器选择 CoreS3 和浏览器 WASM，启动环境选择 Dual Kmeter。启动后点「载入 Dual Kmeter 官方例程」，在编辑器中运行，通过数值框输入两个温度，查看原屏幕和模型读回。点击中断与 Stop。
3. 另用新的浏览器进程选择普通本地 MicroPython 编程，运行相同原脚本并确认标准负对照。保留两个独立报告。
4. 如需自动复跑，将 [脚本](code/run-locked-dual-kmeter-workbench.mjs) 与 [OCR 源码](code/read-display-text.swift) 放到对应的自有实验目录。以 Swift 编译 OCR 工具 `read-display-text`，按脚本选定的固定路径准备原始项目、完整生成的 Python、ROM 和官方镜像。设置 `M5_DUAL_KMETER_WORKBENCH_RUN=1`、`M5_PUBLIC_SITE`、`M5_DUAL_KMETER_SITE`、`M5_DUAL_KMETER_WASM`，分别运行 `node run-locked-dual-kmeter-workbench.mjs default browser-dual-kmeter-0050-default-1` 和 `node run-locked-dual-kmeter-workbench.mjs positive browser-dual-kmeter-0050-positive-1`。每次使用新输出目录，等待前一进程关闭。

全量 Python 2,569 项中跳过 11 项。Node 契约、源码锁、覆盖、目录、配置和生成快照检查通过。其他 Unit、ModuleLLM、真实温度校准及生产文档接入继续分别验收。
