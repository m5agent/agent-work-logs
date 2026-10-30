# StackChan 开机自动跳舞固件报告

## 背景

- 来源：用户要求一套 StackChan 固件，开机自动跳舞，并包含屏幕表情和
  A180 机身 12 颗 RGB 灯效果。
- 产品：StackChan，CoreS3 主控与 A180 机身。
- 目标：生成可直接烧录的完整镜像和可重建源码。
- 约束：不改变硬件；首版需要避免舵机机械端点，并记录真机未验证的边界。

## 设计与实现

- 使用官方 `M5StackChan 1.1.1` BSP 完成 CoreS3、IO 扩展、INA226、
  显示屏和 RGB 灯初始化。
- 屏幕采用程序化绘制，不依赖外部图片资源。表情为 Happy、Excited、Wink、
  Love、Cool、Finale；动态内容包括眨眼、视线、嘴形和节拍条。
- 背景与面板只在表情切换时重绘，动作帧只重绘内部动态区域，避免整屏
  清屏造成明显撕裂。
- 舞蹈为 16 秒、38 个关键帧，水平限制在 ±48°，俯仰限制在 18°–72°，
  舵机速度不超过 `900/1000`。
- 12 颗 RGB 灯使用与表情对应的彩虹、单侧、心跳、扫描和终场模式，亮度
  控制在较低范围。
- 轻触机身顶部触控区域重新开始舞蹈。

## 首版失败与修复

首版候选镜像能显示首帧，但很快触发：

```text
assert failed: spinlock_release spinlock.h:190
(core_owner_id == lock->owner)
```

反向符号化栈落在 ESP-IDF UART RX 中断、SCSCL 写位置和 M5GFX 绘制路径。
BSP 的动作任务以 50 Hz 弹簧动画更新舵机，每个单播写随后等待舵机应答。
虚拟 SCSCL 模型在持续 TX/RX 注入下暴露了 UART ring buffer 的并发断言。

最终固件不再让 BSP 动作任务驱动舵机：

1. BSP 初始化后关闭自动扭矩释放，避免空闲轮询。
2. 直接从 BSP Settings 的 `servo/zero_pos_1` 与 `servo/zero_pos_2` 读取
   已校准零位。
3. 通过广播 `SYNC_WRITE` 一次设置扭矩和两个目标位置，不等待单舵机应答。
4. 主循环以平滑插值、约 20 Hz 发送新的双舵机同步位置帧。

协议与数学约束保持为 0.1° 角度单位、`5/16°` 原始位置步进，并继续使用
保守角度包络。该改动同时改善硬件端的控制确定性。

## 构建环境与命令

- Arduino CLI：`1.5.1`
- Board package：`m5stack:esp32@3.3.10`
- FQBN：`m5stack:esp32:m5stack_cores3`
- ESP-IDF：`v5.5.4`
- M5StackChan：`1.1.1`
- M5Unified：`0.2.28`
- M5GFX：`0.2.35`
- IRremoteESP8266：`2.9.0`
- M5Unit-NFC：`0.1.2`

```bash
python3 tools/validate_timeline.py
arduino-cli compile \
  --fqbn m5stack:esp32:m5stack_cores3 \
  --build-path build/arduino-build \
  --output-dir build/arduino \
  --export-binaries \
  stackchan_dance
```

## 执行与证据

### 镜像结构

- merged image：16,777,216 bytes，烧录偏移 `0x000000`。
- app image：570,928 bytes。
- ESP32-S3 header：16 MB flash、DIO、80 MHz，checksum `0x05`，有效。
- 合并镜像在 `0x0/0x8000/0xE000/0x10000` 与 bootloader、partition table、
  boot_app0 和 app 逐字节一致。

### 虚拟设备运行

- Device Service：真实 `/api/v1` artifact、firmware、session、wait、
  frame、logs、device-state、QOM、flash-hash 和 evidence 路径。
- Runtime：`qemu`，machine `m5stackchan`。
- 烧录：`esp-emu-esptool`，`verified=true`，session-isolated 16 MiB flash。
- 启动标记：`StackChan auto-dance started`。
- 运行：超过 90 秒，5 次完整循环；125 条 `DANCE cue=` 日志。
- 稳定性：最终镜像的 QEMU stderr 中没有 assert、panic、core-dump 或
  backtrace 标记。

### 表情

每秒采集一次虚拟机帧，共 19 帧，尺寸均为 320×240，19 个 SHA-256 全部
不同。总览位于 `evidence/contact-sheet.png`，可见 Happy、Excited、Wink、
Love、Cool 和 Finale 的不同构图。

### 舵机数据面

2026-10-29 的派生摘要当时上报 `1006` 个：

```text
[scs] packet id=254 inst=83 len=18 addr=42
```

`id=254` 为广播地址，`inst=83` 为 `SYNC_WRITE`，`addr=42` 为目标位置
内存表地址。每帧同时携带 ID 1/2 的位置、时间和速度字段。

该文件是派生摘要，不是原始 SCS trace。2026-10-30 复核未能在本记录中找到
可重算 `1006` 的原始数据，因此将此计数降级为“历史上报值，未独立复核”。
后续同一完整 Flash 的 browser QEMU 运行在不同窗口直接观测 30 个有效 SCS
包，并证明 present/goal 位置变化；该结果不能用于反推旧 native 运行计数。

### 灯带数据面

QEMU M5IOE1 I2C trace 共记录：

- `1367` 次从寄存器 `0x30` 开始的 12 灯 RGB 缓冲刷新；
- `32808` 个 RGB 寄存器写。

不同表情的缓冲字节序列不同，证明灯效持续由 guest I2C 写入模型，而不是
服务端伪造静态颜色。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | Arduino 实际交叉编译；应用镜像 header/checksum/hash 有效 |
| flash | PASS | 16 MiB merged image 经 Device Service 烧录，`verified=true` |
| transport | PARTIAL | 启动与派生摘要存在；SCSCL `1006` 计数缺少可重算原始 trace |
| data_behavior | PASS | 125 个舞步事件、5 次循环、表情帧变化、持续 RGB 写 |
| visual_or_physical | PASS（virtual） / NOT RUN（physical） | 19 个真实虚拟机帧；物理机械、电气、光学和声学未测试 |

## 验证边界

- 虚拟设备验证不等同于实体 StackChan 测量。
- 未验证舵机真实扭矩、噪声、寿命、堵转、电池瞬时电流和机械零位。
- 未验证 LED 的实体亮度、颜色一致性、功耗和外壳导光效果。
- 未验证 CoreS3 实体屏幕的可视帧率、面板响应和触摸重启。
- 未验证相机、NFC、IR、Wi-Fi、BLE、麦克风和扬声器。
- 结论只覆盖上述 merged image 的 SHA-256；重新编译或修改源码不继承 PASS。
- 记录内源码已用相同工具链重新编译通过；由于 Arduino/ESP-IDF 会把构建路径等
  元数据写入镜像，重建 BIN 的完整 SHA-256 不保证与交付 BIN 相同。

## 风险与回滚

- 烧录完整 merged image 会替换设备现有固件。回滚方式是重新烧录官方
  StackChan 用户固件或原厂备份。
- 首次运行应使用 USB-C 供电并清空头部运动范围；不要通电强扳舵机。
- 如果实体零位偏斜，先运行官方 `HomeCalibration`，再重新烧录本固件。
- 本固件不修改 eFuse，不启用 Secure Boot 或 Flash Encryption。
