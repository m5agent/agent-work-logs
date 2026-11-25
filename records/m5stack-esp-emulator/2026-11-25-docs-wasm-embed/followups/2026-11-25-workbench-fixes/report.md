# 文档浏览器工作台验证

## iframe 共享内存

回归使用 `platform/tests/test_public_workbench_browser.mjs --embedding-isolation`，以桌面 Chromium 打开无跨源隔离头的文档父页。旧版 iframe 切换设备后显示泛化的“此设备需要仿真服务”。候选保持共享内存缺失原因和独立打开提示，浏览器启动禁用，明确选择模型模式仍可使用。两个版本都没有请求启动所用的 WASM。

隔离父页通过 same-origin 的真实浏览器 iframe 打开同一来源静态导出。CoreS3 固定 LVGL/PIR 参考固件冷启动与同页再次启动样本约 13.0 和 11.6 秒。已知触点 (160,184) 按住约 650 ms 后，串口 `touch_clicked` 与点击计数像素都变化，动作到观察约 1.09 和 1.36 秒。两个较早的同坐标输入尝试尚未得到回调，成功测量使用了 20 秒稳定窗口。Cardputer-Adv 固定参考固件两组约 24.5 和 23.4 秒到应用就绪，真实 A 键通过 TCA8418 路径更新来宾序列和像素，动作到观察约 0.62 和 0.69 秒。每组退出码 0，1 个 engine 和 5 个 pthread Worker 由 CDP 确认回收。测试用隔离文档是集成预览，正式文档页面还需要其响应策略更改和上线验收。样本是桌面本地观测。

## CoreS3 UIFlow2 M5UI

在原工作台镜像运行官方的 Display、Canvas、touch 和 M5UI button 过程中曾在 `m5ui/port.py` 出现 `RuntimeError: schedule queue full`。单独运行按钮在原镜像上也可以成功。候选把仓库中既有的 CoreS3 LVGL 单 VM 调度合并模块纳入默认 CoreS3 编程镜像，保留原固件参考和其他板型。浏览器按源文件与完整镜像哈希验证组合结果。

候选镜像 SHA-256 为 `b9fe8334023c1b1f95e7c51b3a63724e621a6789812083848ed3ea7eaa332d49`。真实 UI→LittleFS→WASM 路径的 64 项编辑器检查通过，涵盖暂停、恢复、程序中断、已知颜色像素、复位及同 UART 恢复。候选同一 VM 顺序执行六例（显示、Canvas、触摸、按钮、arc、checkbox），未出现原队列溢出，正常回收。独立复验用物理帧坐标 (154,118) 对原 Button 例程送入按下及释放，来宾 RGB565 显示标签更新为 `released`。某次混合运行随后出现 roller 的中断问题，原版和候选各自独立运行该例均通过。长时运行与任意重复执行维持开放。

两个摘要保留实际输入、固件和 WASM 标识、像素哈希和退出。环境地址、Worker 标识和原始日志已省略。真机及文档线上部署 `NOT RUN`。
