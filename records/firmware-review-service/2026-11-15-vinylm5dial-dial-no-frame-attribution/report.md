# 完整报告：vinylM5Dial 1.0 在 Dial 虚拟设备上无首帧

## 1. 来源与现象

固件审查任务 `job-7071ded9a698` 对 `vinylM5Dial : mp3 player 1.0`（设备 Dial）给出
`SIM_PARTIAL / manual_review / E_NO_FRAME`：静态检查通过，但虚拟设备在 60 s 观察窗口内
没有产生可证明应用就绪的非黑帧。目标目录内的证据（`analysis.json`、`execution-plan.json`、
`wait.json`、`logs.json`、`serial.log`、`qom-*.json`、`flash-*.json`、`observation.json`）
均为只读使用。

目标固件身份：

| 项目 | 值 |
| --- | --- |
| 设备 | Dial（SKU K130，ESP32-S3FN8，8 MiB Flash，无 PSRAM） |
| 版本 ID | 2122006759453179905 |
| 文件 | `dial.bin`，8,388,608 B |
| SHA-256 | `7778656ee942bb5e87fbc780955c452f752059c9cf9325d7e026b83ec6c7ffaf` |
| 应用描述 | `arduino-lib-builder`，IDF v5.5.5，app0 @ 0x10000 |
| 分区 | nvs / otadata / app0 / app1(空) / spiffs(未格式化) / coredump |

审查任务侧观测：

- 串口 226 B，止于 ROM `entry 0x403c88b8`，之后 60 s 无新字节；
- 帧 248 B 全黑（`4bf6fb04…`），两次输入探测后仍同帧；
- `wait.json`：`ready=false`，`phase=application_readiness`，`session_state=running`；
- `flash-diff.json`：`changed_bytes=0`；
- `qom-diff.json`：仅 `pcf8563/unix-time` 推进；
- 无 `emulator-failure.json`，无 QEMU 退出、断言或崩溃标记。

## 2. 判定路径

### 2.1 启动阶段

ROM banner 的 load 段（`0x3fce2820`/`0x403c8700`/`0x403cb700`）与 `entry` 行说明 ROM 已从
Flash 读出二级 bootloader 并跳转。目标镜像 bootloader 位于 0x0，符合 ESP32-S3 布局，不是
StickC-Plus2 那类「bootloader 错位到 0x0（应为 0x1000）」的打包问题。

应用段是否装载：在独立复跑中读取 app0 的 DRAM 段（0x3fc94c00）与 IRAM 段（0x40374000），
内容与镜像一致；IRAM 段包含应用自己的向量区。bootloader 只有在完成镜像校验与装载后才会
跳转，因此「bootloader 完全没跑」不成立。

### 2.2 是否 QEMU/模型退出或断言

`session_state=running`，QEMU 进程存活，串口没有 panic/assert/`Guru Meditation`/重启 banner，
Flash 0 字节变化。可排除 QEMU 断言、进程退出、镜像解析失败与固件 panic。

### 2.3 应用是否在运行

独立复跑（同一 QEMU binary、同一虚拟 Flash 副本、同一 `-M m5dial`）中：

- 双核 PC 采样长期落在 app0 IRAM 段内的 `0x40378dda`，即 `waiti 0` 的下一条 `retw.n`；
  PS 显示不在中断/异常上下文，`CCOUNT` 正常递增；
- UART1 以约 2.7 s 周期收到 5 字节 `04 fb 01 08 08`；
- 固件自身字符串包含 `VINYLM5 R1F30 BOOT | USB CDC | PORT B RX=1 TX=2 | 9600bps`，
  与 UART1 上的 Port B 报文一致。

结论：应用已运行并进入「空闲等待 + 周期发包」状态，不是「CPU 未启动」。

### 2.4 显示是否初始化

帧捕获同时给出面板呈现状态：

| 会话 | 帧 | 面板 generation | madctl |
| --- | --- | --- | --- |
| 目标固件 | 248 B 全黑 | 1 | 0 |
| 官方 UIFlow2 v2.5.3 对照 | 19,838 B 非黑 | 2 | 8 |

`generation` 只在面板收到 MADCTL 写入时递增。目标固件连一次 MADCTL 都没有，说明它尚未进入
显示初始化（或卡在初始化之前），而不是「已出画但被判定为非黑失败」。

### 2.5 同机对照

