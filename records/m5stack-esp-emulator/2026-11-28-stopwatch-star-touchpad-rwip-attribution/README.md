# Star Touchpad 0.9.10 在 StopWatch 上 60 s 全黑帧归因（issue #293 补充复现）

- 日期：`2026-11-28`
- 结果：`REVIEW`（归因完成；命中已有 issue #293，只补证据评论，未重复开单、未改代码、未 push）
- 工作类型：`firmware_review_attribution`
- 问题来源：内部固件审查任务 `job-58f87aaff47d`（lane=`SIM_PARTIAL`、status=`manual_review`、error_code=`E_NO_FRAME`）
- 源码版本：`m5agent/m5stack-esp-emulator @ 74ee6cb00`（只读核对板级 PHY 桩窗口与 RWIP 补丁作用域；审查运行时自身未记录 commit）
- 环境：macOS arm64；对既有审查任务证据目录做只读归因；Device Service 原生 QEMU（`stopwatch`）；未使用真机

## 结论

这次失败**不是固件缺陷，也不是镜像或分区解析问题**，而是模拟器缺少 BLE 控制器 RWIP
握手寄存器窗口的模型：

- guest 已越过 ROM 与二级 bootloader，会话 60.15 s 内始终 `state=running`，没有 panic、
  没有重启、没有 core dump；QEMU stderr 只有 `Adding SPI flash device`，没有 host 断言；
- 但串口固定 226 B，止于 `entry 0x403c8920`，没有 IDF banner、没有应用日志；13 次采样
  帧始终是 711 B 的单色黑帧（SHA-256 前缀 `ec5a0018…`）；
- 同一 BIN 的上一轮审查（`job-a709b2ca44b7`，不同 M5Burner 版本记录）产生**逐字节相同**的
  串口（`20ffb092…`）与帧（`ec5a0018…`）；issue #293 已在该固件上用 QMP 采样定位到
  CPU0 固定轮询 `0x60042000` 的 bit15，该地址落在未建模区、读回 0，属 BLE RWIP 初始化自旋；
- 因此本次是同一模型缺口的**独立复现**，不是新问题。已在 issue #293 下补充本轮证据评论，
  未重复开单。

结论覆盖层级：`virtual-device validation`（两轮独立 qemu 会话，串口与帧哈希逐字节一致）＋
`code-level verification`（板级 PHY 桩窗口上界与 RWIP 轮询地址引用 #293 的既有定位；
本轮未重新采样 PC）。

## 关键证据

- 固件：`Star Touchpad` 0.9.10（M5Burner version id `2126610489361084417`），
  `Star-Touchpad-0.9.10-m5burner.bin`，1,320,608 B，SHA-256
  `23b62091f0eb8ebc6dd6604284310fb69b2fb11d5a5238e2c14b0d504eb0a036`。
- 设备 StopWatch C152（ESP32-S3R8，16 MB flash，CO5300 466×466）。
- 镜像：merged 16 MiB，bootloader / 分区表 / `ota_0` app 均 valid，`ota_1` 为空，
  分区止于 16,711,680 B（可容纳）；静态检查通过。
- 会话：`3a1a39720bb840f4b5637306820917be`，`runtime=qemu`，观察窗口 60.15 s，
  终态 `running`；ready 等待返回 `HTTP 408 ready_timeout`（phase=`application_readiness`）。
- 串口：226 B，SHA-256 `20ffb092379320c9fe701d3c27d48cb07ea7a9c7e66b94ec8a7a4038123ac3e8`，
  末行 `entry 0x403c8920`；从首个采样（0.15 s）到 60 s 偏移未再增长。
- 帧：466×466 RGB PNG，711 B，SHA-256
  `ec5a0018ce3a1ba0992c306981d1c78f2b8c1d9520cac96dbde1db141fbf2a81`，13 次采样不变。
- crash-diagnostics：`status=no_evidence`，panic 计数 0、重启请求 0、IDF banner 0、
  application load 0、无 core dump。
- QOM diff：仅 `rx8130/children/unix-time/value` 前进 71 s（板级 RTC 存活），无设备增删。
- flash diff：16 MiB 内 `changed_bytes=0`，guest 未写入 flash。
- 输入：touch tap、drag、A、B、hold A（2 s）共 5 项均 accepted，`frame_changed=false`，
  前后均为同一黑帧哈希；说明 guest 未进入 UI 输入路径。
- 查重：`gh issue list --search "Star Touchpad"` 与 `"E_NO_FRAME stopwatch"` 均只命中
  开着的 #293；未发现其他同现象 issue。

## 文件

- `report.md`：完整归因路径、证据链、失败阶段判定与边界
- `run.json`：结构化记录
- `evidence/summary.json`：脱敏后的任务、镜像、串口、帧、QOM、flash 与输入摘要
- `evidence/serial.log`：串口全文（226 B）
- `evidence/black-frame.png`：60 s 观察期内的黑帧原图（711 B）
- `evidence/emulator-failure.json`：审查服务产出的失败分类（`E_NO_FRAME`）
- `patches/`：不适用（未改模拟器代码）
- `code/`：不适用（无新增可重建工程）

## 未覆盖项

- 本轮 CPU PC 采样：`NOT RUN`（该任务证据未含 `crash/cpu-pc`，`0x60042000` 轮询定位沿用 #293）。
- 匹配 ELF 符号化：`NOT RUN`（任务未上传 ELF）。
- 真机 StopWatch 复验与 BLE 配对/HID 数据面：`NOT RUN`。
- esp32sim 同 BIN 对照：`NOT RUN`（本轮只做 qemu 证据归因；#293 已记录 esp32sim 侧
  `app_main` 与 BLE 初始化输出）。
- 模型修复与回归验收：`NOT RUN`（本次不修改模拟器代码、不 push、不关闭 issue）。
