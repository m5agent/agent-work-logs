# Star Touchpad 0.9.10 StopWatch 全黑帧归因报告

## 1. 背景与目标

固件审查任务 `job-58f87aaff47d` 以 `lane=SIM_PARTIAL`、`status=manual_review`、
`error_code=E_NO_FRAME` 结束。目标是判定这次「模拟器未产生有效非黑帧」属于模拟器模型问题、
镜像/分区问题、QEMU 主机问题，还是固件自身崩溃，并只在能归因到模拟器且证据充分时提交 issue。

- 固件：`Star Touchpad` 0.9.10，M5Burner version id `2126610489361084417`
- BIN：`Star-Touchpad-0.9.10-m5burner.bin`，1,320,608 B
- SHA-256：`23b62091f0eb8ebc6dd6604284310fb69b2fb11d5a5238e2c14b0d504eb0a036`
- 设备：StopWatch C152（ESP32-S3R8，16 MB flash，CO5300 466×466 圆屏）
- 运行时：Device Service 原生 QEMU，`device_id=stopwatch`，`runtime=qemu`

## 2. 现象

- 会话 `3a1a39720bb840f4b5637306820917be` 在观察窗口 60.15 s 内始终 `state=running`；
- `GET .../frame.png` 始终是 466×466 的 711 B 单色黑帧（SHA-256 `ec5a0018…`）；
- 应用就绪等待返回 `simulator HTTP 408 ready_timeout`，phase=`application_readiness`；
- 串口仅 226 B，止于二级 bootloader 入口 `entry 0x403c8920`，无 IDF banner、无应用日志；
- 审查结论为「模拟器未产生可证明应用就绪的有效非黑帧」，静态检查已通过。

## 3. 证据链

### 3.1 镜像与静态检查通过

- merged 16 MiB：bootloader @0、分区表 @0x8000、app `ota_0` @0x20000 均 valid；
- `ota_1` 为空（`invalid image magic 0xff`），不影响从 `ota_0` 启动；
- 分区表止于 16,711,680 B，16 MiB flash 可容纳；无 secure boot v2 签名；
- app descriptor：`StopWatch-ZeroTouchpad` 0.9.10，ESP-IDF v5.5.4，ELF SHA-256
  `59df54d5…`；静态检查无 finding。

结论：不是镜像不合法、分区越界或 flash 容量不匹配。

### 3.2 guest 存活但停在应用之前

- 串口：226 B，SHA-256 `20ffb092379320c9fe701d3c27d48cb07ea7a9c7e66b94ec8a7a4038123ac3e8`，
  从 0.15 s 首个采样到 60 s 偏移不再增长；最后一行是 bootloader 入口地址；
- crash-diagnostics：`no_evidence`；ROM banner 1 次、IDF banner 0 次、
  application load 0 次、panic 0 次、reboot 0 次、task watchdog 0 次、core dump 未出现；
- QEMU stderr 仅 `Adding SPI flash device`，无 host 断言、abort 或非法指令；
- QOM diff 仅 `rx8130/children/unix-time/value` 前进 71 s，说明板级 RTC 在走、会话在跑；
- flash diff：16 MiB 内 `changed_bytes=0`，guest 没有写 flash，也没有崩溃落盘。

结论：不是 QEMU 整体挂死、不是 host 断言、不是 guest panic/复位、也不是启动竞态
（60 s 窗口内状态稳定，时钟前进）。

### 3.3 guest 未进入 UI 输入路径

执行计划对这份版本记录声明 `touch_required=false`、`button_required=true`（A/B）；
审查仍注入了 5 项输入：

| 输入 | accepted | frame_changed | 前后帧哈希 |
| --- | --- | --- | --- |
| touch tap (233,233) | 是 | 否 | `ec5a0018…` → `ec5a0018…` |
| drag (349,233)→(116,233) | 是 | 否 | `ec5a0018…` → `ec5a0018…` |
| key a tap | 是 | 否 | `ec5a0018…` → `ec5a0018…` |
| key b tap | 是 | 否 | `ec5a0018…` → `ec5a0018…` |
| hold a 2.0 s | 是 | 否 | `ec5a0018…` → `ec5a0018…` |

输入被设备服务接受，但画面完全不变；这与 guest 尚未到达 UI 事件循环一致，
不能据此评价触摸/按键模型或固件交互。

## 4. 失败阶段判定

| 候选阶段 | 判定 | 依据 |
| --- | --- | --- |
| 镜像/分区解析 | 排除 | bootloader/分区表/app 均 valid；flash 契约匹配；无 secure boot 干扰 |
| QEMU 主机断言/abort | 排除 | QEMU stderr 无异常；会话持续 `running`；进程未退出 |
| 启动竞态 | 排除 | 12 次采样跨 60 s，串口与帧哈希均不变；RTC 前进 71 s |
| 固件自身崩溃/复位 | 排除 | panic 0、reboot 0、watchdog 0、无 core dump、flash 未写 |
| 板级外设缺失（PM1/IOE/BMI270/面板） | 排除 | device-state 中 PM1、IOE、BMI270 均在位有值；面板 466×466 可取帧 |
| 模型/外设寄存器缺失（BLE RWIP 握手） | **命中** | 串口停在应用早期、无帧；#293 已用 QMP 定位 CPU0 在 `0x60042000` 轮询 bit15，该地址未建模、读回 0 |