同一 `m5dial` 机器、同一 QEMU、同一 Device Service 路径下，官方 UIFlow2 v2.5.3 Dial 固件
（8,388,608 B，SHA-256 `6a0187da…32a53`）在约 1 s 内出现应用日志
（`E (837) i2c.master: this port has not been initialized`），随后渲染出 UIFlow2 Offline
界面（240×240，19,838 B，`3116e0eb…96372e`），面板 generation=2、madctl=8。

两侧在 ROM/二级 bootloader 阶段触发相同的 `M25P80: Read id ... not supported`、
`Unknown cmd 5a/7a/77` 与 `Invalid read at addr 0x10200C`（对照固件同样出现且正常启动），
这些是共同背景而非差异点。

因此 Dial 的显示链路、SPI 面板模型和会话取帧路径可用；本次失败不能归因到「整体机型不可启动」。
需要说明的是：UIFlow2 是 MicroPython/IDF 路径，目标固件是 Arduino lib builder 路径，
两者不共享板级初始化代码。

### 2.6 为什么没有归因到模拟器或固件

- 归因模拟器需要具体的模型缺陷证据（固定 PC 的断言、寄存器回读恒 0、缺失设备/总线、
  或可复现的模型行为差异）。本次没有捕获到；对照组反而证明显示路径正常。
- 归因固件需要 panic/assert 或功能层证据。本次没有崩溃标记，应用仍在运行，只能判
  「启动卡点未定位」。
- 应用诊断日志走 USB CDC：`misc.esp32c3.usb_serial_jtag` 在 Dial 会话里 `chardev` 为空，
  Device Service 只接 UART0/UART1。带 `-global ...property=chardev` 的独立复跑能把 ROM
  banner 复制到该通道，但目标应用在 USB CDC 上的日志没有出现，无法据此判断
  `display=` / `displayTask=` / `AudioPlayer startup wait=` 的取值。

结论：`E_NO_FRAME` 与 `manual_review` 的收口是正确的；本次不新开模拟器 issue，因为无法
把失败收敛到可复现的模型缺陷。

## 3. 复现步骤（虚拟设备）

1. 通过 Device Service 上传目标 BIN 为 artifact（`POST /api/v1/artifacts`，内容寻址，
   返回 SHA-256 与大小）。
2. 以 `device_id=dial`、`kind=merged` 创建 firmware（`POST /api/v1/firmware`），得到
   `firmware_id`。
3. 创建会话（`POST /api/v1/sessions`，`device_id=dial`、`firmware_id=<上一步>`，
   `ttl_seconds=600`）。
4. 轮询 `GET /api/v1/sessions/{id}/serial?offset=0`、`GET /api/v1/sessions/{id}/frame.png`
   与 `wait`（`frame_nonblank=true` 等就绪条件），观察 60–120 s。
5. 结果：串口 226 B 止于 `entry`；帧 248 B 全黑；`wait` 在 `application_readiness` 超时；
   面板呈现头显示 generation=1、madctl=0。
6. 对照：同步骤替换为官方 UIFlow2 v2.5.3 Dial 镜像，得到 394 B 应用日志与 19,838 B 非黑帧，
   generation=2、madctl=8。

独立离线复核：用会话的虚拟 Flash 副本、相同 `qemu-system-xtensa -M m5dial`、相同
`-drive`/`-global` 参数启动，QMP 采样 PC/PS/CCOUNT 并读面板呈现状态；未修改模拟器代码。

## 4. 影响面与兼容性

本次未改动代码、未提交 patch、未 push、未关闭 issue。审查结论维持 `manual_review`，
证据与历史失败保留。

## 5. 未覆盖项

- 真实 Dial 上该 BIN 的启动与画面：`NOT RUN`。
- 应用 USB CDC 日志（`display=` / `displayTask=` / AudioPlayer 启动等待）：`NOT RUN`。
- 卡点的外设归属（硬件 I2C、SD、I2S、USB）：`NOT RUN`。
- 音频输出、SPIFFS 内容、电气与声学：`NOT RUN`。
- 浏览器 WASM 路径：`NOT RUN`（本次为原生 QEMU 路径）。

## 6. 下一步建议

1. 在真实 Dial 上灌同一 SHA 的 BIN，确认是否出现画面与音频；这是区分「固件自身」与
   「虚拟设备路径」的最短路径。
2. 若真机正常，再补 Dial 的 USB Serial/JTAG 会话通道（参考 StickS3 的 CDC 捕获实现），
   用应用自身日志定位停点，再决定是否开模拟器 issue。
3. 若需要在虚拟设备上继续定位，应提供带符号的 ELF 或可打印串口的构建；当前只有合并 BIN，
   无法把停点收敛到具体函数。
