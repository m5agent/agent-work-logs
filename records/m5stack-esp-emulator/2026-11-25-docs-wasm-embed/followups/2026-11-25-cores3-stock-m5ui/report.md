# CoreS3 UIFlow2 v2.5.3 Switch 与 Slider

两例均使用官方修订 a61a29409f09f1f4bebae05e15c4bd6dcc4956b6 的原始 Python 字节。共同 WASM 为 210db550d50847a3d4f66d86f81c8d1cdb2ac106ebf6bac16cccc60f4da0e211，静态站点清单为 cec271aefa1a575d8b257ea899a8af91eb8209575202fef99fb919bab37f16ac，默认 CoreS3 工作台 Flash 为 b9fe8334023c1b1f95e7c51b3a63724e621a6789812083848ed3ea7eaa332d49。工作台使用时钟除数 1 和 one-insn-per-TB。平面屏幕测试先核验 canvas 是指针命中的无遮挡目标。

| 项目 | 实际结果 |
| --- | --- |
| Switch 首次视觉基线 | 首帧仅 336 个灰像素，后续补全为 1,088。首次判定的等待时间不足，原失败已保留 |
| Switch 自然点击 | 完整灰色画面稳定后，可见中心 (158,106) 的按下和抬起均已确认，原程序未输出 checked |
| Switch 诊断输入 | 盲区 (25,58) 无变化。改为 (106,81) 连续点击两次，依次输出 switch0 checked 和 switch0 unchecked。对应区域由灰色变为 1,120 个绿色像素，再变回灰色 |
| Slider | 盲区触摸对滑轨和标签无影响。标准平面拖动 (110,119)→(225,119) 后，控制条和数值区域各自更新。保留的来宾画面可读数值从 25 更新为 40。编辑器 Ctrl-C 五秒后超时 |
| 停止 | 四次执行均经 DOM Stop 退出 0，iframe 移除，CDP 分别观察到 6 个 Worker 正常关闭 |

Switch 的诊断匹配点符合候选关系 raw=(logical_y,239−logical_x)。本次验证了其中一个变换点。两例画面均保留右侧黑区，完整布局和触摸校准仍需验证。Slider 的应用交互和 UI Stop 有各自的执行证据。

Arc 文档例程与 Switch 的 Python 源码 SHA-256 同为 ddca9d31feeee60478bacacb32d35275bc110c388924146a90b175eac7b5cc2a。Slider 的原始源码 SHA-256 为 e3c7f359fd6dfba395bd16b78adefaabdabe3878f70966a8c6265afdd8261a71。各次报告、截图、可视区域和输入数据见 [机器证据](evidence/stock-m5ui.summary.json)。

## 私有回放复现

保留原 0046 工作台的静态导出，调整 [回放脚本](code/run-stock-m5ui-0046.mjs) 的工作区目录、官方源代码和二进制输入缓存。以 Node 22 加载 Playwright，并用官方本地基底和原 ROM。设置 M5_STOCK_M5UI_RUN=1 启用执行，另设 M5_STOCK_M5UI_PREFLIGHT=1 可只做静态身份检查。

Switch 测试传入 switch 和 browser-0046-stock-m5ui-switch-replay，设置 M5_STOCK_M5UI_SWITCH_DIAGNOSTIC=1 可复验变换候选点。Slider 使用 [原测试版本](code/run-stock-m5ui-0046.slider-checkpoint.mjs)，传入 slider 和 browser-0046-stock-m5ui-slider-replay。每次使用未占用的输出路径，保留应用输出和实际退出回执。
