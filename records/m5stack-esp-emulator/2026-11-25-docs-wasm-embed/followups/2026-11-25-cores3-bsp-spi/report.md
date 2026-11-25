# CoreS3 BSP 显示修复

## 复现与隔离

原 CoreS3 Widgets 固件 e542eae66097a450c20ef95a4f528697cff6f7aedcdcf26dffba5c705bdd7811 在 WASM 42da2149…7558 的默认浏览器配置中反复出现 320×240 全黑。来宾成功创建 ILI9341，设背光为 100%，输出 Display LVGL demo 和 Returned from app_main()，随后以退出码 0 停止并回收 Worker。其他三个固件各有前一版 WASM 的同路径黑屏证据。[预研原记录](../2026-11-25-cores3-esp-idf-bsp/)

同源诊断对照显示，ESP-IDF 从 SPI3 发起初始化命令和像素的 GDMA 传输。GPIO3 输出路由 71 是 SPI3 CS0，SPI3_MISC 0x6 启用 CS0。旧模型把 SPI2 和 SPI3 映射到同一套 GP-SPI 寄存器，并固定读取 GDMA_SPI2。匹配观察的 78 次 SPI3 GDMA 启动没有产生面板字节。只切换面板使用的 GDMA 选择器后，78 个 SPI 块共 153,747 字节到达模型面板，原 Widgets 恢复。在该固件中旧 GPIO 电平恰好为低，因此只切换选择器足以完成这一对照。

## 实现与边界

0041 分开 CoreS3 SPI2/SPI3 的寄存器、GDMA 选择器和各自的中断。两者共用板级面板、SD 和 MAX3421E 模型，各 GPIO 观察由同一个对象注册。硬件片选使用实际 GPIO 矩阵的 CS0、SCLK 和 MOSI 配置与 SPI 外设状态。保留原有软件 GPIO 片选路径。独立 C 控制覆盖错误控制器、禁用片选、禁用时钟、反相、输出门控及不同控制器的 DMA 选择。

使用 Emscripten 3.1.50 和模拟器锁定配方完整从源构建。导出隔离本地静态站点后，以同一份 ESP-IDF v5.4.1、CoreS3 BSP 3.0.2、LVGL 9.6.0~1 的四个原合并镜像运行。构建与输入细节见先前失败记录。Music 沿用已发布的大 factory 分区配置。新 WASM 11c5dea1a3982562c1ccf552df8833e1987cad4cb70cbd3db4f484cd9b230555 的四例默认工作台运行均输出真实 320×240 RGB565 帧。Music 在过渡动画后进入播放器界面，Stress 显示动态部件，Benchmark 输出绘图及测试界面。

Widgets 使用未插入诊断代码的锁定站点。实际触摸按下和释放依次到达 160,22 和 53,22。画面由 Profile 切到 Analytics 的访客曲线，再恢复原 Profile 像素哈希。四个默认例程和触摸会话均正常停止，CDP 观察到全部 Worker 回收。

Benchmark 的独立常速候选 profile 使用同一原镜像，连续切换场景后出具包含平均 CPU、FPS 和渲染时间的结果表。该表来自虚拟机，不提供真机性能测量。原默认 profile 的观察窗口覆盖了测试运行中的动态像素。

挂接上一轮同一 FAT 镜像的私有配置中，原 SD 和 Picture 例程各观察到 55 次 CMD17 读取与 11 次成功写入，含 WriteTest.txt 的原文。两例均按 A→B→A 恢复两张基线帧并正常退出。该正控使用同一 WASM，独立测试站点只加入可选卡镜像。[SD/Picture 记录](evidence/cores3-attached-sd-regression.summary.json)

Cardputer-Adv 的同一 UIFlow2 参考镜像通过 69 项浏览器回归。11 个参考键的按下与释放经原 TCA8418 驱动回读，240×135 实际帧与模型纹理一致，暂停恢复和六个 Worker 的清理也通过。[Cardputer-Adv 记录](evidence/cardputer-adv-regression.summary.json)

验证只覆盖所述影像、控制器路径、浏览器配置和输入。音频输出、物理测量、真机、原生运行时及正式托管版本均未在本轮覆盖。摘要保留固件、实际运行时、产物和帧哈希，省去会话标识、端点及完整日志。回退方式是恢复上一版源锁与 WASM。
