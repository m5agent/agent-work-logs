# 浏览器固件检查反馈复验

反馈覆盖浏览器控制工具的本地选档权限、慢启动、SHA 语义、触摸、REPL 与下载事件。浏览器扩展在选档完成前拒绝操作时，工作台没有文件可校验。新版显示选档结果，并由 Skill 指引使用浏览器原生文件选择器继续。页面会记录下载请求，实际文件由浏览器下载列表或允许访问的下载目录核对。

工作台将 WASM/ROM 准备、客体开始执行、首帧和应用标记分开。只有绑定该运行 Flash SHA 的串口标记确认应用就绪。启动后保留到的首帧和目视可见的应用 UI 仍按各自证据报告。新运行清除前一次画面、串口、摘要与下载入口。旧回执的 `receipt.firmwareSha256` 含义保持为实际运行 Flash，新增字段列明输入、运行和补齐字节数。

## 复现方法

- 正式站点选择 CoreS3 的 **原始程序（正常时钟）**。执行 `platform/tests/test_public_qemu_guest.mjs`，设置 `M5_PUBLIC_URL` 为公开站点、`M5_QEMU_EXAMPLE=stock-reference` 及 `M5_WASM_GPU=hardware`。平面触屏坐标按 320×240 映射到可见画布，按钮中心 (160,184) 按下约 650 ms 再释放。核对客体事件、实际 Clicks 区域与独立 PIR 序列。
- 用 `platform/tools/build_public_site.py` 将改动导出为静态站，指定相符的源构建 Xtensa/C61 QEMU 与 LittleFS 产物。选择 CoreS3 和 **本地文件**，选官方 v2.5.3 merged BIN，填写输入 SHA，选择浏览器本地运行。等待平面触屏显示 Develop，核对两种 SHA、`boot` 字段及下载同次 JSON。主动运行默认代码以单独观测 REPL 握手结果。点停止，确认同次记录和 Worker 退出。用错误输入 SHA 发起下一次运行，校验上一轮证据没有残留。 [官方 BIN](https://m5burner-cdn.m5stack.com/community/1/1897200000000001950/2102696305989775362/bin/2102696305989775363.bin)
- 同一导出站另运行 `M5_UIFLOW_SMOKE_ONLY=1` 的 `platform/tests/test_public_uiflow_guest.mjs`。核对 UIFlow2 绑定启动标记、默认代码重跑、UTF-8 和多行代码输出及正常清场。

## 结果和范围

| 层级 | 结果 | 依据 |
| --- | --- | --- |
| build | PASS | 平台 2,051 项通过、10 项跳过，浏览器契约、静态导出和 Skill 归档通过 |
| flash（虚拟） | PASS | 选档并校验原始 BIN，归一化到 16 MiB，两个 SHA 与显示、回执一致。错误摘要负控拒绝 |
| transport / device_response | PASS | 同次 ROM 启动标记、运行记录和正常退出。内置编程样本可通过 UART 执行代码 |
| data_behavior | PASS | 正式站点分别实测触摸按压与释放、PIR 的控制器和客体回读 |
| visual_or_physical（虚拟） | PASS | 真实 CoreS3 320×240 Develop 画面和固定示例计数变化 |
| REPL（原厂 BIN） | PARTIAL | 已实测网页握手超时，应用画面与运行状态保持。未定位固件内部原因 |
| 短点击与真机 | NOT RUN | 使用已记录的定时指针序列，未复验原反馈的一次短点击和物理设备 |

新下载状态覆盖页面生成和发出请求，不代表浏览器已经写盘。本轮隔离 Chromium 的自动下载获得实际 JSON。该结论不转授不同扩展权限配置。原先部署资源的 patch lock 与新版源码不同，导出验证使用与当前源码一致的构建产物。范围只授予本轮对应 CoreS3 镜像和配置。页面更改可通过回退本次源码提交撤销。
