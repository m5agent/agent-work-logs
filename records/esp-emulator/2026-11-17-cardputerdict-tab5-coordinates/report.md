# 两项原版固件审核复验

两项使用普通 Device Service 会话和隔离的 saved_snapshot 审核。启动画面、输入、外设回执与清场以同一会话为单位。Device Service 源码为 fd08569f06b4afa478eb46da3654c4468e35a5bb。完整身份、证据 SHA-256 和测试范围随记录保存。

## CardputerDict 0.6.4

普通 Cardputer 上使用 M5Stack Xtensa QEMU。保留原版完整合并镜像，Flash 归一化只在尾部补 0xff，未替换引导或应用字节。以自编三词的 FAT32 测试词库核对实际查词。 [发布者目录扫描与加载代码](https://github.com/RadioDisney/CardputerDict/blob/4b69cef2c59ef443eea191aa8e1b6bbef6178595/src/main.cpp#L355-L385)

| 同原版会话 | SD SPI CMD17 | 画面结果 |
| --- | --- | --- |
| 完整词库 | 131 | 打开 zorbax，显示 MINT CACHE 7319. An invented test word. |
| 缺 ecdict.dict | 82 | 回退内置演示，测试词义未显示 |
| 无卡 | 0 | 回退内置演示，测试词义未显示 |

完整卡与缺正文卡的源 SHA 均有 Device Service 存储回执。完整卡的查词帧与实际审核器的 Enter 帧逐字节一致。词义采用原始 240×135 帧目视确认，并以最近邻放大四倍后的 OCR 交叉核对。审核器启动检查通过，观察 60.014 秒和 13 个样本。离线查词 PASS，整项审核仍为 SIM_PARTIAL。 [会话和对照摘要](evidence/cardputerdict-summary.json)

复现时将未压缩 UTF-8 StarDict 2.4.2 的 ecdict.ifo、ecdict.idx、ecdict.dict 放入 FAT32 根目录下的 dictionaries 目录。三个文件后缀使用小写，.ifo 的 sametypesequence 为 m，.idx 由排列后的词头、NUL 以及大端 u32 偏移和长度组成。三个自编词条为 ambercat → A fictional amber-colored cat.、quillfern → A fictional fern shaped like a quill.、zorbax → MINT CACHE 7319. An invented test word.。数据以 CC0 提供。启动后清空默认的 apple，按 z、o、r、b、a、x，待屏幕稳定，再按 Enter。独立启动缺正文卡和无卡对照，重复输入。

初次 FAT 短文件名遗漏小写标记，导致固件略过大写 IFO。另一次过早采帧，虚拟按键队列尚未全部执行。初次原尺寸 OCR 误认一位数字，随后以目视及最近邻放大完成核对。普通 Cardputer 的 0.3.0 在公开目录显示已发布，本地无原始快照。普通下载端点返回 HTTP 400 并要求验证码，旧 CDN 与发布者 v0.3.0 发布页均返回 HTTP 404。0.3.0 未取得可信原件，因此未执行。朗读、Wi‑Fi、维基语料、ADV 和实机未验证。 [公开版本记录](https://burner.m5stack.com/api/v1/firmwares/2120468585455984642/versions)

## Tab5 CarPlay 1.0.0

Tab5 使用 Espressif esp-emu 1.1.0 macOS arm64 与 GT911 ESP Part。原版经 ILI9881C 板型原生 DSI 输出 720×1280。旧审核器使用目录的 1280×720 计算中心点，实际发送过 (640,360)。候选只在会话明确报告原生 DSI 与 panel-native 触点时，从同一会话的原始 PNG 读取带 CRC 的 IHDR。候选单测核对显式拖动坐标按原值传递并以原生帧尺寸校验。 [Espressif 发布版本](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0) · [板型问题 #227](https://github.com/m5agent/m5stack-esp-emulator/issues/227)

实际 saved_snapshot dry-run 发送校正后的 (360,640)，返回 13 份报告和 13 次来宾 I²C 确认。中心点前后画面相同。拖动返回 HTTP 409 unsupported_input，语义审核保持 SIM_PARTIAL。启动检查通过，观察 60.273 秒和 13 个样本，释放会话 Flash，无剩余租约。候选提交和实际重放归档的 Git 源树完全相同。 [坐标和回执摘要](evidence/tab5-coordinate-summary.json)

单独的一次正常 Device Service 正控里，(320,500) 空白处点击通过 I²C 确认且画面不变，(640,160) 打开 Clear phone pairing? 对话框。这个功能动作发生在独立会话。审核器中心点只证明坐标与控制器传递，仍无应用语义证据。保持打开未确认清除。至少一次早期启动在 32 秒内未取得 DSI 帧，启动重复性仍有边界。

## 边界与交付

两项均为虚拟设备验证。Tab5 的其它板型、浏览器触点映射、多指、USB Host 和 iPhone 数据面未覆盖。隔离实例和可写 Flash 已清理，没有更改常驻环境，不涉及设备刷写。未提交 Burner。
