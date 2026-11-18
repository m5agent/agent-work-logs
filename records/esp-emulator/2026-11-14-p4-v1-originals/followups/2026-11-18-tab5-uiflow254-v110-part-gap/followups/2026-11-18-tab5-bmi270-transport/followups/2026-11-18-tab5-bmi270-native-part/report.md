# Tab5 原版 BMI270 传输修复和触摸回归

## 现象与实现

旧 Part ABI 缓冲区为 1,024 字节，无法接收原版 UIFlow2 v2.5.4 的 BMI270 配置事务。前次诊断分开测量了宿主声明的 8,205 字节编码帧和真正解码出的 8,192 字节配置。两种面板共享这条早期 I²C 路径。[前次诊断](../../README.md)

`f7f6b53` 将 GT911 和 ST7123 Part 的事务缓冲区扩至 16 KiB，保留 144 KiB 的 Part 模块准入上限和旧模块的显式兼容。两个 Part 通过 HP I²C1 地址 `0x68` 共用 BMI270 模型。原版来宾将配置写入 `INIT_DATA`（`0x5e`）。全部地址写齐、摘要与标准配置一致并收到 `INIT_CTRL` 完成请求后，模型才在 `INTERNAL_STATUS`（`0x21`）报告初始化成功。仓库只固定标准配置摘要。模型未执行上传的传感器程序，也未模拟运动数据。[实现提交](https://github.com/m5agent/m5stack-esp-emulator/commit/f7f6b53eed43257b21d9bec291088c8c5e2648f6) · [共享模型](https://github.com/m5agent/m5stack-esp-emulator/blob/f7f6b53eed43257b21d9bec291088c8c5e2648f6/platform/esp-parts/tab5-bmi270.rs) · [Bosch 标准配置源码](https://github.com/boschsensortec/BMI270_SensorAPI/blob/41129fcfe39c583ee5462d79195741945d51c1fe/bmi270.c)

## 原版虚拟设备验证

| 固件 / 板型 | 来宾行为 | 结果 |
| --- | --- | --- |
| UIFlow2 v2.5.4 / `st7123` | 配置上传 8,192 字节，状态 `1`，读取一次。面板采到 9 张非黑帧；一个原生触摸产生 2 份都获确认的报告，离线启动页打开 I²C Scan 菜单。 | `PASS`（离线启动、页面切换） |
| UIFlow2 v2.5.4 / `gt911-ili9881c` | 同一原始 BIN，配置上传和状态读取通过，出现 DSI 零读回与面板识别失败，0 张有效非黑帧。 | `PARTIAL`（BMI270 通过，原版界面未就绪） |
| Arduventure / `st7123` | 原生触摸 2/2 确认，速度切换 `1X → 2X`。 | `PASS`（速度切换） |
| CarPlay / `gt911-ili9881c` | 原生触摸 13/13 确认，离线确认窗口出现；未确认窗口。 | `PASS`（窗口出现） |

四项 Part 回归在冻结的 Device Service 代码上，仅替换准入的两个候选 Part 摘要，适用的代码与运行时均写入收据。最初 ST7123 候选摘要中的录入错误保留为初始化失败。首次 CarPlay 脚本把 ST7123 的报告数量应用到了 GT911，已作为采集断言错误保留，后续同板控制核对了真实确认数。[四项 Part 回归摘要](evidence/tab5-native-qualification-summary.json)

最终源码重放从 `f7f6b53` 的完整 Git 源码启动隔离 Device Service，加载两个正式 Part，显式将原版映像映射到 `st7123`。回读确认应用字节未变，未提供 ELF 符号。保留的 ST7123 板配置与返回能力一致。标准触摸输入 `(83, 308)` 得到 2/2 控制器报告确认；触摸记录核对了同会话历史。标签和地址表证实由离线启动页打开 I²C Scan 菜单。后帧为 720×1280、989 色，哈希 `9963d5edcd9f6fccd58f7daf4709092bc234ef2064946d8f604f4f103513fb41`。另存的菜单 PNG 与该会话 ZIP 中的当前帧哈希不同。独立回读核对了同一会话，以及两张图中相同的 I²C Scan 侧栏和地址表区域。页面里的扫描按钮未点击。[最终源码重放摘要](evidence/tab5-native-service-replay-summary.json)

四项 Part 回归与最终源码重放的同会话 ZIP 均校验 CRC 和清单，保留串口、帧或设备状态证据。结束后会话已停止，Flash 已释放，无活动租约或剩余自有进程。无运行实例的第一次源码重放仅遇到参考资源缺失，未计入来宾结果。各轮证据回执分别保留。[证据文件索引](evidence/README.md)

GT911 的原版剩余缺口停在现有 DSI 读回与面板识别。esp-emu v1.1.0 的协议定义说明 DSI 读回返回零。CarPlay 的弹窗结果仅覆盖其已验证路径，UIFlow2 的 GT911 面板分支仍是 `PARTIAL`。[esp-emu v1.1.0 DSI 协议](https://github.com/espressif/esp-emulator/blob/v1.1.0/proto/esp_cosim.proto#L1084-L1100)

## 复现与边界

使用 `f7f6b53` 源码及 Rust `1.88.0` 配合锁定的 esp-emu v1.1.0 SDK 重建两个 Part，比对文件大小与 SHA-256。GT911 为 118,355 字节，ST7123 为 130,425 字节。两者均低于 147,456 字节上限。[GT911 构建](https://github.com/m5agent/m5stack-esp-emulator/blob/f7f6b53eed43257b21d9bec291088c8c5e2648f6/platform/esp-parts/tab5-gt911/README.md) · [ST7123 构建](https://github.com/m5agent/m5stack-esp-emulator/blob/f7f6b53eed43257b21d9bec291088c8c5e2648f6/platform/esp-parts/tab5-st7123-gpio/README.md)

在隔离 Device Service 设置 `M5_TAB5_DSI_EMULATOR`、`M5_TAB5_GT911_PART`、`M5_TAB5_ST7123_TOUCH_PART` 与显式的原版 SHA 准入。分别选择 `st7123` 或 `gt911-ili9881c`。对照收据中的运行时、ROM、eFuse、C6 附属固件、原版 BIN 及规范化 Flash 哈希。通过设备状态检查 BMI270 配置字节数、状态与读取计数。使用 panel-native 坐标输入，核对控制器报告与前后帧，在停机会话前导出同会话证据。[固定 API 使用文档](https://github.com/m5agent/m5stack-esp-emulator/blob/f7f6b53eed43257b21d9bec291088c8c5e2648f6/docs/device-service-api.md#create-a-reference-uiflow2-device)

Rust Part 单测共 8 项，相关服务测试 60 项。平台全量套件运行 2,440 项，其中 10 项按测试条件跳过，其余通过。覆盖、外设目录、QEMU 档案和项目快照四项检查通过。证据提交 `13df3b8a` 相对于原版重放版本只增加说明和收据，文档 51 项检查通过，最终提交的两项 GitHub Actions 检查通过。[固定验证台账](https://github.com/m5agent/m5stack-esp-emulator/blob/13df3b8a7ab197df14f57d2ca8bc58919a7eb666/docs/validation-ledger.md) · [最终 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44249549298)

长按、拖动和关机能力通过返回元数据或实际板配置核对，这次原版重放只发出一次点击。I²C 扫描结果、网络、配对、浏览器与实机均未执行。Burner 未提交。准入表继续接受此前固定模块摘要，保留对应旧行为的复现路径。
