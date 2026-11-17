# Cardputer-ADV 16 MB flash 契约镜像归因报告

## 背景

固件审查任务 `job-080c2a4eacc1` 以 `lane=SIM_PARTIAL`、`status=manual_review`、
`error_code=E_NO_FRAME` 结束，结论为“模拟器未产生可证明应用就绪的有效非黑帧”。
本次任务只读读取该任务的证据（`session.json`、`serial`、`analysis.json`、
`observation.json`、`qom-diff`、`flash-diff`、`execution-plan.json`），判断失败阶段，
并决定是否需要向 `m5agent/m5stack-esp-emulator` 提交 issue。

## 被测对象

| 项 | 值 |
| --- | --- |
| 固件 | Micropython code for cardputerADV 1.0 |
| BIN | `ShellMicroPythonShell_CN_v1.0.0_FACTORY_0x0.bin` |
| 大小 / SHA-256 | 2,041,968 B / `53d73494dc80c8ff3e6ae8a7a8a28b4130f0d2cfe6907f1fa569531932209826` |
| 版本 ID | `2122652927099092995` |
| 设备 | Cardputer-ADV（K132-Adv，ESP32-S3FN8，8 MB flash） |
| 审查任务 | `job-080c2a4eacc1` |
| 会话 | `1e9121ded6d34877b5521dc99d16a8c9`（runtime=qemu，whole_device） |
| 合成 8 MB 镜像 | `34aebda915be227f88b3bdbd85d83b856997afd595c5ffd204ce6bd0cdc9c400` |

## 失败阶段判定

逐项排除：

| 假设 | 证据 | 判定 |
| --- | --- | --- |
| 模型/外设缺失 | `execution-plan` 的 features 全部可用；`device-state` 返回 BMI270；会话保持 running | 否 |
| QEMU 断言/崩溃 | `crash-diagnostics.status=no_evidence`，无 panic/watchdog，`qom-diff` 无增删改 | 否 |
| 启动竞态 | 串口只到 REPL，60.145 s 内 660 B 不再增长；帧稳定全黑 | 否 |
| 镜像/分区解析（静态） | 按声明的 16 MB 解析：`valid=true`、`partitions_fit=true` | 否（镜像自洽） |
| 固件与机型 flash 契约 | header 声明 16 MB，设备 8 MB；probe 失败后 `ESP_ERR_FLASH_NOT_INITIALISED` | **是** |

串口（660 B，节选）：

```text
ESP-ROM:esp32s3-20210327
...
entry 0x403c88ac
E (438) spi_flash: Detected size(8192k) smaller than the size in the binary image header(16384k). Probe failed.
NEKO: app_main alive | console UART0 @115200 (USB-Serial-JTAG secondary)
Traceback (most recent call last):
  File "_boot.py", line 11, in <module>
  File "inisetup.py", line 38, in setup
  File "inisetup.py", line 7, in check_bootsec
OSError: (-24579, 'ESP_ERR_FLASH_NOT_INITIALISED')
>>> 
```

关键点：

- `Detected size(8192k)` 与 `cardputer-adv` 设备档案的 `flash_bytes=8388608` 一致；
- `header(16384k)` 来自 BIN 自身：bootloader/app 的 `flash_size_code=4`，分区表
  `vfs` 偏移 `0x310000`、大小 `0xcf0000`，结束于 `0x1000000`；
- 固件落到 REPL，没有应用 UI，因此 240×135 帧始终是 174 B 全黑 PNG。

固件在 M5Burner 的自述里写明目标为 “M5Stack Cardputer ADV（ESP32-S3，16MB Flash）”，
刷写命令也是 `--flash_size 16MB`。由此可确认 BIN 按 16 MB 目标构建，而 Cardputer-ADV
（K132-Adv / ESP32-S3FN8）的官方规格是 8 MB；同一 BIN 在 8 MB 真机上会走相同的
`esp_flash` probe 路径并得到相同结果。

因此**启动失败不是 QEMU 模型缺陷**。

