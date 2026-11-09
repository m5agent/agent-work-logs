# UIFlow 就绪提示的同路径验证

共享工作台在启动时显示状态，确认 UIFlow 可用后提供“编辑代码”入口。提示说明程序绘图后屏幕才会更新。Node 契约覆盖未知固件、错误状态和 managed Run 开始后收起提示。

候选 `d111addaf1ff4919951b40cd2926f6b90517cf46` 基于 `80d1879a014a55bc598fbc1474445c1f6773ff34`，改动三个页面文件和两个既有测试文件。两条候选路径的 `public.js` 均为 `3aff72322078855cab38d2967982fed134e60e611408e295d9456da033ad6243`。主线并行推进到 `340d80cf`。本报告使用上述实际受测的基线与候选。

Browser-WASM CoreS3 基线 12/12，候选 24/24。候选执行涉及的 33 个页面源码逐字匹配提交。两轮使用相同固件、ROM、WASM、profile 和参数。UART ready 后尚无代码运行，实际 320×240 guest 帧与模型均为全黑。候选观察到启动和就绪提示，1440 与 390 宽度无溢出。编辑入口实际聚焦源码，raw-paste 绘图使 guest 红帧进入模型。绘图后提示收起，停止后 DOM 快照确认隐藏，两轮 Worker 均清理。[浏览器证据](evidence/browser-cores3-summary.json)

Native CoreS3 基线 10/10，候选 15/15。隔离 managed Preview 使用相同 QEMU、基底、合成 Flash 和 boot 文件。基线经 host-image，候选用隔离的已核对 cache 副本。候选启动时 Run 禁用。UART ready 后 Run 启用，浏览器尚无代码提交或帧请求，独立 320×240 PNG 为全黑。同一 Preview 执行绘图后，绑定实际执行修订的全红帧进入模型，提示收起。UI 停止、预停止证据 ZIP、进程、租约、Flash 与浏览器清理均通过。公开派生摘要省略复现说明中的私用端口，保留原摘要 SHA256 和字节数。[Native 证据](evidence/native-cores3-summary.json)

Python 运行 2039 项，用时 136.705 秒，2029 通过、10 跳过。Node 首次启动缺少依赖链接，链接既有锁定依赖后 33 个脚本通过。四项 validator、PR scope 与 diff 检查通过。[结构化结果](run.json)

本次为本地 CoreS3 `virtual-device validation`。Pages、独立 HTTPS、物理硬件、其它型号和启动速度基准属于 `NOT RUN`。原截图、报告和 ZIP 以各摘要的 SHA256 与字节数关联。
