# Cardputer ADV 裸板接线与 SPI SD 修复报告

## 原因与修复

原复核保留了两个独立故障。默认虚拟裸板安装了选配 Cap 的 CC1101 与 ST25R3916，并把片选 GPIO5/6 标为外部驱动高。固件的 M5GFX 板型探测因此进入 VAMeter 分支，恢复 I²C1 时重入已经持有的锁。去除该虚拟外设后，来宾可以绘制画面，却因空闲状态下的 CMD59 错误返回值无法挂载卡。[原始虚拟设备复核](https://github.com/m5agent/agent-work-logs/blob/0a4969c549561efcf5423a592ca567a86d838e0b/records/firmware-review-service/2026-11-09-cardputer-adv-mp3-startup/report.md)

- 板级补丁 `0165-cardputer-adv-explicit-caps.patch` 将两个芯片绑定到显式的 Cap CC1101 配置，保留它们通过实际 GP-SPI 控制器访问的路径。片选登记只观察来宾 GPIO，取消由从设备主动驱动高电平，允许来宾的内部下拉参与 pad 电平解析。内部 I²C 的 GPIO8/9 维持板载连接。[Cardputer ADV 原理图](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1178/Sch_M5CardputerAdv_v1.0_2025_06_20_17_19_58.pdf)
- SD 补丁 `0166-spi-sd-card-init-state.patch` 使空槽的 MISO 保持未驱动的读值 `0xff`。有介质时，CMD0 进入空闲，CMD59 返回当前状态，CMD58 根据卡状态返回 OCR，CMD55 前缀启用 ACMD41 和 ACMD42。启用 CRC 后检查命令和写块 CRC，并按 SD 线序发送读块 CRC。保留现有的 SDSC 字节地址、512 字节扇区与多块读写入口。[SD Association 简化规范](https://www.sdcard.org/downloads/pls/) · [Arduino-ESP32 3.3.12 驱动](https://github.com/espressif/arduino-esp32/blob/94afccf35fb1e401facddbcf9e13bcf7c76a31d8/libraries/SD/src/sd_diskio.cpp#L517-L635)

## 可复现环境

| 项目 | 身份 |
| --- | --- |
| ESP Emulator 基线 | `80d1879a014a55bc598fbc1474445c1f6773ff34` |
| 交付源码 | `340d80cf2e54bbe867f5dbade422ac0907251607（独立本地分支）` |
| QEMU 基线 | Espressif QEMU `40edccac415693c5130f91c01d84176ae6008566` |
| 原生 QEMU | `d150c645291e66202d73eb6bdc98900980c2dcb4e851b41d9386dfa6a1ae4b7d` |
| ESP32-S3 ROM | `b5c7090cc22efce51c1323cef31ca96fcd673a5b1d1b1017e219d393f2659913` |
| MP3 Player 发布文件 | 885,600 字节，SHA-256 `c5918ff914a51b0dc4398f331c8306c25e26a4b157592d3e7d9c0dff2d0c5e45` |
| 8 MiB 来宾 Flash | SHA-256 `10d42a08a69d3e1f628fd9078015a64b598a74f02437c26ecc7201cc2db3e78d` |
| 64 MiB FAT32/MBR SD 镜像 | SHA-256 `6e7c003e532f2912b5a6841ea24b6ffbe1ca113caf0dd83b26d750d0cbd7f4a0` |
| 根目录合成 `TEST.MP3` | 36,362 字节，SHA-256 `30ffce5202e6926566a920c2b236ac74c6077752642b34b85193f67931ae8fc4`，解码测得约 524 Hz |

原生构建按 `scripts/bootstrap-unit-runtime.py` 的固定补丁顺序。使用独立 Device Service 实例上传同一发布 BIN，创建 `device_id=cardputer-adv`、`runtime=qemu` 会话。默认裸板省略 Cap 配置。无卡会话省略 `storage`，有卡会话用 `storage.sd_image_artifact_id` 挂载验证过的 FAT32/MBR 镜像。采集屏幕帧、串口、SPI SD trace 和虚拟音频。选择曲目时通过会话 input API 发送 Enter。结束前请求证据包，停止时保留历史并释放可写 Flash。[固件发布](https://github.com/TurbulentGoat/cardputer-adv-mp3-player/releases/tag/v1.0.0)

原生矩阵通过仓库内用例执行。设置 `M5_QEMU_XTENSA` 和 `M5_QEMU_XTENSA_ROM_DIR` 指向本次构建的二进制与 ROM 目录，然后运行下面命令。NFC 和 CC1101 的 checked-in case 显式选择 Cap。裸板负对照使用同一来宾镜像并省略 Cap 挂载配置。

```sh
PYTHONPATH=.work/py python3 tests/uiflow2/run_peripheral_matrix.py \
  --case cardputer-adv-sd --case cores3-sd --case papercolor-sd \
  --out-dir sd-results
PYTHONPATH=.work/py python3 tests/uiflow2/run_peripheral_matrix.py \
  --case cardputer-adv-nfc --case cardputer-adv-cc1101 \
  --case cardputer-adv-keyboard --case cardputer-adv-audio \
  --out-dir topology-results
```

## 原生虚拟设备验证

| 执行 | 状态 | 独立观察 |
| --- | --- | --- |
| 默认裸板、无卡 | PASS | `Cardputer MP3` 从挂载提示进入 `No microSD card`。 |
| 有卡首轮观察 | FAIL | 自动 OCR 将界面识别成 `LIBRART` 和 `TESTIMPз`。SPI 已读取 MBR、FAT 和根目录。未达到脚本输入门槛，未发送回车。 |
| 有卡、播放复验 | PASS | 与首轮 OCR 失败时相同哈希的库画面经独立目视确认为 `TEST.MP3`。发送 Enter 后重绘播放画面、读取曲目扇区并输出匹配的 PCM。 |
| 三板 SPI SD 回归 | PASS | Cardputer ADV、CoreS3、PaperColor 共 3/3 用例和 12/12 检查，含初始化、写入、来宾读回和画面标记。宿主直接读取三份原始镜像的第 100 扇区均匹配独立生成的 512 字节序列。 |
| 裸板与选装 Cap 回归 | PASS | 使用同一整合原生运行时。裸板键盘、音频，显式 Cap NFC 和 CC1101 共 4/4 用例及 15/15 检查。 |
| Cap 缺席负对照 | PASS | 沿用同一整合原生运行时及两份 Cap 试验来宾镜像，移除 Cap 环境参数后，裸板配置正确显示预期失败。NFC 显示 `chip begin failed 00`，CC1101 显示 `tx failed`。 |

播放会话使用同一个虚拟来宾收集输入前后证据。输入前无扬声器 PCM，SPI 共 22 条初始化和文件系统访问命令。输入后，曲目数据读取包含 LBA 4067 到 4098 及末尾 LBA 4137 和 4138，累计 SPI 命令 103 条。截图显示播放界面，进度从 `0:00` 变为 `0:01`。扬声器虚拟捕获包含 108,032 字节，按单声道 48 kHz 解释时约 524 Hz 分量在 11 个分析窗口匹配合成源，最高频率能量占比为 0.9835。其结果覆盖虚拟文件读取、解码与 I²S 数字输出。[帧、SPI 和 PCM 脱敏摘要](evidence/execution-summary.redacted.json)

三次实际 Device Service 会话均先导出证据，再停止并回读历史，保留最后一帧、释放可写 Flash。原始压缩包及唯一会话标识留在本地。原生 Device Service 和三板 SD、板级拓扑回归使用同一 QEMU 二进制，各自保留执行边界。

## 浏览器与发布范围

本地隔离导出以 77 层源码构建 WASM，SHA-256 `684ee05cb3f136ca3b214706006d96faa4685c45149973a342b3e536a0cdc55a`。相同原版合并镜像从页面上传后，在 240×135 画布显示 `Cardputer MP3 / No microSD card`。普通 Stop 以退出码 0 完成，先于页面关闭释放 iframe 和六个已观测 Worker。独立 UIFlow2 键盘回归在同一 WASM 上通过 69 项断言，覆盖 11 键真实按下及释放。浏览器挂卡与播放为 `NOT RUN`，实测使用本地导出，站点发布未执行。[浏览器证据](evidence/browser-summary.redacted.json)

平台套件运行 2,041 项，2,033 通过、8 跳过。浏览器契约、目录、QEMU profile、项目快照及 PR 范围检查通过。

归档的两份 [QEMU 补丁](patches/) 与源码提交字节一致。按基线的原生顺序重放至最后一层，再依次应用 0165 和 0166。两层均通过正向检查与反向检查，独立回放与最终编译树的文件哈希一致。

## 边界与回滚

结果为 virtual-device validation。真机、无线射频、物理 SD 电气时序、声学和音质为 `NOT RUN`。复验只覆盖记录的固件、板型、卡和音频路径。可撤回交付的板级与 SD 补丁及构建清单改动，再由固定基线重新构建。虚拟 Flash 与 SD 写入都限定于本轮会话的独立副本。
