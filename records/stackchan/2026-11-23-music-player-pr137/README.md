# StackChan PR #137 MicroSD 音乐播放器 App 评审

- 日期：`2026-11-23`
- 结果：`PARTIAL`（构建 `PASS`，虚拟设备集成 `PASS`，播放路径 `NOT RUN`）
- 工作类型：`pr_review`
- 问题来源：https://github.com/m5stack/StackChan/pull/137
- 源码版本：`m5stack/StackChan @ db4fee0f5525a80ee34cd71131f2fb2739621e35`（base `28b9f0c`）
- 环境：macOS 15 arm64、ESP-IDF v6.1、本机 Device Service 的 `stackchan` QEMU profile

## 结论

PR 可以在 IDF v6.1 下完整构建（app 3,976,928 B，分区余量 23%），在虚拟 StackChan 上
能启动、注册 MUSIC 图标、进入 App、渲染主界面/设置/播放列表，并在无 microSD 时给出
可读的空状态，不崩溃。没有发现阻塞合并的硬件或集成缺陷。

需要作者处理的是一致性与边界问题：

1. `onRunning()` 在 LVGL 锁外调用 `GetStackChan().update()`，与 HAL/DANCE 的既有约定不一致，
   是跨任务 LVGL 访问；
2. 可见性 NVS 键改名导致老用户偏好被静默重置；
3. 24-bit WAV 会被探测为有效但静默跳过；
4. MP3 坏帧路径整块丢弃 16 KB 缓冲；
5. `PsramAllocator` 的 OOM 语义不符合 allocator 要求；
6. `hal.cpp` 的 100→80 ms 是全局改动，与本功能无关。

PR 的核心承诺（真实 microSD 上的扫描、解码、播放、seek、NVS 持久化、舵机/RGB）在本机
**没有**被验证：`stackchan` profile 的 `features.storage=false`，没有 SD 模型。

## 关键证据

- 构建：`idf.py build` 2503/2503，退出码 0；merged BIN SHA-256
  `de1b0779…77583`，见 `evidence/05-build.txt`。
- 虚拟设备：session `7ff25f9c…3a20`，串口确认 `[MUSIC] on create`、`[Launcher] handle open
  app, app id: 7`、`[MUSIC] on open`；无卡时 `sdmmc_init_sd_if_cond ... 0x108` 后
  `[MUSIC] SD mount failed ... ESP_ERR_INVALID_RESPONSE`，UI 正常，见
  `evidence/06-virtual-device-run.txt` 与 `evidence/frames/`。
- GPIO35（LCD D/C 与 SD MISO 共用）：IDF v6.1 的 `esp_lcd_panel_io_spi.c` 在每笔事务后
  `gpio_ll_output_disable(dc)`，因此该用法成立，见 `evidence/03-gpio35-usage.txt`。
- 代码定位：`evidence/04-code-findings.txt`。

## 文件

- `report.md`：完整评审报告、逐项发现与合并建议
- `run.json`：结构化记录
- `evidence/01-scope.txt`：PR 状态、固定提交、diff 规模
- `evidence/02-device-profile-redacted.json`：脱敏后的设备能力
- `evidence/03-gpio35-usage.txt`：GPIO35 双用途与 IDF 行为核对
- `evidence/04-code-findings.txt`：并发、NVS、WAV/MP3、allocator、扫描
- `evidence/05-build.txt`：构建与二进制哈希
- `evidence/06-virtual-device-run.txt`：会话步骤、串口、截图与边界
- `evidence/frames/01..05-*.png`：launcher 图标、主界面、设置、空播放列表、EXIT 后画面

## 未覆盖项

- 真实 microSD：挂载、递归扫描 1,000+ 曲目、MP3/WAV 解码、24 kHz 重采样、seek、切歌、
  循环/随机、播放中拔卡——全部 `NOT RUN`。
- 音频质量、音量曲线、爆音、I2S 时钟——`NOT RUN`。
- 舵机摆动、RGB 随拍、头部校准的实际运动——`NOT RUN`（仅验证 UI 与调用路径）。
- NVS 跨断电持久化——`NOT RUN`。
- 实机与虚拟设备 GPIO35 pad 级电气行为——`NOT RUN`。
- EXIT 触发的 warm reboot 在虚拟设备上停在 `cpu_start: Multicore app`，复位前无 panic；
  判为虚拟设备 reset 路径限制，未在实机复现。
