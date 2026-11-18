# Nesso N1 原版的四种 UART1 应答

## 版本与方法

使用 [Device Service 1.89.0 固定源码](https://github.com/m5agent/m5stack-esp-emulator/tree/13df3b8a7ab197df14f57d2ca8bc58919a7eb666) 和 macOS arm64 原生 C6 QEMU 发布二进制。原版是 Meshtastic RFID Demo 2.7.21 Landscape。运行时、ROM、原 BIN、规范化 Flash 和原生面板帧均在[回执](evidence/nesso-rfid-uart1-summary.json)绑定完整 SHA-256。

通过 Device Service 的固件上传、导入和会话接口创建独占会话。启动时仅把原本写入 UART1 文件的后端换成诊断 Unix socket，保留文件镜像便于核对。UART0、USB Serial-JTAG、UART1 控制器读写和 FIFO/中断路径保持原样。每轮为冷启动，使用相同 Flash 字节和默认时钟观察至少 25 秒。没有按键或调试器介入，隔离配置保持离线。探针只回应已识别且校验通过的 UART 帧。

## 执行结果

| 独立冷启动 | UART 等待超时 | 数据校验错误 | 长度校验错误 | 软件复位 |
| --- | ---: | ---: | ---: | ---: |
| 接通对端且保持静默 | 4 | 0 | 0 | 1 |
| ACK 加响应，数据校验改变一位 | 0 | 4 | 0 | 1 |
| 只发送响应帧，故意缺少 ACK | 0 | 0 | 3 | 1 |
| ACK 和正确校验的 SAM 响应、无数据的厂商查询响应 | 0 | 0 | 0 | 1 |

原版两次发出相同顺序的查询和初始化请求。每轮 UART1 发送字节共 72，SHA-256 与上一轮未接对端的 UART 日志完全一致。第四轮中，原版打印标准 SAMConfiguration 应答帧后，把数据校验字节和结束字节打印为两字节数据。原版指令使用完整帧 LEN 作为拷贝长度，源地址已经跳过 TFI 和响应码。厂商检测分支还要求返回数据向量至少 3 字节。这里的 D5 AB 仅重建公开厂商客户端支持的查询应答外壳，实际私有数据未得到确认。[NXP §7.2.10](https://www.nxp.com/docs/en/user-guide/141520.pdf#page=89) · [已固定的厂商客户端命令](https://github.com/whywilson/pn532-python/blob/4761db79625e5b764104c4ef36eab080758f6088/script/pn532_enum.py#L39)

每轮均观察到原版上电和一次 LP_SW_HPSYS 软件复位，原版仍报告厂商 NFC 初始化失败。同轮原厂应用 Flash 分区读回保持一致，四轮都取得同一张非黑面板帧。先校验同会话证据 ZIP，再停止会话并释放 Flash，零剩余租约。四轮是 UART 收包与解析的诊断，不能推翻此前独立的 IDLE 看门狗证据。标签读卡和实机行为均为 NOT RUN。

## 复现

1. 准备回执列出的原版 BIN、C6 QEMU、ROM 及固定 Device Service 源码。在新状态目录启动独占服务，导入原版并核对规范化 Flash。保留默认时钟。
2. 在宿主复现程序中导入随记录附带的 UART 诊断对端 Peer 类，用临时目录、证据目录、固定 QEMU 路径和模式构造实例。将该实例的 wrapper 作为服务的 M5_QEMU_RISCV32。分别新建静默、错误 DCS、省略 ACK、正确 ACK/校验四个会话，模式分别是 silent、bad-dcs、response-only、killer。
3. 每轮读取实际 UART0 和 USB Serial-JTAG，按回执匹配四种错误和正确帧，采集帧与 CRC 有效的证据 ZIP。关停该会话并保留历史，释放工作 Flash。服务退出后调用 Peer.close 核对 UART1 双向字节和对端线程退出。全量宿主信息和原始 ZIP 仅留在受控测试目录。

没有变更产品源码。移除临时运行目录和串口对端即可结束本轮环境。
