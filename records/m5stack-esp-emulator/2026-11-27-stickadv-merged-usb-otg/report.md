# StickADV 0.2（merged）在 Cardputer-ADV 上启动断言归因

## 1. 任务与现象

固件审查任务 `job-280d20633f28` 对 M5Burner 社区固件 **StickADV 0.2**（设备 Cardputer ADV）做
虚拟设备验证，最终为 `SIM_PARTIAL / manual_review / E_SIM_APP_CRASH`：

> 虚拟设备记录到应用运行异常（`usb_dwc_hal_init` `IDF/components/hal/usb_dwc_hal.c:129`
> (`core_id == CORE_REG_GSNPSID`)），串口和运行证据已保留。缺少已匹配的 ELF，函数名尚未解析。

任务使用的文件名是 `stickadv-merged.bin`，版本说明为
`Fixed firmware to be merged binary / standalone flash version.`，与 issue #278 记录的 app-only
版本不是同一个文件（SHA 不同），需要判断这次失败是否仍是同一模拟器缺口。

目标：只读判断失败阶段（模型/外设缺失、QEMU 断言、启动竞态、镜像/分区解析、固件自身崩溃），
能归因到模拟器时只补充已有 issue，不重复开单。

## 2. 输入与身份

| 项 | 值 |
| --- | --- |
| 固件名 / 版本 | StickADV / 0.2 |
| M5Burner version id | `2126265789181636610` |
| 文件 | `stickadv-merged.bin` |
| 大小 | 931,888 B（与声明一致） |
| SHA-256 | `d50916a5cb3edac0be6dd4eac965856179de90c35fa4c4988bf17c9fa9eca105`（与声明一致） |
| 设备 / 运行时 | `cardputer-adv` / `runtime=qemu` |
| 审查任务 | `job-280d20633f28` |
| 会话 | `bd0b2440d22140a0816f4062e7fe944a` |
| 组合后 8 MiB 镜像 | SHA-256 `1ed2344e7bd749ebe0af1a1a22c62396054fff151a4f9970fcf253146c1e09c3` |

固件描述（节选）：`I ported the Game-Simulator Lua script from EdgeTX into the Cardputer ADV ...
USB is supported but a powered 5 volt USB hub or dongle is required and I haven't been able to
test it yet.` 即作者明确在固件中启用了 USB，且未在真机验证。

## 3. 失败阶段判定

逐项排除：

1. **镜像/分区解析**：`analysis.json` 对 8 MiB merged 镜像给出 `valid: true`。bootloader @0
   有效（3 段，chip `esp32s3`，`flash_size_code=3` = 8 MiB，`image_end=15056`）；分区表 @0x8000
   有效（`nvs`、`otadata`、`app0`、`app1`、`spiffs`、`coredump`，md5
   `467eb896e29d1aa938c557f4cdfc4c5b`，止于 8388608）；app0 @0x10000 有效（5 段，
   `image_end=931848`）；app1 为空槽（`0xff`）。**不是解析失败。**
2. **QEMU/host 侧断言**：`qemu.stderr` 全文仅 `Adding SPI flash device`；`crash-diagnostics`
   的 `backend_illegal_instruction=false`；会话进程仍 running。**不是 QEMU abort。**
3. **启动竞态**：panic 在 ROM `entry` 后立即出现，`panic_count=1`、`reboot_requests=1`，
   没有 WDT、没有重复复位；失败点固定在同一断言。**不是竞态。**
4. **外设/模型缺失**：断言读取 USB OTG 的 `GSNPSID` 常量（`CORE_REG_GSNPSID = 0x4F54400A`）。
   `m5cardputeradv` 没有实例化 `esp32s3.usb-otg`，该 MMIO 区域没有模型，读回 0，断言必然失败。
   **命中模型缺口。**
5. **固件自身崩溃**：该固件确实在启动早期初始化 USB DWC host（二进制含 `usb_dwc_hal_init`、
   `usb_dwc_hal_chan_*`、`usb_dwc_hal_port_periodic_enable` 与 `0x4F54400A` 常量），
   但在真机 S3 上 `GSNPSID` 是 SoC 常量，正常应返回 `0x4F54400A`。当前证据只证明模拟器缺模型，
   不能证明固件逻辑有错。**归因为模拟器。**

## 4. 证据链

### 4.1 串口（876 B）

```text
ESP-ROM:esp32s3-20210327
Build:Mar 27 2021
rst:0x1 (POWERON),boot:0x4 (SPI_FLASH_BOOT)
SPIWP:0xee
mode:DIO, clock div:1
load:0x3fce3808,len:0x4bc
load:0x403c9700,len:0xbd8
load:0x403cc700,len:0x2a0c
entry 0x403c98d0

assert failed: usb_dwc_hal_init IDF/components/hal/usb_dwc_hal.c:129 (core_id == CORE_REG_GSNPSID)

Backtrace: 0x4037816e:0x3fceb910 0x4037fdbd:0x3fceb930 0x40386ea1:0x3fceb950
0x4205dfe1:0x3fceba80 0x4204d843:0x3fcebaa0 0x4204ea25:0x3fcebad0 0x4204a6ea:0x3fcebb10
0x42009a35:0x3fcebb60 0x4200586c:0x3fcebbd0 0x420063d8:0x3fcebbf0 0x42031b42:0x3fcebc50

ELF file SHA256: f6195ae7a3b1ce68

Rebooting...
ESP-ROM:esp32s3-20210327
Build:Mar 27 2021
rst:0xc (RTC_SW_CPU_RST),boot:0x4 (SPI_FLASH_BOOT)
...
entry 0x403c98d0
```

