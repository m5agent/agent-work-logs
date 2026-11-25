# 验证和复现

旧浏览器工作台没有为该超声波例程装配 I²C 目标。使用相同原固件时记录到 NACK，原例程回退显示 4500.00 mm。继电器原程序能切换标签，但当时未挂接和观测虚拟继电器。早期隔离正控直接挂接两种 Unit，确认已有 QEMU 模型可运行，并给出实际屏幕基准。[失败对照](../2026-11-25-arduino-board-probe-and-units/) · [隔离正控](../2026-11-25-version-and-unit-controls/)

候选工作台 `bdfe07fcb0eb462565d25095edf722c2de468b98` 对 CoreS3 的两份已核验输入固件启用固定接线。启动时把接线送入 QEMU；超声波挂在 Port A 的 GPIO2/1，继电器通过 Port B 的 GPIO9 接收信号。超声波距离须经固定 QOM 写入和回读，状态来自该 I²C 芯片及其计数。继电器状态来自 QEMU GPIO 监听。界面提供距离滑块和继电器电平观察。

| 原固件 | 输入及同次虚拟设备结果 |
| --- | --- |
| Ultrasonic-I2C | 同一 guest 通过滑块走过 1000 → 250 → 1700 → 1000 mm。对应 I²C 事务/读字节/写字节为 2/3/1 → 4/6/2 → 6/9/3 → 8/12/4，实际 RGB565 帧与每个预期距离匹配。无 I²C NACK。 |
| Ultrasonic-I2C 重开 | 停止前确认 1700 mm；同页重开出现新 guest，输入历史为空，恢复 1000 mm 和初始帧。原生范围控件 ArrowRight 走到 1001 mm，实际 I²C 读数和 LCD 随之更新。 |
| Unit Relay | 屏幕原生坐标 (144,122) 两次按下和释放。GPIO9 输出低→高→低，实际计数 1→2→3，来宾标签 Open→Closed→Open。 |
| Arduino Display 对照 | 同设备另一个原始 BIN 连续输出不同的真实帧，没有匹配的 Unit、控制项或运行状态。 |

固定环境为标准浏览器工作台、`cores3-wasm-vm-div8`、Chrome 158.0.8127.37 和 `e350ed7b…5f4b` Xtensa WASM。四次运行正常退出，观测到的 6 个 Worker 全部关闭，iframe 移除。精确选点使用滑块的 DOM change 事件。键盘原生事件和两次继电器触摸通过浏览器实际输入路径。ROM 请求使用单独摘要核验的原版缓存响应。结果覆盖本地虚拟 I²C/GPIO 和本表中的镜像。物理测距、继电器触点、电气和负载、原生运行时及正式托管未执行。

## 复现

1. 以该记录的代码提交为基础，按模拟器 `docs/pages-deployment.md` 的 QEMU、LittleFS 构建及 `build_public_site.py` 流程导出站点。使用摄像头修复的[锁定构建](../2026-11-25-cores3-qvga-camera/evidence/locked-build.summary.json)核对 WASM 和 ROM；完整摘要见本记录证据。
2. 使用 Arduino CLI 1.3.1 与 M5Stack 板管理器 3.2.5，为 CoreS3 编译官方英文文档中的原始 [Ultrasonic-I2C](https://docs.m5stack.com/en/arduino/projects/unit/unit_ultrasonic_i2c) 和 [Unit Relay](https://docs.m5stack.com/en/arduino/projects/unit/unit_relay) 例程。Ultrasonic-I2C 使用 M5Unit-Sonic 0.0.2。核对合并 BIN 的完整 SHA-256；本次固定图像及原源码摘要写在 `run.json`。
3. 从本地 Pages 导出运行浏览器工作台，选择 CoreS3，上传原合并 BIN。依次操作滑块、停止再开和方向键。另起继电器会话，在原始 LCD 坐标点击两次，分别观察工作台电平与 LCD。再运行 Arduino Display 原例程对照。
4. 在停止前下载浏览器运行记录，核对 `unit_example_state`、固件和 WASM 摘要及输入回执。用 `evidence/standard-workbench.summary.json` 逐项核对距离、GPIO、I²C 计数、RGB565 和 Worker 清理。
