# Core2 原生模拟器显示刷新与触摸回归

## 显示模型

Core2 的面板启用了 `immediate-update`。每次 SPI 数据写入令面板变脏时，写入路径都会排入即时刷新并唤醒虚拟时钟。刷新函数在脏帧上遍历整个可见区域，把 RGB565 像素转换为宿主显示缓冲。高频小批写入会反复触发这条整屏转换路径。

补丁 `0167-core2-panel-refresh.patch` 仅删除 Core2 板初始化设置的 `immediate-update=true`，由面板已有的 16,666,667 ns 虚拟时钟定时器合并更新。仍由同一个面板函数处理脏帧，触摸映射、GPIO39 和 FT5x06 I²C 寄存器路径沿用原实现。原生构建基于上游 QEMU `40edccac415693c5130f91c01d84176ae6008566` 及项目补丁栈。[模拟器源码基线](https://github.com/m5agent/m5stack-esp-emulator/tree/70ca46258598294eb5e5852115b1dfce386d8754)

补丁已合入 `main` 的 `9c2fe5f22189ba5cb90485230b905bb17c625984`。原生 115 层补丁正反重放通过，构建使用的 138 个补丁源文件逐字节一致。平台 2,041 项测试完成，2,031 项通过、10 项跳过，运行覆盖、外设目录、QEMU profiles 和生成快照检查均通过。[合入提交](https://github.com/m5agent/m5stack-esp-emulator/commit/9c2fe5f22189ba5cb90485230b905bb17c625984)

## 虚拟设备对照

将同一份 [来宾脚本](code/main.py) 通过 Device Service 的 `POST /api/v1/firmware/uiflow` 组合到官方 UIFlow2 Core2 v2.5.4，固定 `expected_base_sha256` 为原始官方参考文件哈希。然后用 Core2 配置、`runtime=qemu`、同一组合固件和同一 ROM，在两个独立会话依次运行基线和候选。创建会话时固定 `uiflow_source_sha256`，开启 `M5SW_FT_TRACE` 和 `M5SW_I2C_TRACE`。待串口输出 `CORE2_TOUCH_PROBE_READY 320 240` 后，向 `POST /api/v1/sessions/{id}/input` 发送 [同样的五组输入](evidence/stock-control.summary.json)，每次设置 0.6 秒稳定等待。

| 输入 | 起止坐标 | 来宾输出 |
| --- | --- | --- |
| 点击 | (97,118) | 原始与逻辑坐标完全匹配，触点数从 1 回到 0 |
| 左拖 | (220,170) → (94,170) | 每个坐标一致，共 7 个，松手后为 0 |
| 右拖 | (96,170) → (221,170) | 每个坐标一致，共 7 个，松手后为 0 |
| 上拖 | (140,208) → (140,87) | 每个坐标一致，共 7 个，松手后为 0 |
| 下拖 | (140,84) → (140,212) | 每个坐标一致，共 7 个，松手后为 0 |

串口探针调用 `M5.update()` 后同时读取 `getTouchPointRaw()` 和 `getX()/getY()`。QEMU 的触摸事件和实际 FT5x06 I²C 读回互相核对，每个按下的坐标在候选中至少有 39 次完整寄存器 `0x02–0x06` 读回匹配，基线至少 38 次。基线和候选各记录 34 次触摸模型回调。两次会话的 320×240 画面均为同一 SHA-256 `72b59e756709e0ceec867fd1c40aca9ee1dc83dd295e3cf6b417e9a6aba93f14`，可见 `Core2 touch probe`。两次均先保存证据包再停止，保留画面并释放可写 Flash。[坐标、运行时与 ROM 哈希](evidence/stock-control.summary.json) · [候选画面](evidence/probe-screen.png)

## 范围与回滚

结果归类为 `virtual-device validation`。本记录验证稳定帧和输入兼容性。全屏转换的触发机制由源码确认。本次控制固件未测高负载刷新吞吐、宿主 CPU 使用率、硬件和浏览器 WASM。公开摘要保留了输入、输出和文件指纹，省略会话标识、环境路径和原始日志。恢复 Core2 原显示配置即可回滚。
