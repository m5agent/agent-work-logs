# Dial 默认输入节奏与来宾采样

本记录使用隔离 Device Service 进行原生虚拟设备验证。持续使用原 UIFlow2 RotaryIRQ 和同步 LCD 重画的组合镜像 SHA-256 为 `310c6eff78be47a722582dc05400f2e18463eaf0a8a4b02a1682c9aa923ad4d5`，原生 Xtensa QEMU 为 `5f8a5f38f0512db04a36fb7ca5cf13ec3d359d0fff1eb481fe9b2c06ab3580f2`。最终执行代码 `1a9c33cf172342c45a07ff40571bb1898a022e5e` 与候选 `693c56948c2458cf8e24c800832f7600438f4b45` 之间只有项目状态和自动快照两份文档改变。编码器处理模块 SHA-256 为 `a20afb7995d67dc7e66987bad22ab081fc8e854e6d7c31b631c953ba89405dea`。

| 路径 | 观察 |
| --- | --- |
| 原默认 5 ms，原驱动与同步重画 | 8 个快速正反向动作，精确计数 1/8 |
| ESP-IDF ISR 快速对照 | 上述动作的 96 个边沿全部进入来宾，四相相序正确 |
| 仪器化 UIFlow2 快速对照 | 96 次回调都执行，8 个动作的实时 A/B 读数都出现跳变或重复 |
| 前台延迟改为 1 ms、继续重画 | 5 ms 快速动作精确计数 0/8 |
| 保持 20 ms 前台延迟、暂停同步重画的对照 | 6 个显式 5 ms 动作精确计数 6/6 |
| 新普通输入省略间隔 | 35 ms，原驱动及重画下 `±3` 和 `±4` 各三次，精确计数 12/12 |
| 确认执行源码的复验 | 35 ms 默认四次均准确；显式 5 ms 的 `+4` 和 `−4` 交付各 16 个模型边沿，应用分别记为 `+2` 和 `−2` |
| 单次普通输入 `+128` | 来宾 ISR 捕获 512 个准确边沿，首末边沿间隔 18.104 秒 |
| 旧运行时普通输入 | 实际间隔回执为 5 ms，`+3` 和 `−3` 共 24 个准确来宾 ISR 边沿 |

ESP32 Pin 中断将对象加入 MicroPython 调度队列，RotaryIRQ 的延后回调读取当时 GPIO A/B。快速输入加上同步 LCD 重画时，后续实体相位已到达，回调可能读取重复或跨越后的相位。对照仍经过真实虚拟控制器和来宾 GPIO。Device Service 对支持 `paced-detents` 的 Dial 普通请求选择 35 ms；明确的 `edge_period_ms` 按请求执行，旧运行时读取并回报自身间隔。

## 复现

按源码目录 `docs/evidence/2026-11-17-semantic-native-input/README.md` 组装同一 UIFlow2 组合镜像。用独立原生 Device Service 创建 Dial 会话，等待 `DIAL_DISPLAY` 和初始计数。提交 `{"kind":"encoder","delta":3}`，读取 `/machine/encoder` 的 `delivered-detents`、`gpio-edges` 和同一会话串口 `DIAL_ROTARY`，核对来宾差值。等动作完成再提交下一条。显式高速对照仅增加 `"edge_period_ms":5`。读取同一路径的 ESP-IDF ISR 对照来核验实收四相边沿。保存停止前证据 ZIP 并检查清理。回执 `completion:queued` 表示输入已排队，来宾消费证明来自读回。

## 精确集成源码确认

以 `693c56948c2458cf8e24c800832f7600438f4b45` 重跑同一 UIFlow2 组合镜像和原生运行时。省略间隔的 `+3`、`−3`、`+4`、`−4` 四个请求全部采用 35 ms，四个来宾差值均准确。显式 5 ms 的 `+4` 和 `−4` 均交付 16 个模型边沿，来宾分别记为 `+3` 和 `−2`。早先 `1a9c33cf` 同样的正向快转读为 `+2`，两次均保留实际来宾计数。隔离会话和服务已停止。[精确源码复验摘要](evidence/integrated-dial-confirmation-summary.json)

最终候选 `37fc8963d77bf806cde4fa16ea11e31b5a98b4d7` 只调整传感器测试 ZIP 时间戳。以该精确源码再跑普通输入，来宾对 `+3`、`−3`、`+4`、`−4` 记录 4/4 准确差值，捕获总计 56 个模型 GPIO 边沿并释放所有租约。[最终源码隔离复验](evidence/release-source-dial-confirmation-summary.json)

## 范围

普通服务输入在已验证 UIFlow2 路径为 `PASS`。显式 5 ms 同步重画下原驱动应用行为仍为 `PARTIAL`。实体旋钮时序、浏览器 WASM、其他 Dial 应用和 Burner 提交均为 `NOT RUN`。本记录仅归集源码及其隔离执行证据。选择较早服务源码可回退默认节奏，固件无需改变。
