# 同一原版面板对照

三次独立会话使用相同的原版 BIN、规范化 Flash 和 1.1.0 原生后端。每轮先通过标准制品上传与导入接口重新验证 SHA-256，再创建 Tab5 会话。为控制磁盘残留，仅对已核验的相同不可变输入创建 APFS 写时复制。记录由本轮 API 新建，可写会话 Flash 和 eFuse 副本独立持有。证据 ZIP 在停止前取回，逐条核对 CRC、大小和 SHA-256。三轮均核对运行后应用分区字节、Flash 释放、零活动租约及 P4/C6 进程退出。

| 运行 | 实际观察 | 判定 |
| --- | --- | --- |
| GT911／ILI9881C 普通冷启动 | 20 秒内 0 个完整帧，9 次原生 DSI 取帧明确返回不可用。串口 406 字节，单次上电且无软件复位或看门狗 | FAIL，面板探测 |
| GT911／ILI9881C 单独诊断 | 原版 DCS 命令 0x00 从实际 RX FIFO 读到零。API 返回成功与数据 0x00，应用比较读到 `00 00 00`，首字节期望 `0x98`。同样无完整帧，串口与普通冷启动逐字节一致 | PASS，归因 |
| ST7123 普通冷启动和触摸 | 11 个完整 720×1280 帧，其中 10 个非黑。原生触控在 (83,308) 生成两个报告并获两次来宾确认，帧从离线主页到 I²C Scan | PASS，离线界面和该次触摸 |

## FIFO 观测

只在诊断会话附加 GDB。脚本先用硬件断点命中原版读取接口，跟踪其动态调用的驱动，再观察来宾指令实际执行的 MMIO 操作。`GEN_HDR` 先写入 `0x137`，将最大回复长度设为一个字节。随后的 `0x06` 是 DCS 读请求。CPU 从 `CMD_PKT_STATUS` 地址 `0x500A0074` 读到 `0x50005`，读 FIFO 空标志与读命令忙标志均为零。紧接着，原版指令在 `0x482BAC1A` 从 `GEN_PLD_DATA` 地址 `0x500A0070` 取到零。脚本读取 CPU 执行后的寄存器和普通 RAM，未用调试器直接读取 FIFO 或注入面板数据。接口返回成功，后续板型比较首字节与 `0x98` 不一致。[Espressif ESP32-P4 寄存器定义](https://github.com/espressif/esp-idf/blob/v5.4.2/components/soc/esp32p4/register/soc/mipi_dsi_host_reg.h#L628-L712)

1.1.0 的 `DsiEvent` 可向认领虚拟通道的面板交付命令。官方 ABI 将其定义为单向通知，协议记录说明读端由后端以零完成。需要一个有界面板响应，让真实响应字节与长度在来宾等待期间到达已有 RX FIFO，并让 FIFO 状态与读取行为一致。当前接口范围由官方版本说明与本轮实际 CPU 证据交叉确认。[Espressif 1.1.0 发布记录](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0) · [固定版 Part ABI](https://github.com/espressif/esp-emulator/blob/v1.1.0/proto/PART_ABI.md) · [固定版 DSI 消息](https://github.com/espressif/esp-emulator/blob/v1.1.0/proto/esp_cosim.proto#L1018-L1045)

## 复现

1. 准备摘要中固定的公开原版、esp-emu、板级 Part 与 P4 ROM、eFuse seed、C6 companion 资料。
2. 启动独立 Device Service，设置 `M5_TAB5_DSI_EMULATOR`、`M5_TAB5_DSI_BOARD` 和对应的 `M5_TAB5_GT911_PART` 或 `M5_TAB5_ST7123_TOUCH_PART`。把规范化镜像 SHA-256 放入该试验的 `M5_TAB5_DSI_FIRMWARE_SHA256S`。经标准 API 上传、导入并创建原生 `qemu` 会话。
3. 独立 GT911 对照先保留正常冷启动的串口、帧返回和 ZIP。将只读脚本加载到另一次拥有的 GDB 会话，采用 `riscv:rv32` 架构并附加该 P4 进程。输出 `FIFO_OBSERVATION` 汇总，随后断开。继续以 API 收集同会话串口和 ZIP。
4. ST7123 冷启动确认主页后，按面板坐标执行原生 tap，核对两个控制器回复与实际 I²C Scan 页面。结束每轮前取得 ZIP，停止时保留会话历史并释放可写 Flash。

真机、浏览器、联网、配对、脚本执行、I²C Scan 的数据结果及非零面板回包正对照均为 NOT RUN。Burner 未提交，常驻服务无变更。原始固件、会话标识、内部端点和原始 ZIP 留在私有执行目录。