（第二段为重启后的 ROM banner，无新的应用日志。）

### 4.2 与 #278 的对照

issue #278 的 app-only 样本（`stickadv.bin`，866,048 B，SHA-256 `f3bdfd50…`）串口：

```text
assert failed: usb_dwc_hal_init IDF/components/hal/usb_dwc_hal.c:129 (core_id == CORE_REG_GSNPSID)

Backtrace: 0x4037816e:0x3fceb970 0x4037fdbd:0x3fceb990 0x40386ea1:0x3fceb9b0 0x4205dec9:...
ELF file SHA256: 88d58c08feb01598
```

| 项 | app-only（#278） | merged（本条） |
| --- | --- | --- |
| 断言 | `usb_dwc_hal_init:129` | 同 |
| 前 3 个 PC | `0x4037816e` / `0x4037fdbd` / `0x40386ea1` | 同 |
| 应用段 PC | `0x4205dec9`… | `0x4205dfe1`…（重新链接偏移） |
| ELF SHA 前缀 | `88d58c08` | `f6195ae7` |

同一固件的两种打包形式、不同链接结果，断言与调用链前段完全一致，说明不是 merged 组合引入的问题。

### 4.3 镜像内证

- app0 descriptor：`version = esp-idf: v4.4.7 38eeba213a`、`project_name = arduino-lib-builder`、
  `elf_sha256 = f6195ae7a3b1ce681000733e47bf4502b7b8c062e5fc976dcb2a9b1479b24055`。
- 串口报告的 `ELF file SHA256: f6195ae7a3b1ce68` 与之同前缀，确认串口输出来自被解析的 app0。
- 只读二进制检查（在本机对上传 BIN 做字节搜索，不执行）：
  - `usb_dwc_hal_init` @ 159506；
  - `usb_dwc_hal_chan` @ 145449；
  - `usb_dwc_hal_port_periodic_enable` @ 145169；
  - `GSNPSID` @ 158972；
  - `0x4F54400A`（`CORE_REG_GSNPSID`）出现 1 次，`0x4F54280A` 出现 0 次。
- 文件系统分区 `spiffs` 为 `UNFORMATTED`（全 0 / 已擦除），属镜像未带 SPIFFS 内容；与本崩溃无因果关系。

### 4.4 代码侧核对

当前 `m5agent/m5stack-esp-emulator` main `74ee6cb00`：

- `patches/qemu-m5stack-peripherals/0172-sticks3-usb-otg-device.patch` 实现 `esp32s3.usb-otg`；
- `patches/qemu-m5stack-peripherals/0180-papercolor-usb-otg.patch` 把实例化条件限定为
  `m5_board == M5_BOARD_STICKS3 || m5_board == M5_BOARD_PAPERCOLOR`，`M5_BOARD_CARDPUTER_ADV`
  不在其中；
- 因此 `m5cardputeradv` 上 `0x60080000` 没有 DWC 模型，`GSNPSID` 读回 0。

`#278` 已给出同一 runtime 的寄存器/QOM 对照：`m5sticks3` 有 `/machine/soc/usb-otg` 且
`xp /1wx 0x60080040` 读回 `0x4f54400a`；`m5cardputeradv` 无该节点、读回 0。本条不重复该实验，
只补充 merged 版本的复现。

## 5. 查重与处置

- `gh issue list -R m5agent/m5stack-esp-emulator --search "usb_dwc_hal_init"` → #278、#226；
- `--search "OTG"` → #278、#226、#202（closed）、#220（closed）、#217（closed）；
- #278 的标题、设备、断言、根因与本次完全对应；#226 是 Tab5/P4 同类但不同 SoC 的跟踪项。
- 结论：**不重复开单**。已在 #278 下补充 merged 版本复现评论：
  https://github.com/m5agent/m5stack-esp-emulator/issues/278#issuecomment-7216337434

未修改模拟器代码，未 push 模拟器仓库，未关闭任何 issue。

## 6. 结论

`E_SIM_APP_CRASH` 的根因是 **Cardputer-ADV 板级 USB OTG（DWC2）模型缺失**，不是固件崩溃，
也不是 merged 打包、启动竞态或镜像解析问题。issue #278 的修复诉求不变：在 `m5cardputeradv`
上按板级接线实例化 `esp32s3.usb-otg`（或在设备 profile/会话层显式声明 USB 不支持并让审查
归为 `E_SIM_MODEL_GAP` / PARTIAL）。

## 7. 证据等级与边界

- **virtual-device validation**：8 MiB merged 镜像在 Device Service QEMU 会话中完成虚拟烧录与启动，
  串口、事件、镜像解析和 QEMU stderr 均保留；断言可重复。
- **code-level verification**：`0180` patch 的板级实例化条件、固件内 USB HAL 符号与
  `CORE_REG_GSNPSID` 常量。
- NOT RUN：真机 Cardputer-ADV USB host 枚举（需供电 5 V HUB/dongle）、USB PHY/电气、
  host mode 端点传输、panic 之后的应用行为、backtrace 符号化（无匹配 ELF）。
- 本轮 `qom-diff.json` 报 `device does not advertise qom`，未用于结论；不把该字段解释为设备能力。
- 不涉及固件安全评价；真机行为未验证。
