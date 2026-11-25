# CoreS3 相机和 Cardputer-Adv LoRa Cap 外设例程

使用仓库的 `platform/tools/build_public_site.py` 生成静态导出，在桌面 Chromium 打开工作台，分别选择 CoreS3 和 Cardputer-Adv 的默认浏览器 MicroPython 环境。通过编辑器加载官方示例的原样 Python 源码，核对编辑器文本哈希及同一来宾运行回执，保留串口和 QEMU RGB565 屏幕帧。原文件 CRLF 由编辑器转换成 LF 的例程同时保留两个 SHA-256。每组停止均为 QEMU exit 0，内层 iframe 移除，1 个 engine Worker 和 5 个 pthread Worker 已由 Chrome DevTools 观察退出。

## CoreS3 Camera

用 [Camera Examples](https://uiflow-micropython.readthedocs.io/en/latest/advanced/camera.html) 的 `cores3_example_camera_display.py`。例程初始化 `RGB565/QVGA` 后不断调用 `camera.snapshot()` 和显示。在一次独立干净运行中，12.5 秒观察窗口内，串口重复报告 `cam_hal: FB-SIZE: 15360 != 153600`。最新来宾帧为 320×240、五色虚拟图案，SHA-256 `864c08b6eeffccd05196c731d4d822784a778b3dca3935ebbe295c271a2b055e`。中止例程后，REPL 可继续工作。根因待定位，应核对 GC0308 设置、DVP 帧边界、LCD_CAM/GDMA 长度及重复帧序列。

## Cardputer-Adv LoRa Cap

在 Cardputer-Adv 浏览器工作台运行 [LoRa1262](https://uiflow-micropython.readthedocs.io/en/latest/cap/lora1262.html) 和 [LoRa868](https://uiflow-micropython.readthedocs.io/en/latest/cap/lora868.html) 的原收发和 GPS 例程。当前导出的板级工作台未挂载虚拟 Cap。LoRa1262 接收和 LoRa868 收发均在 `lora/sx126x.py` 进入 `_wait_not_busy` 后报 `RuntimeError: ('BUSY timeout', 8000)`。这轮 LoRa1262 发射在观察窗被中止。两个 GPS 脚本绘出相同初始界面，没有观察到 GPS 数据更新。验收需要真实 SPI/BUSY/IRQ 模型上的双端收发，以及可重复 NMEA 输入到原界面字段变化。物理 RF 未验证。

[脱敏摘要](evidence/camera-and-lora-summary.json) 保留源文件、来宾镜像、运行时、帧和回收计数，略去环境地址、Worker 标识和原始日志。会话标识已哈希化。
