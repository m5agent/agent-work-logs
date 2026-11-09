# EMBER 2.1 独立应用镜像虚拟审核复验

## 旧失败与实际输入

原审核保存的 1,187,056 字节 BIN 的 SHA-256 为 `f4261dbbabdaac5825838455ac553cc21ef9c5c6d308cb2c82941bd8ccc1cb5e`。偏移 `0x20` 为应用描述符，IDF 标识为 `v4.4.7-dirty`。旧审核把该应用置于 Flash 偏移 0，在 `0x8000` 得到无效分区项魔数 `0x0000` 而停止。诊断位于分区表错误列表，顶层为空，原页面仅显示错误标题。旧尝试没有创建固件来宾。原 BIN 的 Git blob SHA-1 为 `52d6f183f52a899b5b5fd22848cc832a368b9351`，与上游公开文件一致。[公开发布 BIN](https://github.com/HorseyofCoursey/EMBER/blob/d34949441e77430239a27248bbbcc47601558431/ember-cardputer-adv.bin)

## 厂商配方

上游配置声明 Espressif32 平台 6.7.0、ESP32-S3、DIO、80 MHz、8 MiB 和 `default_8MB.csv`。原 BIN 内嵌 `framework-arduinoespressif32@3.20016.0`。使用 Arduino 2.0.16 的 `bootloader_dio_80m.elf`、`gen_esp32part.py` 及 `boot_app0.bin`，以 esptool 4.5.1 重建启动段。两个 OTA 槽各为 `0x330000`。[EMBER 构建配置](https://github.com/HorseyofCoursey/EMBER/blob/d34949441e77430239a27248bbbcc47601558431/platformio.ini) · [PlatformIO 6.7.0 配方](https://github.com/platformio/platform-espressif32/blob/v6.7.0/platform.json) · [Arduino 构建规则](https://github.com/espressif/arduino-esp32/blob/54927338eb6ae00a67aba53b7f44747cf2dfd0d2/tools/platformio-build.py) · [分区定义](https://github.com/espressif/arduino-esp32/blob/54927338eb6ae00a67aba53b7f44747cf2dfd0d2/tools/partitions/default_8MB.csv)

按 `0x0000 / 0x8000 / 0xE000 / 0x10000` 放置引导、分区表、OTA 选择区和原应用，未写范围填充 `0xff`。校验分区 MD5、Flash 容量和应用图像均通过，OTA0 应用字节保持完整，另一槽为空。UIFlow2 参考镜像包含不同的 NVS、PHY、factory、sys 和 vfs 布局，本轮使用厂商 Arduino 配方中的 OTA、SPIFFS 与 coredump 布局。[逐段证据](evidence/execution-summary.redacted.json)

公开源码配置启用 USB CDC。程序在 SD 初始化失败时绘制 `SD init FAILED`，所以验证应分别记录启动、读卡和实际应用行为。[EMBER 启动路径](https://github.com/HorseyofCoursey/EMBER/blob/d34949441e77430239a27248bbbcc47601558431/src/main.cpp#L3052-L3139)

将原应用另存为 `application.bin`。以下命令重新生成的引导、分区表和整盘文件均与记录的 SHA-256 一致。

```sh
uv run --no-project --with 'esptool==4.5.1' python -m esptool --chip esp32s3 \
  elf2image --flash_mode dio --flash_freq 80m --flash_size 8MB \
  -o bootloader.bin bootloader_dio_80m.elf
python3 gen_esp32part.py -q --flash-size 8MB default_8MB.csv partitions.bin
uv run --no-project --with 'esptool==4.5.1' python -m esptool --chip esp32s3 \
  merge_bin --fill-flash-size 8MB -o composed.bin \
  0x0000 bootloader.bin 0x8000 partitions.bin 0xe000 boot_app0.bin 0x10000 application.bin
shasum -a 256 application.bin composed.bin
```

## 审核改动与实测

审核器先识别 ESP 应用描述符，并按原 BIN 的 SHA-256 选择已验证的启动上下文。它验证芯片、Flash 容量、分区边界和可选中的应用槽，再向 Device Service 分段提交、静态检查和虚拟烧录。原来已合并的镜像继续使用原入口。缺少兼容启动资料时转人工复核。上线检查读取了旧任务的完整分区错误，原 `E_STATIC` 结果仍有记录。审核服务本地部署后的 42 项 Python 3.9 测试及页面 JavaScript 语法检查均通过。

用已保存描述和原哈希 BIN 执行常驻服务 dry-run。结果为 `done / SIM_VERIFIED / NOT SUBMITTED`。执行使用 Device Service 的原生 QEMU 配置 `cardputer-adv`，QEMU SHA-256 为 `d150c645291e66202d73eb6bdc98900980c2dcb4e851b41d9386dfa6a1ae4b7d`。证据 ZIP 读取的虚拟 Flash 在 `0x10000` 的应用字节与原 BIN 完全相同，逐段回读哈希也与启动段清单一致。串口记录 `rst:0x1 (POWERON),boot:0x4 (SPI_FLASH_BOOT)` 和 `entry 0x403c98b8`。取证后停止会话，保留画面，释放可写 Flash。[运行证据](evidence/execution-summary.redacted.json)

会话挂载 64 MiB 的隔离 FAT SD 镜像。应用曲库显示 `TEST.MP3`。发送 Enter 后画面进入播放态，扬声器 PCM 从 0 增至 52,224 字节。将原测试曲目解码得到约 524 Hz 参考音，采集的单声道 44.1 kHz PCM 有 4 个分析窗匹配，峰值频谱能量占比为 0.978。这一结果支持本次读卡及播放路径。PCM 峰值为 210，低于通用幅值阈值 400。

## 范围与回滚

这是 `virtual-device validation`。任务及会话标识、运行路径和其他本机细节留在本地，归档保留身份哈希和可复查观察。实物硬件、物理声学和浏览器路径均为 `NOT RUN`。如需回滚，可恢复前一审核服务版本和配方配置，保留原有审核历史。
