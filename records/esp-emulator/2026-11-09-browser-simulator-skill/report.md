# GitHub Pages 固件画面检查报告

## 背景与改动

需要一个可以由模型执行的浏览器操作 Skill，聚焦导入固件和查看实际画面。已部署工作台具有独立浏览器 WASM 运行、合并 BIN 导入、原始屏幕及停止入口。仓库加入文档型 Skill、独立 ZIP 白名单和入口说明。现有打包测试继续对每个归档验证内容及校验和，并对提供 Python helper 的包执行 `--help`。

## 复现

1. 用桌面 Chromium 打开公开工作台，选 CoreS3 K128。 [工作台](https://m5agent.github.io/m5stack-esp-emulator/)
2. 选 **加载固件 → 链接**，使用官方 UIFlow2 v2.5.3 CoreS3 BIN，大小 16,121,856 字节。源文件 SHA-256 为 `1324f12d3ddd5392f47a9eff537f9ce0b01a8e6e36d829b6bd22cdf82d2c1264`。 [官方 BIN](https://m5burner-cdn.m5stack.com/community/1/1897200000000001950/2102696305989775362/bin/2102696305989775363.bin)
3. 打开 **校验与运行选项**，填写源文件 SHA-256，选择 **浏览器本地运行** 后开始。等待启动，点击 **平面触屏**，观察 UIFlow2 Develop 菜单。
4. 点击 **停止**，确认页面显示「运行已停止」，下载本地运行记录。可复现的串口标记包括 `ESP-ROM:esp32s3-20210327`、`SPI_FLASH_BOOT` 和 `entry 0x403c8890`。同次运行也有两条 I2C 初始化日志。画面样本的帧序号为 94。

用同一份 BIN 复测本地文件路径时，第 2 步改为 **加载固件 → 本地文件 → 选择 .bin 固件**。在隔离 Chromium 中确认所选文件、源 SHA、同一 guest 的 ROM 标记及 320×240 客体帧。该次取证显示 UIFlow2 启动画面，序号 128。观测到的请求中没有 Device Service 或固件 CDN 请求。停止后回执的 iframe 已移除，独立 CDP 观测到的 6 个 Worker target 全部消失。首次自动化的应用串口标记不适用于此原版固件，取消后改以 ROM 启动标记和同次客体画面验收。

## 验证层级

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | Skill 格式、独立 ZIP、确定性打包与 SHA256SUMS 检查。平台回归 2,042 项通过、10 项跳过，快照和相关 validator 通过 |
| flash（虚拟） | PASS | 源镜像 SHA-256 检验后，运行回执记录补齐到 16 MiB 的 Flash SHA-256 |
| transport | PASS | CoreS3 同次启动串口和原始 RGB565 帧回读 |
| device_response | PASS | ROM 从 SPI Flash 启动，应用画面可见，QMP 停止后正常退出 |
| visual_or_physical（虚拟） | PASS | 两次均取得 320×240 实际客体画面。直链显示 Develop 菜单，本地文件显示启动画面 |
| data_behavior | NOT RUN | 这次目标只涉及启动与显示 |
| visual_or_physical（物理） | NOT RUN | 使用浏览器 WASM 验证 |

URL 试验的运行时 profile 为 `cores3-wasm-vm-div8`。输入只有工作台的文件配置、运行、展开屏幕和停止，未向客体发送按键或触摸。停止回执记录退出码 0、嵌套 Worker 计数归零和 iframe 已移除。运行摘要保留镜像与运行时哈希，排除原始会话标识及完整像素。

独立 ZIP 可由仓库的 `python3 platform/tools/agent_skills.py --out-dir dist/agent-skills` 重建。恢复本地 Skill 安装可移除新 Skill 目录。工作台本身复用原部署，浏览器 Flash 属于当次运行。

## 本地 BIN 进入 Develop 的复测

另建一轮浏览器会话加载同一份本地文件。原始屏幕第 378 帧的 Develop 选中标签和 WEB IDE 标题区域 SHA-256 均与直链样本一致。串口保留同一固件的 ROM 启动和应用入口标记。停止后回执记录退出码 0、iframe 移除，独立 CDP 再次确认 6 个 Worker target 全部消失。复测过程中修正了第一次取图判定过早的问题，首轮启动画面证据仍保留。 [复测摘要](evidence/local-bin-develop-summary.json)
