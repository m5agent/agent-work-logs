# Atom Lite「ATEM HD8 EMULATOR 1.01」审查 `E_SIM_APP_READY_PARTIAL` 归因

- 日期：`2026-11-23`
- 结果：`PARTIAL`（归因完成；判定非模拟器启动缺陷，未开 issue）
- 工作类型：`firmware_review_attribution`
- 问题来源：内部固件审查任务 `job-64c19d0704ae`（lane=`SIM_PARTIAL`、status=`manual_review`、error_code=`E_SIM_APP_READY_PARTIAL`）
- 源码版本：`m5agent/m5stack-esp-emulator @ 55e5763ea`；审查服务 `auto-firmware-review @ a938d965`
- 环境：macOS arm64；对既有审查任务证据目录做只读归因；Device Service 原生 QEMU（`m5atomlite`）；未使用真机

## 结论

这次**启动与运行本身是成功的**：qemu-esptool 回读与合成镜像逐字节相等，guest 正常加载 bootloader
（`entry 0x400805e4`）并运行应用，2.0 s 打印应用自己的 ready 行，连续运行 60.148 s（13 次采样全
`running`），无 panic、无 WDT、无重启循环，QEMU stderr 仅 `Adding SPI flash device`。因此不存在
QEMU 断言、启动竞态、镜像/分区解析失败或模型卡死。

把任务收口为 `E_SIM_APP_READY_PARTIAL` 的原因是**审查侧的 readiness/输入判定口径与无 framebuffer
机型的能力边界**，不是模拟器实现缺陷：

1. Atom Lite 无板载显示屏（`display=null`、`screenshot=false`、`frame_bytes=0`、`frame_scope=serial_only`）。
   无屏机型的 `boot_status` 只能依赖串口 ready marker，而本任务没有配置 network `ready_markers`，
   于是 `ready` 判定条件为空对象，审查服务**根本没有发起 readiness 探测**（`wait.json` 为 `{}`），
   `boot_status` 在结构上必然是 `PARTIAL`。结论文案「首帧已出现」是固定模板，与实际 `frame_bytes=0`
   矛盾。
2. 输入探针被「帧必须以 PNG magic 起始」门控，无 framebuffer 时永不执行（`interactions.json`：
   `accepted=0`、`changed=0`、`status=NOT RUN`）；同时描述只提到单个 button，审查计划却默认成
   `required_buttons=["a","b"]`，与单键板不匹配。
3. 描述声明网络功能（ATEM UDP/videohub/web + DHCP server），但 Atom Lite 无 NIC，执行计划
   `network=false`、`native_sta=board_not_advertised`。guest 自己打印 `W5500 not found - check the
   PoE base`，说明该功能依赖外置 PoE 底座，本虚拟机型不覆盖——同 guest 数据面只能 `NOT RUN`，
   不能表述为 FAIL 或「网络不通」。
4. 启动期 `Corrupted dir pair {0x0,0x1}` → `mount failed (-84)` 是 sparse merged 镜像首启空白
   FS 的已知现象（issue #206 已登记），guest 随后回退内置 HD8 ISO 状态并自行格式化 LittleFS，
   写入已由 flash 差异与回读证明持久化，不构成模拟器缺陷。

结论覆盖层级：`virtual-device validation`（启动/运行/外设）＋`code-level verification`（readiness
与输入门控判定代码）。`failure_attribution` 四个桶（emulator_or_transport / firmware / unknown /
evidence_collection）全为空，与「无模拟器归因证据」一致。

## 关键证据

- 固件：`atem-emu-atom-0.5.0-stock.bin`，522,384 B，SHA-256
  `86ad1b7f784e3a9965884f46e3114c03cfbd21aa9f9f4bf06b8578d4691c9758`；合成后 4 MiB 镜像 SHA-256
  `3a59f6f97224f7c73bf1e803038f449135a5877af51e3f8e9a7115803b1e387e`，qemu-esptool 回读逐字节相等。
- 静态：bootloader `0x1000` 有效（3 段、`entry 0x400805e4`、`flash_size_code=2` = 4 MB）；分区表有效，
  `nvs 0x9000/20480`、`otadata 0xE000/8192`、`app0 0x10000/1310720`、`app1 0x150000/1310720`、
  `spiffs 0x290000/1441792`、`coredump 0x3F0000/65536`，结束于 `0x400000` 与 4 MiB 容量一致；
  `app0` 有效（5 段、`entry 0x40082f90`）、`app1` 为空槽（0xff）、`spiffs` 入库时 `UNFORMATTED`。
