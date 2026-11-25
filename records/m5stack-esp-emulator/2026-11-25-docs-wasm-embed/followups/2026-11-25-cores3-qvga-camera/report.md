# CoreS3 QVGA DMA 短帧与修复

[#243](https://github.com/m5agent/m5stack-esp-emulator/issues/243) 记录 CoreS3 UIFlow2 官方 Camera 程序反复报告短帧。使用官方 Python 文件、固定合并镜像和同一浏览器虚拟设备回归。原版源码 SHA-256 `58f1f6361eaa2b77c8bb91e8a1d62f44db6631177806b73be1ec28731965ece8`，浏览器文本框标准化换行后 SHA-256 `da995cdc16d03cce8e986dd603a368ac15bdcf0534367a29b31543bfdba416b4`。 [原版例程源码](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/advanced/camera/cores3_example_camera_display.py)

旧锁定 WASM `618f471307a11e90301372b5f704afa46df1224be19feda292ba663fb6c31a62` 与原 UIFlow2 v2.5.3 摄像头候选 Flash `52f38f562f6e3749357a2ed4834efd72d16870046ea052f2f31691743cb5384d` 在 320×240 输出正确场景，也反复报告 `FB-SIZE: 15360 != 153600`。MMIO 跟踪中 28 次短帧时序一致，第二个 15,360 字节 DMA 分组的 EOF 清除后，来宾先禁用 EOF、清除状态并写入 IN_LINK STOP。下一轮发现活动通道已失效，旧模型补发 VSYNC。来宾实际记录一个分组。

锁定源上 CAM_START 写入同步拷贝首个分组，后续按毫秒取整定时。对应 ESP32-S3 驱动的 ISR 先清 EOF 再向队列写入，队列此配置为一个槽；首次开采还在完成启动路径。过密事件与队列溢出相符，首次 STOP 的固件分支仍待直接取证。 [固定版本驱动](https://github.com/espressif/esp32-camera/blob/b817e9b81041980608d1a3d3e0b08d86e3666382/driver/cam_hal.c)

## 逐步对照和所选修复

隔离对照沿用相同固件、未改的官方例程、浏览器 UI 与虚拟控制器。先将首个分组交由下一次定时器；再使用完整的相对纳秒期限；最后按每个分组占当前 RGB 帧的比例安排合成 DVP 数据，通过已有 GDMA 描述符交付。选定补丁 0043 将定时延迟分配到整个帧周期，以 30 帧/虚拟秒为合成源的标称节拍。EOF 确认与空闲 VSYNC 的 rearm 行为继续由实际控制器处理。 [GC0308 模组规格](https://docs.m5stack.com/en/stamp/Stamp-AddOn_Cam0308)

30 秒带跟踪对照中，异步首块为 22/731 次提前停止，相对纳秒计时为 3/696。按帧周期的新候选两轮记录 958/959 次完整采集。每个完整采集有十组 GDMA 确认及正常 VSYNC。一次在第八个分组后提前停止，随后自动重开。两轮都有完整 RGB565 场景且没有短帧或溢出告警。短窗口、原失败、自动恢复和实际 Worker 回收都单列于证据。

## 复现方式

按模拟器仓库 `scripts/qemu-wasm-build/README.md` 以锁定 Emscripten 3.1.50 构建，使用 `platform/tools/build_public_site.py` 导出隔离浏览器工作台。选择 CoreS3 与默认 UIFlow2，导入原始 Python 并执行，读取实际 UART 与本次来宾的源 RGB565。在独立 Controller 诊断中，使用相同原例程、固定摄像头 Flash 和 div1 profile，额外启用 `M5SW_CAMERA_TRACE=1` 与 `M5SW_GDMA_TRACE=1`，确认每个实际帧的十次读写确认及 VSYNC 序列。完整显示的预期 RGB565 SHA-256 为 `864c08b6eeffccd05196c731d4d822784a778b3dca3935ebbe295c271a2b055e`，可由固定 seed 0 的四色条及白色网格源独立重建。

最终浏览器观察覆盖 CoreS3 QVGA 与固定虚拟场景。物理光学、传感器 PCLK、其他分辨率、其他设备与正式托管未在此轮验收。

## 最终锁定构建

完整重建的 WASM `e350ed7b2f969139803befef12757178049427058a212136868d382dfe5a5f4b` 与带跟踪候选逐字节一致。用未经额外跟踪修改的静态工作台，选择默认 v2.5.3，浏览器实际组合 `b9fe8334023c1b1f95e7c51b3a63724e621a6789812083848ed3ea7eaa332d49`，随后从真实文件入口载入官方程序并运行。官方基底和 ROM 请求通过绑定摘要的缓存回放。

从首帧开始观察 30.187 秒。采样的 118 帧均匹配 320×240 的预期 RGB565，显示源序号从 66 前进到 5274，六段五秒窗口各有 19 或 20 个不同采样帧。观察期间同一来宾未出现短帧、溢出、异常或复位。最后通过实际中断获来宾确认，QEMU 退出码 0，实际六个 Worker 和 iframe 已清理。采样帧和刷新序号用于验证画面持续更新。
