# StickADV 0.2 merged 版本的 `usb_dwc_hal_init` 断言归因（issue #278 补充）

- 日期：`2026-11-27`
- 结果：`REVIEW`（归因完成；命中已有 issue #278，只补证据评论，未重复开单、未改代码）
- 工作类型：`firmware_review_attribution`
- 问题来源：内部固件审查任务 `job-280d20633f28`（lane=`SIM_PARTIAL`、status=`manual_review`、error_code=`E_SIM_APP_CRASH`）
- 源码版本：`m5agent/m5stack-esp-emulator @ 74ee6cb00`（仅用于复核板级 `usb-otg` 实例化条件；审查运行时自身未记录 commit）
- 环境：macOS arm64；对既有审查任务证据目录做只读归因；Device Service 原生 QEMU（`m5cardputeradv`）；未使用真机

## 结论

这次失败**不是固件缺陷，也不是 merged/standalone 打包造成的镜像问题**，而是模拟器
`m5cardputeradv` 没有实例化 USB OTG（DWC2）模型：

- guest 在应用初始化早期读 `GSNPSID`（USB OTG 基址 + `0x40`），`m5cardputeradv` 上该区域没有
  DWC 模型，读回 0，于是 `usb_dwc_hal_init` 在 `IDF/components/hal/usb_dwc_hal.c:129` 触发
  `HAL_ASSERT(core_id == CORE_REG_GSNPSID)` 并重启；
- 同一固件的 app-only 版本已在 issue #278 上定位到同一根因（`0180-papercolor-usb-otg.patch`
  只对 `M5_BOARD_STICKS3 || M5_BOARD_PAPERCOLOR` 实例化 `usb-otg`，Cardputer-ADV 不在其中）；
- 本次新增的 merged / standalone 版本（不同 SHA）复现完全相同的断言与前 3 个 backtrace PC，
  说明该失败与镜像组合方式无关，是板级模型缺口。

已在 issue #278 下补充评论：
https://github.com/m5agent/m5stack-esp-emulator/issues/278#issuecomment-7216337434

结论覆盖层级：`virtual-device validation`（完整 8 MiB merged 镜像、可重复 guest panic）＋
`code-level verification`（`0180` patch 的板级条件与固件内 USB HAL 符号/常量）。

## 关键证据

- 固件：`StickADV 0.2`（version id `2126265789181636610`），`stickadv-merged.bin`，931,888 B，
  SHA-256 `d50916a5cb3edac0be6dd4eac965856179de90c35fa4c4988bf17c9fa9eca105`，声明大小与哈希均匹配。
- 组合镜像：8 MiB，SHA-256 `1ed2344e7bd749ebe0af1a1a22c62396054fff151a4f9970fcf253146c1e09c3`；
  bootloader @0、分区表 @0x8000、app0 @0x10000 均 valid，app1 为空，分区表止于 8388608（可容纳）。
- 串口 876 B：ROM 完成 `load`/`entry` 后**没有 IDF banner**，直接打印
  `assert failed: usb_dwc_hal_init ... (core_id == CORE_REG_GSNPSID)`；panic 计数 1、重启 1 次、
  无 task watchdog、无 core dump。
- backtrace 前 3 个 PC（`0x4037816e` / `0x4037fdbd` / `0x40386ea1`）与 #278 的 app-only 样本逐字一致；
  应用段 PC 因重新链接略偏移（`0x4205dfe1`… vs `0x4205dec9`…）。
- 串口 `ELF file SHA256: f6195ae7a3b1ce68` 与镜像 app0 descriptor 的 `elf_sha256
  f6195ae7a3b1ce681000733e47bf4502b7b8c062e5fc976dcb2a9b1479b24055` 前缀一致，确认运行的是解析出的 app0。
- 二进制只读检查：含 `usb_dwc_hal_init`、`usb_dwc_hal_chan_*`、`usb_dwc_hal_port_periodic_enable`
  与 `0x4F54400A` 常量，未出现 `0x4F54280A`，说明固件确实在启动早期初始化 USB DWC host。
- QEMU stderr 只有 `Adding SPI flash device`，无 host 断言、非法指令或进程 abort。
- 查重：`gh issue list --search` 命中 #278（同设备、同断言），未发现其他同现象 issue；本条未重复开单。

## 文件

- `report.md`：完整归因路径、证据链、查重与边界
- `run.json`：结构化记录
- `evidence/summary.json`：脱敏后的镜像解析、串口、二进制与代码侧核对摘要
- `evidence/serial.log`：串口全文（876 B）
- `evidence/qemu.stderr`：QEMU 运行期 stderr（24 B）
- `patches/`：不适用（未改模拟器代码）
- `code/`：不适用（无新增可重建工程）

## 未覆盖项

- 真机 Cardputer-ADV USB host 枚举：`NOT RUN`（需带供电 5 V HUB/dongle）。
- USB PHY/电气、host mode 端点传输：`NOT RUN`。
- panic 之后的应用行为：`NOT RUN`。
- backtrace 符号化：`NOT RUN`（无可匹配 ELF，函数名未解析）。
- 本轮 QOM 导出未产出可用 diff（`qom-diff.json` 报 `device does not advertise qom`），
  因此未引用新的 QOM 数据；寄存器级对照沿用 #278 的既有结果。
- issue #278 的修复与回归验收：`NOT RUN`（本次不修改模拟器代码、不 push、不关闭 issue）。