- 运行：60.148 s、13 次采样全部 `running`；`qom-diff` 仅 6 项变化且均为外设前进计数——
  `onboard_io/led-frames` 0→473、`led-rgb` 0→24、`output-transitions` 0→473、
  `rmt-classic/tx-completions` 0→473、`tx-last-tick-hz` 0→10000000、`tx-symbols` 0→11352，
  即应用主循环与 SK6812/RMT 输出持续工作。
- flash：`changed_bytes=129`、13 段，分别落在 NVS（`0x9000..0x9059`）与 spiffs 超级块
  （`0x290000..0x291034`）；末态镜像 `0x290000`/`0x291000` 可见 `littlefs` 超级块魔数（block size
  4096、block count 352），是 guest 对空白分区执行格式化的结果。
- 串口（948 B 后不再增长，节选）：

  ```text
  rst:0x1 (POWERON_RESET),boot:0x12 (SPI_FAST_FLASH_BOOT)
  load:0x3fff0030,len:1184
  load:0x40078000,len:13220
  load:0x40080400,len:3028
  entry 0x400805e4
  00:00:00 atem-emu-atom 0.5.0
  ./components/esp_littlefs/src/littlefs/lfs.c:1229:error: Corrupted dir pair at {0x0, 0x1}
  E (97) esp_littlefs: mount failed,  (-84)
  00:00:00 state: built-in standard HD8 ISO
  00:00:00 M/E1 PGM 1 Camera 1
  00:00:02 ethernet: W5500 not found - check the PoE base
  00:00:02 ethernet: 0.0.0.0, link down
  00:00:02 ready: ATEM udp 0.0.0.0:9910, videohub 9990, web :80, free heap 220724
  ```

  以上均为 guest 自身日志；`ready:` 是应用级就绪标记，但本任务未把它配置为审查 ready marker。
- 判定代码（审查服务 `a938d965`）：`service/app.py:4017-4022` ready_markers 仅来自任务 network
  配置；`:4041-4046` `ready` 为空时不调用 `/wait`；`:4743-4754` 无 framebuffer 机型要求
  `serial_runtime_ready`（依赖 ready_markers）；`:4312-4313`、`:4346-4347` 输入探针仅在 PNG 帧存在时执行；
  `:5179-5181` `boot_status != PASS` 时固定写「首帧已出现…」并置 `E_SIM_APP_READY_PARTIAL`；
  `:806-825` 描述含 button 词且无显式 a/b 时默认 `["a","b"]`。
- 设备档案：`platform/qemu/profiles.json` 中 `atom-lite` 为 `display=null`、`input=gpio-button`、
  `peripheral_status=partial`；`devices/esp32-lx6/atom-lite/device.json` 仅一个 `button`（USER、GPIO39）
  且 `led_matrix=1x1`；2026-10-29 原生验证已覆盖启动、两次 USER 按键、GPIO27 RMT RGB 与无 LCD 契约。
  外设目录仅有 `ethernet-sr9900a`（Cardputer Zero Linux 后端），无 W5500 SPI 模型。

## 文件

- `report.md`：完整归因路径、证据分层、查重与未覆盖项
- `run.json`：结构化记录
- `evidence/summary.json`：脱敏后的执行计划、固件分析、串口、QOM/flash 差异、判定代码与查重摘要
- `evidence/serial.log`：串口全文（948 B）
- `evidence/qemu.stderr`：QEMU 运行期 stderr（24 B）
- `patches/`：不适用（本次未改代码）
- `code/`：不适用（无新增可重建工程）

## 未覆盖项

- 真机复现：`NOT RUN`（无 Atom Lite 实机档期；不影响「非模拟器启动缺陷」结论）。
- 独立重跑第二次虚拟设备会话：`NOT RUN`（只读归因既有任务证据，未新建会话）。
- 交互输入验证：`NOT RUN`（无 framebuffer 时探针被门控，输入未在 guest 中执行；不得表述为输入失败）。
- 网络数据面：`NOT RUN`（机型无 NIC，准入不支持；W5500 为外置 PoE 底座，不属本机型模型）。
- IR、浏览器准入及其余未选外设路径：沿用设备档案 `partial` 边界，未验证。
- 固件静态字符串中发现 2 个私网 IPv4 字面量（地址值不记录），是否属预期配置由内容审查判断：`REVIEW`。
