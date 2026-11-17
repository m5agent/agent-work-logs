# 原生语义输入与虚拟 FAT32

## 原生输入

原生 ADV 沿用早期字母范围算法。完整的物理布局依赖 56 项显式 QKeyCode→TCA8418 映射，与 UIFlow2 guest I²C 驱动读回相符。旧运行时缺少能力属性，公共语义输入提前报告不支持。相同测试镜像走旧 raw Q 入口时无 guest 键事件。

Device Service 单键调度走虚拟时钟，组合边沿以同组 QMP 事件提交。StickS3 同次复验记录 A 双击、A+B 同时按下和 B 4994 毫秒长按，独立前次记录 4999 毫秒。K132 官方固件基底加测试 VFS 读到 Fn+分号及释放，Core2 读回两次 (67, 110) 原始触点及释放。初次试验的错误 HTTP 前缀发生在建会话前，K132 初次 guest 的成员测试引发 NotImplementedError，改用原驱动的索引方式后重新取得数据。

Dial 的九个旋转请求全部到达正交边沿目标，共 120 边沿，原 RotaryIRQ 应用计数 3/9。原版 Grok Bot MultiFace 通过关提交的保存快照审核重放，截图有效，双击与组合各一条记录，功能断言不足仍为 E_INTERACTION_CLAIM_PARTIAL。

## SD

存储候选根据实际板级挂载能力接纳 K132 和 PaperS3 设备端口，阻止 diagnostic network 路径忽略 storage。利用 ESP-IDF SDSPI/FAT 真实 guest 测试 K132、PaperS3、已有 ADV 对照，验证同一可写卡挂载、目录、预置内容、客体写入及重挂载。K132 下一个会话读到前一会话写入，无卡负对照分开保留。宿主使用独立 FAT 解析库核对保存卡，原 fixture SHA 保持不变。内部文件系统、自动导出、PaperDIY 卡检测及更多原版应用仍待验证。

## 复现

使用元数据中固定的候选源码、原生 Xtensa 和固件 SHA。启动独立 Device Service，从源码目录执行 `tests/uiflow2/api_sweep/run_hardware_guest.py`，分别用 code 目录同名文件作 `--source` 与 `--drive-json`，终止标记为 `SK_DONE`、`KB_DONE`、`TS_DONE`。串口读回来自这些客体驱动，HTTP 回执和末帧分别留档。ADV 使用真实 MatrixKeyboard 回调与按下/释放，逐物理键并用相同镜像做旧运行时负控。SD 验证使用存储候选的 `tests/firmware/spi_sd_media/` ESP-IDF fixture。各服务从受控独立端口取证后停止，保留历史。

本记录的摘要删除了进程、会话和设备标识与本机路径。功能结论限于实际执行的原生数据面，未进行物理和 WASM 运行。