## Device Service 的校验缺口

虽然启动失败在固件侧，但 Device Service 不应接受这个镜像：

1. `platform/tools/device_service.py:2157-2168`（main `6da7ab20`）merged intake 只检查
   `len(data) > spec.flash_size`；2,041,968 B < 8 MB，通过。
2. 合成后 `platform/tools/device_service.py:2322-2325` 用
   `parse_partition_table(image_bytes, image_size=spec.flash_size)` 解析。对合成出的
   8 MB 镜像，结果是 `valid=false`、`partition vfs exceeds flash size`。
3. 但 2328-2353 的两处检查都以 `partition_table["valid"]` 为前提：invalid 分区表
   不会触发 `bootloader_offset_mismatch`，也不会触发
   `partition_end > bootloader_flash_size`（比较对象是 bootloader 自己声明的 16 MB，
   而不是设备容量），且没有对 invalid 分区表本身报错。
4. 镜像因此照常入库、分配会话、烧入 8 MB 虚拟 flash，最后以 `E_NO_FRAME` 收口。

期望行为：intake 阶段返回 4xx（例如 `firmware_flash_contract_mismatch`），并显式比较
`bootloader.flash_size` 与 `spec.flash_size`，让审查直接得到“固件与目标机型 flash 不匹配”
的结论，而不是空跑 60 s 后转人工。

已开 issue：[#234](https://github.com/m5agent/m5stack-esp-emulator/issues/234)
（证据等级：virtual-device validation + code-level verification）。

## 复现

静态分析：

```sh
python3 - <<'PY'
from pathlib import Path
from firmware_analysis import analyze_firmware, parse_partition_table

bin_path = Path('<ShellMicroPythonShell_CN_v1.0.0_FACTORY_0x0.bin>')
a = analyze_firmware(bin_path, expected_chip_id_value=9)
print(a['valid'], hex(a['declared_flash_size']), a['bootloader_flash_contract'])
# True 0x1000000 {'declared_flash_size': 16777216, 'partition_end': 16777216, 'partitions_fit': True}

t = parse_partition_table(bin_path.read_bytes(), image_size=8 * 1024 * 1024)
print(t['valid'], t['errors'])
# False ['partition vfs exceeds flash size']
PY
```

合成 8 MB 镜像（与 `composed_firmware.sha256` 一致）：

```sh
python3 - <<'PY'
src = open('ShellMicroPythonShell_CN_v1.0.0_FACTORY_0x0.bin', 'rb').read()
open('virtual-flash.bin', 'wb').write(src + b'\xff' * (8 * 1024 * 1024 - len(src)))
PY
sha256sum virtual-flash.bin   # 34aebda915be227f88b3bdbd85d83b856997afd595c5ffd204ce6bd0cdc9c400
```

以 device=`cardputer-adv`、runtime=`qemu`、whole_device 创建会话并烧入该 8 MB 镜像，
即可复现上述串口与 60 s 全黑帧。

## 证据摘要

- 观察窗口：60.145 s，13 次采样，会话保持 running，串口 660 B 后不再增长。
- 帧：174 B、240×135、RGB、全 0 像素，
  `sha256=877179afb0021d9147cc66ae65f30cb7c621cab992faa597c2a8eb9d8f5c99b6`。
- `flash-diff`：`changed_bytes=0`，无写入变化。
- `qom-diff`：`added/removed/changed` 均为空。
- `crash-diagnostics`：`status=no_evidence`，panic_count=0，无 watchdog 报告。

## 边界与未覆盖项

- 物理 Cardputer-ADV 烧录复现：`NOT RUN`（按 8 MB 规格预期同样失败）。
- 16 MB flash 变体硬件：`NOT RUN`。
- ELF 符号化：`NOT RUN`（BIN 未附匹配 ELF）。
- 按键/语义输入后的界面行为：`NOT RUN`（应用未到达 UI）。
- 本记录不主张 QEMU 模型缺陷；8 MB flash 模型与设备档案一致。
