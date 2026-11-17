# Cardputer-ADV 16 MB flash 契约镜像的 intake 校验缺口

- 日期：`2026-11-17`
- 结果：`PARTIAL`
- 工作类型：`firmware_review_attribution`
- 问题来源：模拟器固件审查任务 `job-080c2a4eacc1`（lane=`SIM_PARTIAL`、status=`manual_review`、error_code=`E_NO_FRAME`）；新开 issue
  [#234](https://github.com/m5agent/m5stack-esp-emulator/issues/234)
- 源码版本：`m5agent/m5stack-esp-emulator @ 6da7ab20`；运行服务快照 `fd08569f`
- 环境：macOS arm64；Device Service 原生 QEMU（ESP32-S3 / `cardputer-adv`）；审查任务证据只读归因；未使用真机

## 结论

固件 `ShellMicroPythonShell_CN_v1.0.0_FACTORY_0x0.bin` 是按 **16 MB flash** 构建的
（bootloader/app 头部 `flash_size_code=4`，分区表 `vfs` 结束于 `0x1000000`），而
Cardputer-ADV（K132-Adv，ESP32-S3FN8）只有 8 MB flash。QEMU 的 8 MB 模型按实际容量
报告，固件在 `esp_flash` probe 失败后落到 MicroPython REPL，60 s 观察窗口内没有 UI 帧。

因此**这次启动失败不是 QEMU 模型缺陷**，而是固件与目标机型的 flash 契约不匹配：
同一 BIN 在 8 MB 真机上走相同 IDF 路径也会在此处失败。

不过 Device Service 在本应拒绝的位置放行了：merged 合成后用
`parse_partition_table(..., image_size=spec.flash_size)` 已得到
`partition vfs exceeds flash size`，但代码没有对 invalid 分区表报错，镜像仍被接受、
烧入 8 MB 虚拟 flash 并分配会话，最后以 `E_NO_FRAME` / `manual_review` 收口，
`failure_attribution` 为空。该 intake 校验缺口已开
[#234](https://github.com/m5agent/m5stack-esp-emulator/issues/234)，本次未修改模拟器代码。

## 关键证据

- 源 BIN：2,041,968 B，SHA-256
  `53d73494dc80c8ff3e6ae8a7a8a28b4130f0d2cfe6907f1fa569531932209826`。
- 静态分析（按 `esp32s3` 解析）：`valid=true`，`declared_flash_size=16777216`，
  `partition_end=0x1000000`，`partitions_fit=true`。
- 按设备 8 MB 解析同一分区表：`valid=false`，`partition vfs exceeds flash size`。
- 合成 8 MB 虚拟 flash：`sha256=34aebda915be227f88b3bdbd85d83b856997afd595c5ffd204ce6bd0cdc9c400`
  （源 BIN + `0xFF` 填充到 8 MiB，与审查任务的 `composed_firmware.sha256` 一致）。
- 串口（660 B，之后不再增长，节选）：

  ```text
  E (438) spi_flash: Detected size(8192k) smaller than the size in the binary image header(16384k). Probe failed.
  NEKO: app_main alive | console UART0 @115200 (USB-Serial-JTAG secondary)
  Traceback (most recent call last):
    File "_boot.py", line 11, in <module>
    File "inisetup.py", line 38, in setup
    File "inisetup.py", line 7, in check_bootsec
  OSError: (-24579, 'ESP_ERR_FLASH_NOT_INITIALISED')
  >>> 
  ```

- 观察窗口 60.145 s、13 次采样；帧 174 B、240×135、全黑
  （`sha256=877179afb0021d9147cc66ae65f30cb7c621cab992faa597c2a8eb9d8f5c99b6`）；
  `flash-diff.changed_bytes=0`；`qom-diff` 无增删改。
- 固件在 M5Burner 的自述中写明目标为 “Cardputer ADV（ESP32-S3，16MB Flash）”，
  刷写命令使用 `--flash_size 16MB`，可确认构建目标是 16 MB。

## 文件

- `report.md`：完整归因与代码位置
- `run.json`：结构化记录
- `evidence/analysis-summary.json`：脱敏后的分析、串口、帧与合成摘要

## 未覆盖项

- 同一 BIN 在物理 Cardputer-ADV 上的烧录复现：`NOT RUN`（按 8 MB 规格预期同样失败）。
- 16 MB flash 变体硬件上的行为：`NOT RUN`。
- ELF 符号化：`NOT RUN`（BIN 未附匹配 ELF）。
- 按键/语义输入后的界面行为：`NOT RUN`（应用未到达 UI）。
