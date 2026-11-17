# Linux 原生 STA、Tab5 审核归因与 PaperS3 触摸复验

本轮使用三个独立虚拟设备路径。Linux 原生 Device Service 及 Tab5 当前审核运行绑定 `63472ab884dc2968904999c75eb6aca91c3f2517`，PaperS3 独立浏览器运行绑定 `a2148953f1c22a2b2b066780f9c501b3daddcdf0` 与冻结 WASM。归档源码 `36b091f9766209d2fbc1c28d717ea065cd035d96` 收录两个实跑证据和状态更新。整体为 `PARTIAL`，以下结论均为 virtual-device validation。

## Linux Cardputer 与 Cardputer ADV 原生 STA

在 Linux arm64 上使用真实 Device Service、原生 ESP32-S3 QEMU SHA-256 `1733f511c4528cbd991e673069ecedf261b7043e8302553e050924089ce09bff` 和同一 ESP-IDF v5.5.4 STA 探针 SHA-256 `f67e0a7a8e2805b01b3c2f9d1607ef6505467a60f4dd678d20a4576e56765db6`。Cardputer 及 Cardputer ADV 的直接会话各取得 DHCP DORA、受控 DNS 的 A 和预期 NXDOMAIN、HTTP 200、来宾校验通过的 UDP 载荷。两板的原生进程均通过 QEMU 二进制哈希读回。

原生来宾运行在独立私有网络命名空间，观察时没有外部路由和网关。网络收据确认回收来宾进程和关闭 DNS、HTTP、UDP 对端。五个实际来宾会话最终都停止，租约为零。每个会话的结束抓包各有一次 DHCP DORA、一条双向 TCP 载荷流、三条双向 UDP 载荷流。对 Cardputer ADV 启用内容负对照时，来宾仍收到 UDP 对端的一个应答，但由于响应相差一字节，串口记录 `udp=0`。同会话的 DORA、HTTP 和 DNS 保持通过。另一对照缺少私有命名空间能力，服务在分配前以 503 `network_isolation_unavailable` 拒绝创建来宾。

组合审核版本 `212843e7753195b8878943c97429b00c6d385995` 的原生 STA 计划分别为两板生成真实会话，均通过入场。停止后审核收集器保留 `OBSERVED`，其中抓包 SHA、DORA 和流量计数与会话一致。这里的 `OBSERVED` 表示传输层取证；来宾行为另由串口校验。早期观察脚本曾读取错误的 DNS 字段，也曾把 `OBSERVED` 误当成预期 `PASS`，两次观察脚本失败均保存在记录。范围为所测受控 IPv4 数据面，真机射频、浏览器 STA 和任意应用协议为 `NOT RUN`。[Linux 源码记录](https://github.com/m5agent/m5stack-esp-emulator/blob/36b091f9766209d2fbc1c28d717ea065cd035d96/tests/network/native_sta_peers/linux-session-summary.json) · [脱敏运行摘要](evidence/linux-native-sta-summary.redacted.json)

## Tab5 原版 CarPlay 触摸审核

对相同原版 BIN `4f3bb118a5570a6ba885a234fce55b66e28ef26091cfe4f3f2e4c33711471ea3`，在相同原生 DSI/GT911 运行时 `633a35f993300a765634ed78a2dbcfd5ffcd5c3f2f354a2dddabeb6108240828` 上用无 ELF 保存快照复审。当前 Device Service 约 60 秒观察中，中心点击和左滑分别收到 13、24 份 GT911 报告，画面均没有变化。较早 Device Service `6da7ab20351d732c6738fe13311f686efc856db3` 记录中心点击的 13 份报告，对自动左滑返回 409 `unsupported_input`。

审核实现将旧服务拒绝的具体输入投射为 `runtime_model_gap`，保留实际点击回执。原描述的触摸交互仍为 `PARTIAL`，通用左滑探针被拒绝后仍保留原有总体人工复核 `E_INTERACTION_CLAIM_PARTIAL`。最终审核源码上的同原版重跑再次得到 13/24 份触摸与滑动报告、画面不变及人工复核。会话停止、释放可写 Flash、租约为零。审核回归 185 项通过。USB Host 手机功能、实机和该固件浏览器运行均为 `NOT RUN`。[归因与最终复跑](evidence/tab5-original-carplay-summary.redacted.json)

## PaperS3 浏览器虚拟触摸与 GT911 准备状态

沿用同一官方 Factory V0.5 原版与冻结 QEMU WASM `96c7f8baf1d5f2fd760c560a0827ef7305ad06a1cefb28c905d05d796dc540d8`。在两个独立 Browser-WASM 会话以相同坐标发送 300 ms 输入，在引擎内通过按下确认和释放入队时间计算下限、以按下入队和释放确认计算上限。汇总得到 12 次输入的下限均至少 300.355 ms，上限均至多 342.650 ms。来宾没有 pause 或 reset。四次输入在实际按住窗口中直接读取到 GPIO48 ready 低电平，前、中、释放后早期分别为高、低、低。输入收据约束的是正在运行的虚拟接触窗口。来宾任务实际获得的运行时间尚未测得。

两组共 12 次都未达到完整图标切换。每次在按住窗口内未观察到 GT911 事务，释放后看到清旧报告、空 `0x80`、再清除。所测面板在稳定图标与可见刷新条件都记录到 ET047 扫描进度，两个条件无法区分真正空闲面板与 EPD 任务。已有的浏览器图标成功对照仍保留。本轮只排除了所测手势中的虚拟接触缩短和四次中点采样中 ready 未出现的解释。较晚处理的具体来宾任务或调度原因仍未定位。两个 Chromium 来宾退出，Worker 与 iframe 都归零。真机触摸力学和电子纸光学为 `NOT RUN`。[源码记录](https://github.com/m5agent/m5stack-esp-emulator/blob/36b091f9766209d2fbc1c28d717ea065cd035d96/docs/evidence/2026-11-18-papers3-browser-gt911/clock-irq-epd-summary.json) · [时序与 GPIO 摘要](evidence/papers3-browser-clock-summary.redacted.json)

## 复现和检查

Linux 按项目记录中的隔离 STA 探针构建与普通 Device Service 创建路径运行两种板，核对来宾串口和停止后的同会话抓包摘要。用固定错误应答复验 UDP，用缺少命名空间能力的独立服务复验入场拒绝。Tab5 用同一原版保存快照和 DSI/GT911 设备，以审核报告和运行层回执交叉核对。PaperS3 用冻结静态浏览器运行时、原版 BIN 和源记录内的输入观察条件，保留各次接触的时间上下界、GT911 操作和归零的 Worker/iframe 计数。归档源的 51 项文档测试和范围检查通过。[当前提交的 GitHub Actions](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44148738534)
