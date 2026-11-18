# Tab5 UserDemo V0.4 源码 A/B

## 输入与对照

原版发布 BIN 的嵌入版本是 `V0.3-1-g4b57c62`，对应提交
`4b57c62a2aef99f6f68902c045c34fea467e21a7`，其 Git 树与 V0.4 发布标签提交
`68b19d37fbf9cefd5f256992f5dca34794c62ab4` 相同。重建使用发布标签、发布
`sdkconfig` 与 `dependencies.lock`、ESP-IDF v5.4.2 和
`riscv32-esp-elf esp-14.2.0_20241119`。
[发布源码](https://github.com/m5stack/M5Tab5-UserDemo/tree/68b19d37fbf9cefd5f256992f5dca34794c62ab4)

重建候选应用在同一 SDK 基线上加入 Espressif 后续移除 WFI 暂停状态等待的
改动。两次构建固定 `ESP_IDF_VERSION=5.4`、`SOURCE_DATE_EPOCH=1780467004`
及 SDK 显示版本，保持编译配置、bootloader 和分区表字节一致。
在仓库根目录用 `python3 fetch_repos.py` 获取发布声明依赖，随后执行
`idf.py -C platforms/tab5 -B BUILD reconfigure`、`ninja -C BUILD`，
并在构建目录用
`python -m esptool --chip esp32p4 merge_bin -o IMAGE --fill-flash-size 16MB @flash_args`。
应用改动内容、配置和两个固件哈希见执行摘要。
[Espressif 上游变更](https://github.com/espressif/esp-idf/commit/d59b797d449c5b4010889cdb7fd91ae8c996502f)

## 执行结果

通过独立 Device Service 上传并导入各固件，创建原生 Tab5 会话。
原版及两份重建的普通会话均观察约 65 秒。每例使用同一 1.1.0 后端、板型、
ROM、eFuse、hosted C6 固件和 GT911 Part。没有上传 ELF 或改变来宾内存。
在单独的诊断会话里，用相应构建 ELF 在本地符号化程序计数器和调用栈。

| 固件 | 普通会话 | 完整帧 |
| --- | --- | --- |
| 发布 BIN | 1 次 ROM 启动，无复位 | 0 |
| 重建原 SDK | 1 次 ROM 启动，无复位 | 0 |
| 重建上游 WFI 改动 | 85 次 ROM 启动，84 次软件复位 | 0 |

重建基线在 `bsp_audio_codec_speaker_init` 触发条件 `es8388_dev` 的断言。
CPU0 位于 `panic_handler` 后的 `esp_cpu_stall`，执行等待状态位的回跳。
CPU1 位于 `esp_cpu_wait_for_intr` 的 WFI 后。PMU 暂停请求读回为
`0x00860000`，暂停确认状态为零。加入上游变更的构建再次命中同一断言。
原版另试原生 HP I²C0 的 `0x10`、`0x40` 通用寄存器文件。后端报告
该总线被 co-sim Part 接管，两份通用寄存器文件未被调用。该会话没有完整帧，
I²S 捕获只留下 44 字节占位文件。

## 边界与清理

该结果把重建固件的 ES8388 初始化断言与后续 panic 等待关联。原版缺少匹配
ELF，实际 I²C 初始化失败交易仍待核对。通用寄存器文件只用于控制器诊断。
两份诊断构建未用于用户服务或发布应用。六个独立会话先验证证据 ZIP、
清单和镜像哈希，再释放租约、Flash 与自有进程。未执行 Burner、实体硬件、
浏览器和用户交互。
[有界会话摘要](evidence/userdemo-wfi-source-ab-summary.json)
