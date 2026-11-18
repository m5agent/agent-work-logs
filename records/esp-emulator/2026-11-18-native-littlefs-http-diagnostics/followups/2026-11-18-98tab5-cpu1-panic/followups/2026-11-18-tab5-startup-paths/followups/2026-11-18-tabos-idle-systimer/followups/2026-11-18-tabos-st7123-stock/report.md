# M5TabOS 0.9.1 原版的板型、出帧与触摸对照

此前的原版 GT911 样本确认两核处于空闲任务且定时中断正常。此次固定原版上传 SHA-256 `08aa10d0caeaf7835cd2f93ee66a8d2042ce15bd6e52350df6b96c70ec8bbe3e`、归一化后 SHA-256 `8def8f22155f9b7459c75de9aea02f6401ccc5f65341fcf52a5e6992b9c875ec`、Device Service 源码 `57d397462e661e608e7c3ae2a878e80527d08e84`、原生 esp-emu 1.1.0 与同一 P4/C6 工件。只在隔离会话中切换板型和部件。[此前中断对照](../../README.md) · [本次证据](evidence/tabos-stock-board-touch.summary.json)

## 原版启动和板型对照

| 配置 | 执行 | 完整帧 / 非黑帧 |
| --- | --- | --- |
| GT911 静态识别寄存器 | 两次只读采样。A5 取得启动阶段，A6 补齐任务链和显示读回。 | 两次均 0 / 0 |
| GT911 完整部件 | 一次只读采样。 | 0 / 0 |
| ST7123 用于识别的 GPIO I²C 部件 | 一次只读采样。 | 11 / 11 |
| ST7123 完整触摸部件 | 一次只读采样、一次无调试器且无原生 trace 冷启动、一次无调试器的触摸 trace。 | 分别 11 / 10、16 / 15、16 / 15 |

GT911 的原版应用内启动记录含 18 个标记，执行经过 `app_main`、`M5.begin (painel, toque)`、UI 任务启动与 `sistema_iniciar (fim)`。A6 的原版 UI 任务优先级为 4，三次都采到带推进的延时唤醒计数，event list 为空。三个样本的面板对象使用只返回的虚方法，应用尺寸 0×0，DSI 主机保持关闭，桥接禁用。ST7123 样本的应用尺寸为 720×1280，DSI 主机和桥接已启用，能渲染出 M5TabOS 欢迎页。使用 ST7123 识别部件已经足以取得显示。未配置必需识别部件的 A10 由服务在原生机器启动前拒绝，单独留证。[原版启动记录和寄存器](evidence/tabos-stock-board-touch.summary.json)

## 欢迎页原生触摸

在完整 ST7123 部件的同一原版会话，以面板坐标 `(530, 1147)` 点击 `PRÓXIMO`。前后真实 720×1280 非黑帧分别显示 “Bem-vindo ao M5tabOS” 和 “Fuso horário”。服务返回 2 个报告、2 个已读取。原生 co-sim 按来宾时钟记录 GPIO23 的低高低高边沿，以及 HP I²C 控制器 1 对 0x55 的实际读取。按下时寄存器 0x10 返回 8，坐标寄存器 0x14 的原始字节解码为 (530, 1147)，抬起后状态寄存器返回 0。手势结束时部件回到无接触和无待读报告。此会话用普通 HTTP 路径，只额外开启原生 co-sim 通信日志参数，未连接调试器。[触摸、IRQ 与两帧哈希](evidence/tabos-stock-board-touch.summary.json)

## 复现与清理

按回执匹配原版、原生后端以及每个板型使用的部件。通过标准 API 上传、导入并在每种配置单独创建会话。取同一会话的 `frame.png?max_age_ms=0&orient=panel`。诊断会话在约 4、10、16 秒读原版内置启动记录、任务链与 DSI 状态。无调试启动对照不连 GDB。在完整 ST7123 触摸会话等待欢迎页，在葡萄牙语默认界面点击右下 `PRÓXIMO`，保存前后帧和控制器回执，启用可选原生 trace 复核 GPIO23 及地址 0x55。在停机前下载同会话证据 ZIP，核对清单内每个文件的大小、SHA-256 和归一化 Flash 身份。各轮均停机并清理所属进程、工作 Flash 和活动租约。[Device Service 复现和 ST7123 接线](https://github.com/m5agent/m5stack-esp-emulator/blob/57d397462e661e608e7c3ae2a878e80527d08e84/docs/device-service-api.md#L3301-L3310)

本记录覆盖已验证板型的显示与指定触摸。GT911 路径的底层差异、外网与账号操作、USB 设备枚举、浏览器和实体硬件未验收。未提交 Burner。