## 5. 代码级定位（引用 #293，本轮只读核对）

issue #293 在该固件上采样到 CPU0 固定于 `0x4207cf33`，对应 app IROM 内循环：

```text
4207cf2d  l32r a8, <literal 0x60042000>
4207cf30  memw
4207cf33  l32i.n a4, a8, 0
4207cf35  bbci a4, 15, 0x4207cf30   ; bit15 未置位就回到 memw
```

同一 IROM 邻近字符串 `rwip_driver.c`、`RWIP Heap alloc` 指向 BLE 控制器 RWIP 路径。
StopWatch 的 PHY 桩模型窗口在 `patches/qemu-m5stack-peripherals/0003-m5stack-shared-spi-full.patch`
中定义为 `0x6002f000..0x60037fff`（`PHY_BASE=0x6002f000`、`PHY_SIZE=0x9000`），
`0x60042000` 不在其中；`0015-motonav-rwip-and-co5300-framing.patch` 处理的是
`A_SYSTEM_BT_LPCK_DIV_INT/FRAC`（`0x60031000` 段），也不覆盖 `0x60042000`。
因此该读落入 S3 IO catch-all、恒为 0，bit15 永不置位，BLE-first 应用在显示首帧前自旋。

本轮限制：该任务证据未包含 CPU PC 采样，`0x60042000` 的具体轮询地址与反汇编沿用 #293
的既有定位，本轮未重新采样，也未重新反汇编 BIN。

## 6. 同一缺陷的第二次独立复现

同一 BIN 曾以另一条 M5Burner 版本记录（version id `2126606902513938434`）送审，
任务 `job-a709b2ca44b7`。两次运行是不同会话、不同 worker generation：

| 项目 | 上一轮 `job-a709b2ca44b7` | 本轮 `job-58f87aaff47d` |
| --- | --- | --- |
| 固件 SHA-256 | `23b62091…` | `23b62091…`（相同） |
| 串口 SHA-256 | `20ffb092…` | `20ffb092…`（相同） |
| 黑帧 SHA-256 | `ec5a0018…` | `ec5a0018…`（相同） |
| 错误码 | `E_NO_FRAME` | `E_NO_FRAME` |
| 终态 | `running`，ready 超时 | `running`，ready 超时 |

两条版本记录的固件字节完全一致，但描述、分类与执行计划不同（本轮 `touch_required=false`），
失败表现逐字节一致，说明失败只随 BIN/设备/运行时复现，与审查输入声明无关。

## 7. 查重与提交

- `gh issue list --search "Star Touchpad"` → 仅 #293（OPEN）；
- `gh issue list --search "0x60042000"` → 无结果；
- `gh issue list --search "E_NO_FRAME stopwatch"` → 仅 #293（OPEN）。

已命中的 #293 标题为「[StopWatch][ESP32-S3] BLE 固件卡在未建模的 0x60042000 RWIP 握手轮询，
60 s 全黑帧（Star Touchpad 0.9.10 / E_NO_FRAME）」，覆盖同一固件 SHA、同一设备、同一错误码。
按查重规则，本轮只在 #293 下补充独立复现证据，不重复开 issue、不关闭 issue。

## 8. 复现步骤

1. 取上述 SHA-256 的 1,320,608 B merged BIN，组合 16 MiB 镜像；
2. 用 `device_id=stopwatch`、`runtime=qemu` 创建虚拟设备会话；
3. 在 60 s 窗口内周期性读取 `frame.png` 与 `serial`：
   - 串口应稳定在 226 B、末行 `entry 0x403c8920`；
   - 帧应为 711 B、466×466、SHA-256 `ec5a0018…` 的单色黑帧；
4. 读取应用就绪等待结果：应返回 `ready_timeout`（phase=`application_readiness`），
   而会话仍是 `running`；
5. 读取 crash 诊断：应为 `no_evidence`（无 panic/reboot/core dump）；
6. 可选：读取 QOM/flash 快照 diff，应只有 RTC 时间前进、flash 零字节变化。

## 9. 影响面与边界

- 影响面：所有在显示首帧前初始化 BLE 控制器 RWIP 的 StopWatch 固件；本轮不受益于
  该固件的镜像组合方式或描述变更。
- QEMU 后端自 2026-11-26 起封存，只接受阻断性修复；本缺口属启动阻断类。
- 未修改模拟器代码、未 push、未关闭任何 issue。
- `NOT RUN`：本轮 PC 采样、ELF 符号化、真机复验、BLE 配对/HID 数据面、esp32sim 对照、
  模型修复后的回归验收。
