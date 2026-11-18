# Tab5 UserDemo ES8388 控制器层归因

## 观察目标与身份

上一次 UserDemo 重建复验定位到 `bsp_audio_codec_speaker_init` 断言。为区分控制句柄创建失败、I²C 传输失败和 codec 寄存器事务不兼容，本次对相同重建镜像做两组同路径对照，并用未改动发布版复验移除 GT911 Part 后的启动边界。三组均经隔离 Device Service 1.90.0 与 esp-emu 1.1.0 启动。运行时、两个镜像、匹配 ELF 与会话证据包的精确 SHA-256 见[验证摘要](evidence/userdemo-codec-routing.summary.json)。 [Device Service 源码](https://github.com/m5agent/m5stack-esp-emulator/commit/57d397462e661e608e7c3ae2a878e80527d08e84) · [官方 UserDemo 源码](https://github.com/m5stack/M5Tab5-UserDemo/tree/68b19d37fbf9cefd5f256992f5dca34794c62ab4)

## 执行与结果

两组都将同一个 SDK 重建镜像上传并导入 Tab5，使用相同 ROM、C6 固件与 GT911/ILI9881C 板型。只在诊断运行参数中配置原生寄存器设备 `--i2c-dev 0:0x10,width=1,fill=0` 及 `0:0x40,width=1,fill=0`。两组唯一的板模型差异是加载或省略已准入的 GT911 Part。

通过匹配 ELF 的硬件断点，读取 BSP 控制接口构造返回、真实 HP I²C 主机设备参数、每次 `i2c_master_transmit` 的数据与状态，以及 ES8388 构造返回值。两组都成功创建控制接口。总线是 HP I²C0，GPIO32/31，100 kHz，7 位地址 `0x10`。首次事务为寄存器 `0x19` 写入 `0x04`，其后全部事务 payload 摘要也一致。

| 重建对照 | 真实总线结果 | 构造 |
| --- | --- | --- |
| 启用 GT911 Part | 32/32 NACK。驱动状态 `ACK_ERROR`，事件 `NACK`，返回 `0x103` | 空句柄 |
| 省略 Part，保留相同寄存器设备 | 32/32 完成。驱动状态与事件均为 `DONE`，返回 `0` | 有效句柄 |

原生后端日志明确报告 Part 接管整个 HP I²C0，两个独立设备不会被查询。这与实际事务分歧一致，可将该断言归因到当前配置的总线寻址路径。带 Part 的重建组无完整帧，无 Part 的重建组产生完整帧。额外用未经修改的发布版运行无 Part 诊断组，无 GDB。取到 11 个完整的均匀底色帧，并在后续触控初始化记录 `ESP_ERR_INVALID_STATE`。此对照给出了后续阻塞点。

## 证据边界

最初暂停在复位向量的 GDB 方法遇到较早的非法指令，未进入 codec 路径。实测对照采用正常启动后提前连接的只读诊断。每组保留停止前 ZIP，核对 CRC、清单和串口摘要，以 `purge=0` 停止，核验来宾及服务退出、租约归零。公开证据省略宿主路径、端点和原始会话标识。

独立寄存器设备仅用于确认事务路径。此次归档的默认 I²S0 输出文件仅保留了 44 个全零字节，后端确认没有采到样本。该诊断没有验证声音播放、触控就绪、实体硬件或浏览器，也没有修改产品源码或准入配置。
