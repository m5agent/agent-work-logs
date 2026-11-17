# Tab5 CarPlay 原版 DSI 首帧复验报告

## 背景

Tab5 原版固件在缺少匹配 ELF 时能执行，但旧后端的帧缓冲取证依赖应用符号。此次只验证固定新版运行时的原生 DSI 接收链路，以及审核服务能否用同一原版画面通过就绪检查。

## 执行

使用固定原版 CarPlay v1.0.0，长 2,221,360 字节，SHA-256 `4f3bb118a5570a6ba885a234fce55b66e28ef26091cfe4f3f2e4c33711471ea3`。Device Service 执行源码为 `42e282f25c8ad8f0694f97c8a44bd82dd5d0a43c`。它包含 `60c715abc86ae1d77149b0c50014a85a403ec865` 的 Tab5 GT911 板型改动。审核服务执行源码为 `55ffc80e7c9ec5e5280a267e875b4c042b54fde3`。

用独立 Device Service 进程，配置 `M5_TAB5_DSI_EMULATOR` 为明确核验 SHA-256 的 esp-emu 1.1.0 可执行文件，并设置 `M5_TAB5_DSI_BOARD=gt911-ili9881c`。实际运行时 SHA-256 为 `633a35f993300a765634ed78a2dbcfd5ffcd5c3f2f354a2dddabeb6108240828`。审核服务以 `sourceMode=saved_snapshot` 创建一次同哈希 dry-run；读取等待、观察和截图记录，导出证据 ZIP，结束会话并核对租约及临时 Flash 释放。

## 结果

| 验收层级 | 状态 | 依据 |
| --- | --- | --- |
| 板级 DSI 与画面就绪 | `PASS` | 取帧后端 `esp-emu-dsi`。画面 `720×1280`、921,600 个非黑像素、48 色，SHA-256 `b9caf8f325d9b9ec1ee5d7ae3b49f3c709d584b0a5dce54d2ffd2fc62708f767`。画面可见版本、连接 iPhone 提示和 Clear pairing 按钮。 |
| 持续观察及诊断 | `PASS` | 60.255 秒、13 次观察。非空画面随 ZIP 留存，且与审核保存的 PNG 字节一致。结构化诊断未观察到主要 panic 或重复 CPU 复位。 |
| 交互请求准入 | `FAIL` | 中心触摸返回 `input_requires_matching_elf`，拖动返回 `unsupported_input`。两个请求均未触发画面变化。 |
| USB host、手机连接及触摸行为 | `NOT RUN` | 实验只到达等待手机的画面。 |
| 整体审核 | `PARTIAL` | 审核为 `E_INTERACTION_CLAIM_PARTIAL / SIM_PARTIAL`。 |

检查 ZIP CRC、原始串口字节范围、诊断身份和 PNG 字节一致性均通过。具体 SHA-256 和大小见[脱敏证据](evidence/carplay-native-dsi-summary.json)。

## 边界与回滚

原版应用 ELF 仍未匹配，所以本机测试只验证原生 DSI 的画面通路。GT911 识别配置用于固件启动和面板识别。物理显示方向、USB 枚举、手机连接与实时触摸未经验证。诊断、USB 和触摸结论按不同证据范围保留。

该 DSI 后端通过环境显式启用。若需要回到旧运行方式，移除两个 DSI 参数即可使用之前的 ELF 门槛。已结束隔离会话并释放临时 Flash 和租约。未动常驻服务，未提交 Burner。
