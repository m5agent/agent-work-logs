# ESP-EMU 1.1.0 与项目适配评估

## 当前使用情况

2026-11-18 核对上游，`main` 与 v1.1.0 同为 `34ba27a6e5a3da41743fc861b462cf2452f0ca28`。项目基线为 `174c6d42048bf12f315e8b572948f17638d0bb77`。项目已经按固件和板型限定使用 1.1.0 的 P4 DSI 与 ESP Parts。原版 Arduventure 与 CarPlay 的无 ELF 取帧及指定触控动作有既有验证。官方 Tab5 UIFlow2 v2.5.4 已到 I²C 初始化，两套 Part 均在 8,205 字节消息处退出，Python、可用画面和触控仍待验证。[正式发行](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0) · [既有原版触控证据](https://github.com/m5agent/m5stack-esp-emulator/blob/174c6d42048bf12f315e8b572948f17638d0bb77/docs/evidence/2026-11-17-tab5-st7123-touch/README.md) · [#188 既有对照](https://github.com/m5agent/m5stack-esp-emulator/blob/174c6d42048bf12f315e8b572948f17638d0bb77/docs/evidence/2026-11-18-tab5-stock-frame-comparison/uiflow254-v110-summary.json)

## 本轮虚拟设备验证

取 ESP-IDF v5.5.4（`735507283d5b2f9fb363a1901172dbd9e847945d`）的原版 SDMMC 示例源码，只在独立构建配置选择 rev3 P4。三个独立进程使用同一固件和 rev300 ROM，来宾默认 SDMMC slot 1，使用项目生成的 32 MiB FAT16 副本。使用限制网络模式，且不启动 C6 或对端。证据由来宾 UART、宿主 FAT16 目录项与数据区、镜像哈希共同构成。[ESP-IDF 示例](https://github.com/espressif/esp-idf/tree/v5.5.4/examples/storage/sd_card/sdmmc) · [SD 卡参数](https://github.com/espressif/esp-emulator/blob/v1.1.0/docs/guides/CLI.md#sd-card) · [项目镜像生成器](https://github.com/m5agent/m5stack-esp-emulator/blob/174c6d42048bf12f315e8b572948f17638d0bb77/platform/tools/sd_image.py)

| 输入 | 观测 |
| --- | --- |
| `--sd card.img,slot=1` | FAT 挂载，写入、改名、两次读回及卸载。宿主读取 `FOO.TXT` 和 `NIHAO.TXT`，内容和 UART 一致。 |
| 空槽 | UART 显示 `ESP_ERR_TIMEOUT`，无文件系统挂载。 |
| `--sd card.img,ro,slot=1`，使用可写组产物的副本 | FAT 挂载。底层块写报 `0x107`，改名失败且进程到达超时边界。例程仍打印一条 `File written`，应以失败的块写及镜像 SHA 为准。只读组输出与输入全文件相同。 |

宿主 FAT 检查通过。三个进程返回且私有 Flash 输入 SHA 相同，原始 FAT 镜像保持不变。第一次宿主格式化工具拒绝普通文件，改用项目内置 FAT16 生成器。第一次 CLI 尝试因重复 `--exit-on` 被拒，在来宾启动前退出。上表使用独立的单标记运行记录。[证据摘要](evidence/sdmmc-summary.json)

## 复现

从 [官方发行包](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0) 取对应宿主架构的运行时。准备独立目录及 SHA 匹配的 P4 rev300 ROM。激活 ESP-IDF v5.5.4 环境，在该目录中运行以下命令。生成器取自上述项目提交。构建时间会影响自行重建的 Flash SHA。

```sh
cp -R "$IDF_PATH/examples/storage/sd_card/sdmmc" example
printf '\nCONFIG_ESP32P4_SELECTS_REV_LESS_V3=n\n' >> example/sdkconfig.defaults
IDF_TARGET=esp32p4 IDF_CCACHE_ENABLE=0 idf.py -C example -B build build
IDF_TARGET=esp32p4 IDF_CCACHE_ENABLE=0 idf.py -C example -B build merge-bin
python3 -c 'from pathlib import Path; from sd_image import create_fat16_image; create_fat16_image(Path("base.img"), label="SDPROBE")'
cp base.img card.img
"$ESP_EMU" --chip esp32p4 --firmware build/merged-binary.bin --rom "$P4_ROM" \
  --console uart0 --net user,restrict=yes --timeout 12s \
  --exit-on 'Card unmounted' --sd card.img,slot=1
```

空槽对照省去 `--sd`，退出标记改为 `Failed to initialize the card`。只读对照使用写入组卡镜像的副本、`--sd card-ro.img,ro,slot=1`、`--exit-on 'Failed to open file for writing'`，并用 12 秒运行时上限收回进程。对比 UART 及镜像的整文件 SHA，另从 FAT16 根目录文件项读取首簇和文件长度检查载荷。

## 应用范围

现有 Device Service SD 准入和私有镜像逻辑只进入 QEMU 后端。Tab5 的板支持包使用 SDMMC slot 0，而现有 P4/C6 的 ESP-Hosted 需要保留 slot 1。接入候选应绑定版本和 Tab5 路径，在同一原版固件会话验证文件读写、复位重挂载、宿主镜像回读和 C6 共存。该板级验证为 `NOT RUN`，项目与常驻服务维持现有配置。移除、UHS、eMMC 和浏览器 SD 属于发行说明列出的边界。[当前服务准入](https://github.com/m5agent/m5stack-esp-emulator/blob/174c6d42048bf12f315e8b572948f17638d0bb77/platform/tools/device_service.py#L11963-L11988) · [Tab5 板级源码](https://github.com/m5stack/M5Tab5-UserDemo/blob/fe8aa051beb9385468f7e46b909e764169df3f7a/platforms/tab5/components/m5stack_tab5/m5stack_tab5.c#L558-L630)
