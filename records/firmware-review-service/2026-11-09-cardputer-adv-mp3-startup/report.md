# Cardputer ADV MP3 Player v1.0.0 启动复核报告

## 背景

同一份公开合并镜像在 Cardputer ADV 的虚拟设备上通过静态检查和 Flash 验证，随后出现黑屏。复核目标是定位启动停留阶段，验证延长等待和提供 microSD 是否改变结果，并用同板参考固件验证基线运行时路径。

- 固件来源：[v1.0.0 发布页](https://github.com/TurbulentGoat/cardputer-adv-mp3-player/releases/tag/v1.0.0)，[固定提交中的 BIN](https://github.com/TurbulentGoat/cardputer-adv-mp3-player/blob/fa967592011e9e8495ef3f540422eac4d6169adc/cardputer-mp3-adv.bin)。
- 合并镜像 885,600 字节，SHA-256 `c5918ff914a51b0dc4398f331c8306c25e26a4b157592d3e7d9c0dff2d0c5e45`。
- 目标镜像经过服务补齐为 8,388,608 字节的 Flash，SHA-256 `10d42a08a69d3e1f628fd9078015a64b598a74f02437c26ecc7201cc2db3e78d`。
- 上游文档描述了应用内的无卡提示。该提示属于进入应用后的行为。[固件故障排查](https://github.com/TurbulentGoat/cardputer-adv-mp3-player/blob/fa967592011e9e8495ef3f540422eac4d6169adc/README.md#troubleshooting)

## 结论

总体为 `PARTIAL`。默认 QEMU 板级接线触发了目标固件所用 Arduino I2C HAL 的自锁。来宾栈和内存确认 M5GFX 显示识别路径在恢复 I2C1 时挂起。受控对照仅移除四处默认挂载的外接 SPI Cap，同一固件、ROM 和 SD 镜像即出现应用界面。界面之后的 SD 初始化另有失败。

复跑使用既有 Device Service 和运行时。寄存器采样另开隔离诊断会话，只增加读取寄存器的观测。

## 证据

### 基线

基线使用 `m5cardputeradv` 原生 QEMU profile，未附加 microSD。就绪等待预算为 12 秒，运行观测约 14 秒。串口共 225 字节，末尾如下。

```text
rst:0x1 (POWERON),boot:0x4 (SPI_FLASH_BOOT)
SPIWP:0xee
mode:DIO, clock div:1
load:0x3fce2820,len:0xfb0
load:0x403c8700,len:0xaf4
load:0x403cb700,len:0x2e24
entry 0x403c8898
```

`0x403c8898` 是镜像二级 bootloader 的入口。镜像中 app0 的入口为 `0x40375cc4`。基线窗口内未出现应用日志或 panic。屏幕为 240×135，PNG 174 字节，0 个非黑像素，SHA-256 `877179afb0021d9147cc66ae65f30cb7c621cab992faa597c2a8eb9d8f5c99b6`。服务接收了 `a` 和 `b` 输入，帧保持不变。输入接收证明了 API 路径，应用响应需要同一会话中的状态或帧变化来证明。

### 复跑方式

Device Service 源码为 [ESP Emulator 固定提交](https://github.com/m5agent/m5stack-esp-emulator/tree/dd2eb35d2e6a909992268089ddc37e27970d4a92)。启动独立服务实例并配置自有状态目录。以下路径相对于服务的 `/api/v1`。

1. 下载公开合并镜像并校验 885,600 字节及上述 SHA-256。通过 `POST /artifacts` 上传原始字节，再调用 `POST /firmware`，指定 `device_id=cardputer-adv`、`kind=merged` 和返回的 `artifact_id`。
2. 通过 `POST /sessions` 指定 `device_id=cardputer-adv`、`runtime=qemu` 和相应 `firmware_id`。无卡实验省略 `storage`。有卡实验先上传 FAT32/MBR microSD 原始镜像，再传入 `storage.sd_image_artifact_id`。参考固件实验省略 `firmware_id`。
3. 等待进入 `running`，再于预定采样点读取 `/serial`、`/frame.png`、`/logs` 和 `/device-state`。应用就绪观测使用非黑帧判定，阈值为至少 1,024 PNG 字节及至少 16 个非黑像素。同时单独检查串口阶段和实际屏幕内容。
4. 从同一会话请求 `/evidence?include=manifest,serial,frames,logs,qom`，随后以 `DELETE /sessions/<session>?purge=0&retain_flash=0` 停止并保留历史，回读停止状态。

### 复跑观测

三个独立会话都使用 `m5cardputeradv` 原生 QEMU profile，运行时二进制 SHA-256 为 `6d9af027e2f744208fc2503128f1772f436d7ca7358f9e53be597bc76800f39d`。每个会话进入 `running` 后，分别在约 5、15、35 和 65 秒采样。

| 实验 | 65 秒时串口字节数 | 240×135 帧 | 就绪结果 |
| --- | ---: | --- | --- |
| 目标镜像，无卡 | 225 | 4 帧均全黑，0 非黑像素 | `ready_timeout` |
| 目标镜像，有卡 | 225 | 4 帧均全黑，与无卡帧 SHA-256 一致 | `ready_timeout` |
| 同板 UIFlow2 v2.5.3 参考固件 | 3,243 | 5 秒采样时已显示 Offline 界面，4 帧均有 31,262 个非黑像素 | `ready=true` |

有卡会话附加 64 MiB FAT32/MBR 原始镜像，其中包含一段合成音频 `TEST.MP3`。会话保存的介质 SHA-256 为 `47094ec1b39cce2361056c4a4bf120039668e0c4bff6fe49e89ad152a9b37704`，等于上传的夹具哈希。会话可读取模型状态，来宾挂载或读取该文件仍无可用证据。目标两份证据包均未包含扬声器 PCM。

单独的隔离诊断会话使用同一目标 Flash，在屏幕采样前通过 QMP 发出只读的 `info registers -a`。首份样本的 CPU0 PC 为 `0x4038536d`，CPU1 PC 为 `0x40378f6e`，两个核心的 VECBASE 均为 `0x40374000`。从同一发布镜像读取的 app0 IRAM 段覆盖 `[0x40374000, 0x40379044)` 和 `[0x40379044, 0x403854e0)`，因此实测 PC 已落在应用映像中。诊断会话自身也复现 225 字节串口和全黑画面。[逐次采样、证据包和寄存器采样摘要](evidence/execution-summary.redacted.json)

### 第二套运行时与面板数据面

第二套原生 QEMU 二进制 SHA-256 为 `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e`。两套运行时使用相同 ROM，SHA-256 为 `b5c7090cc22efce51c1323cef31ca96fcd673a5b1d1b1017e219d393f2659913`。第二套运行时下，目标和参考都附加第一份含合成 MP3 的 FAT32/MBR 镜像。18 秒采样时目标仍为 225 字节串口及全黑帧，参考已有非黑界面并通过就绪判定。

使用主运行时另开两次面板跟踪会话，目标和参考均附加同一份已校验的 64 MiB FAT32/MBR 夹具，SHA-256 为 `6e7c003e532f2912b5a6841ea24b6ffbe1ca113caf0dd83b26d750d0cbd7f4a0`。目标只发送面板 ID 读取命令 `0x04`，15 秒采样窗口内未观察到面板初始化、像素写入 `0x2c` 或 SPI SD 命令。参考会话观察到退出休眠 `0x11`、开启显示 `0x29`、设定窗口 `0x2a/0x2b` 以及显存写入 `0x2c`，实际画面通过就绪判定。两份面板跟踪会话均没有 SPI SD 命令，因此对照仅用于显示路径。默认板级模型下的目标流程没有到达可观察的 SD 访问。[面板命令和采样摘要](evidence/execution-summary.redacted.json)

### 应用任务的 I2C1 自锁

精确发布镜像包含 Arduino-ESP32 3.3.12 和 ESP-IDF v5.5.5。使用隔离 Device Service 会话，在每次 QEMU 屏幕采样前通过 QMP 只读采集 `loopTask` 的任务控制块、栈和 I2C1 mutex。三个诊断会话保留了相同的栈特征，最后一次还读取了锁的持有者和等待参数。[Arduino-ESP32 3.3.12 发布版本](https://github.com/espressif/arduino-esp32/releases/tag/3.3.12)

面板 ID 读取完成后，M5GFX 探测 GPIO5/6 和 GPIO8/9。GPIO5、GPIO6 均读高时会先临时用这两个引脚探测 VAMeter 的 I2C1。栈中 `0x42006f46` 和后续调用证明目标走到了这次临时切换的恢复路径。公开 M5GFX 源码对应同一探测结构，BIN 内的执行位置通过反汇编和来宾栈核对。[M5GFX 板型探测](https://github.com/m5stack/M5GFX/blob/d91077b9/src/M5GFX.cpp#L2563-L2624)

恢复时传给 `i2cInit` 的 SDA 和 SCL 都为 GPIO0。外层 `i2cInit` 已持有普通、非递归的 I2C1 mutex。先注册 GPIO0 为 SDA，再注册同一 GPIO 为 SCL，触发前一个用途的卸载回调 `i2cDetachBus`。该回调通过 `i2cDeinit` 再次获取同一把锁。来宾栈从 `perimanSetPinBus` 的 SCL 调用一路落到 `xQueueSemaphoreTake`，等待参数为 `0xffffffff`（`portMAX_DELAY`）。[固定版本的 Arduino I2C HAL](https://github.com/espressif/arduino-esp32/blob/94afccf35fb1e401facddbcf9e13bcf7c76a31d8/cores/esp32/esp32-hal-i2c-ng.c#L73-L177) · [引脚管理回调](https://github.com/espressif/arduino-esp32/blob/94afccf35fb1e401facddbcf9e13bcf7c76a31d8/cores/esp32/esp32-hal-periman.c#L166-L184)

读取到 `loopTask` 的 TCB 为 `0x3fcefa98`，I2C1 mutex 为 `0x3fcec7b4`。该 mutex 的持有者字段也是 `0x3fcefa98`，栈帧中的等待参数指向同一 mutex。这确认了自锁是目标镜像无法继续初始化画面的直接原因。提取 BIN 的 app0 并用 Xtensa 反汇编器查看 IROM 段时，段基址为 `0x42000020`，`i2cInit` 和 `i2cDeinit` 的入口分别为 `0x42038558` 和 `0x420382ec`。[来宾栈和内存摘要](evidence/execution-summary.redacted.json)

### 仿真板型识别的触发条件

Cardputer ADV 主板原理图把 GPIO5/6 引到扩展接口，内部 I2C 的上拉在 GPIO8/9。已测的第二套 QEMU 源码则默认将两个外接 Cap 模型 CC1101 和 ST25R3916 分别挂在 GPIO5/6。GP-SPI 注册从设备时将片选引脚标记为外部高电平，会影响 M5GFX 将这些 GPIO 配为输入下拉时的读值。GPIO 模型的默认高电平近似也是需要单独区分的因素。该源码差异解释了 QEMU 中为何进入 VAMeter 探测分支。受控对照验证了外接模块默认挂载与目标黑屏之间的因果关系。[Cardputer ADV 官方原理图](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1178/Sch_M5CardputerAdv_v1.0_2025_06_20_17_19_58.pdf) · [QEMU 板级挂载](https://github.com/m5agent/m5stack-esp-emulator/blob/dd2eb35d2e6a909992268089ddc37e27970d4a92/patches/qemu-unit-runtime/0001-reconstructed-xtensa-source.patch#L7941-L7944) · [QEMU 片选输入](https://github.com/m5agent/m5stack-esp-emulator/blob/dd2eb35d2e6a909992268089ddc37e27970d4a92/patches/qemu-unit-runtime/0001-reconstructed-xtensa-source.patch#L1775-L1790)

### 同固件的仿真板级对照

以第二套 QEMU 为基线，只删除 Cardputer ADV 板级文件中的四个 CC1101、ST25R3916 挂载调用，重新编译该板文件并链接，其余编译输入保持一致。基线二进制 SHA-256 为 `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e`，诊断二进制为 `167aaabc6513e0b9703e3ad7512020be52f0136aff1039c531dfb5bf64160702`。固件、8 MiB Flash、ROM 和有卡对照的 FAT32/MBR 镜像完全一致。去掉的四行及对象哈希见脱敏证据。[构建差分和逐次采样](evidence/execution-summary.redacted.json)

| 同一 MP3 固件 | 5、12、20 秒的画面 | 就绪判定 |
| --- | --- | --- |
| 默认模型，附加已校验 microSD | 全黑，0 非黑像素，串口一直 225 字节 | `ready_timeout` |
| 诊断模型，附加相同 microSD | `Cardputer MP3` / `No microSD card` / `Insert a FAT32 card with MP3s` | 画面就绪 |
| 诊断模型，无附加 microSD | 相同无卡画面，帧 SHA-256 一致 | 画面就绪 |

两次诊断模型在每个采样点的 240×135 PNG 都有 32,400 个非黑像素、1,039 字节，SHA-256 为 `90ba9ab23f53fdf5c423707a2f0f5408751b83e942f31dc013781ea5adab0663`。面板记录中出现 `0x11`、`0x29` 和 `0x2c`，与固件已进入应用的画面一致。诊断构建仅用于因果验证。

诊断模型在附加已校验 SD 的情况下仍报 `f_mount failed: (3)`（`FR_NOT_READY`）。SPI 数据面先见 `CMD0` 返回 `0x01`，随后空闲状态中的 `CMD59` 返回 `0x00`。Arduino-ESP32 3.3.12 在此步骤接受 `0x01` 或 `0x05`。采样中没有后续 `CMD8` 或 `CMD17`。因此显示启动恢复后，仍有独立的 SPI SD 初始化响应不匹配。测试输入的一次回车被服务接收，文件枚举和播放均未出现。[Arduino SD 驱动](https://github.com/espressif/arduino-esp32/blob/94afccf35fb1e401facddbcf9e13bcf7c76a31d8/libraries/SD/src/sd_diskio.cpp)

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| 源镜像身份与虚拟 Flash | PASS | 公开镜像哈希匹配。目标使用验证通过的会话独立 8 MiB Flash。 |
| 基线 ROM 读取及跳转 | PASS | 串口从 SPI Flash 启动并跳至二级 bootloader 入口。 |
| 基线应用就绪 | FAIL | 观测窗口内没有应用就绪帧，保持全黑。 |
| 无卡与有卡应用就绪 | FAIL | 各运行 65 秒并记录 4 个全黑帧。介质附加已确认，来宾挂载未证实。 |
| 同板参考固件 | PASS | 相同 Device Service 和 QEMU profile 的 UIFlow2 在 5 秒采样时已有可识别画面。 |
| 目标 app0 指令执行 | PASS | 独立诊断中的双核 PC 均落在同一镜像的 app0 IRAM 内。 |
| 第二套原生运行时 | PARTIAL | 目标持续黑屏，参考通过就绪判定。 |
| 目标面板及 SD 数据面 | PARTIAL | 观察到 ID 读取，未观察到像素写入或 SPI SD 命令。 |
| 直接阻塞原因 | PASS | 来宾内存和栈确认 I2C1 的同一任务持锁并再次等待同一 mutex。 |
| 仿真板级触发条件 | PASS | 同固件、ROM 和 SD，仅移除四处仿真 Cap 挂载即出现界面。 |
| 诊断模型 SD 挂载 | FAIL | 已附加有效夹具，`CMD59` 响应不匹配，来宾报 `FR_NOT_READY`。 |
| MP3 选择、解码和播放 | NOT RUN | 诊断模型显示界面，SD 挂载失败，未到达文件选择或播放。 |
| Cardputer ADV 真机 | NOT RUN | 测试中心没有匹配的真机夹具。 |

## 验证边界

这是 virtual-device validation。实物的 SD、电气和声学行为需在匹配真机上独立验证。公开证据使用实验名称和摘要，服务会话标识、内部运行信息及原始包仅保存在本地。

## 风险与回滚

复跑使用会话独立的 Flash 与 microSD。归档所列十四个会话均在请求证据包后停止。本轮共二十个自有会话回读为 `stopped`，历史保留，可写 Flash 已释放，无剩余来宾进程。四个自有服务实例均已停止。
