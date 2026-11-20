# 审查服务 app-only 启动上下文、错误文案与设备映射修复

- 日期：`2026-11-20`
- 结果：`PASS`（错误文案、映射、Cardputer/ADV 启动基底、6 条复审）；`PARTIAL`（StickS3 自定义分区、M5Paper 原版、部分 Cardputer 应用仍未闭环）
- 工作类型：`code_change`
- 问题来源：用户反馈“最近好几个审核都报错说没有什么 app 上下文”；近期 11 条 app-only 错误
- 源码版本：`firmware-review-service @ 883ccf0` → `479a852` → `9e62882`
- 环境：macOS arm64；常驻审查服务（LaunchAgent）；本机 Device Service 原生 QEMU；
  复审均为 saved-snapshot，`submit=false`；未使用真机

## 结论

这批“没有 app 上下文”不是固件或模拟器失败，而是**上传的 BIN 只含应用分区**，审查服务缺少
可验证的 bootloader + 分区表来组装可启动镜像。本次做了三类修复：

1. **错误文案**：`E_APP_ONLY_UNSUPPORTED_DEVICE` / `E_APP_ONLY_BASE_REQUIRED` 明确写出
   “该 BIN 仅含应用分区，没有 bootloader/分区表；请上传完整合并镜像或提供同工具链启动基底”；
   `E_APP_ONLY_TARGET_MISMATCH` 明确写出“这是构建目标不匹配，不是启动上下文缺失”。
   `firmware-intake.json` 增加 `device_id` 与
   `requires=full_flash_image_or_toolchain_boot_context`。
2. **映射**：补 `STICKC`/`M5STICK` → `stickc`/`m5stick`；移除错误的
   `PAPER`/`M5STACK_PAPER` → `papermono`（原版 M5Paper 是 ESP32 classic，PaperMono 是
   ESP32-S3）；为 `PAPER`、`XIAOZHI_CARD_KIT`、`M5GO`、`FIRE` 增加明确的“无档案”原因，
   不再只显示 `no emulator profile`。
3. **启动基底**：
   - 用官方 UIFlow2 v2.5.4 Cardputer 8 MB 镜像作为 `cardputer` / `cardputer-adv` 的
     stock base（factory 槽 0x10000、大小 0x541000）；
   - 用官方 UIFlow2 v2.5.3 PaperMono 16 MB 镜像作为 `papermono` 的 stock base
     （factory 槽 0x10000、大小 0x710000）；
   - 为 StickS3 增加 default_8MB 的 vendor boot context（otadata 0xE000、ota_0 0x10000、
     app 槽 0x330000），先覆盖 Intercom 这类使用 default_8MB 的 app-only 固件。

复审结果：

| 固件 | 修复前 | 修复后 |
| --- | --- | --- |
| CardBuddy（Cardputer app-only） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | **`done/SIM_VERIFIED`**（60.1 s，UI 1444 B） |
| Saitama（Cardputer app-only） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | **`done/SIM_VERIFIED`**（60.1 s） |
| Meshtastic ADV（Cardputer-ADV app-only） | `E_APP_ONLY_BASE_REQUIRED` | 可启动并观察；仅 `E_NETWORK_PARTIAL` |
| Intercom（StickS3 app-only） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | 可启动；交互 PASS；仅 `E_NETWORK_PARTIAL` |
| META TV IR（Cardputer app-only） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | 可启动，但 `E_NO_FRAME`（应用/分区仍不匹配） |
| BitMap16 DX（Cardputer app-only） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | 可启动，但 `E_NO_FRAME` |
| Slow Draw（PAPER app-only） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | `E_NO_SIM_PROFILE`，明确说明原版 M5Paper 未建模，不是 app 上下文 |
| K85OS 8.9（StickS3 app-only） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | 仍不支持，但文案明确要求完整镜像/同工具链基底 |

## 关键证据

- 服务提交：`479a852`（错误文案/映射/Cardputer+PaperMono base）、`9e62882`
  （StickS3 default_8MB vendor context）。
- 回归：`python3 -m unittest discover -s tests -v`，**334 项通过**。
- 复审：上述 8 条 saved-snapshot 复跑，均 `submit=false`；旧 attempt 已归档。
- 基底 provenance：
  - Cardputer/ADV：官方 UIFlow2 v2.5.4，8,384,512 B，factory 0x541000；
  - PaperMono：官方 UIFlow2 v2.5.3，16,773,120 B，factory 0x710000；
  - StickS3：default_8MB 前缀，otadata 0xE000，ota_0 0x10000，槽 0x330000。
- 证据摘要：[evidence/app-only-summary.json](evidence/app-only-summary.json)。

## 文件

- `report.md`：完整改动、复审结果与剩余分区问题
- `run.json`：结构化记录
- `evidence/app-only-summary.json`：脱敏后的复审摘要

## 未覆盖项

- K85OS 的自定义 OTA/storage 布局（app 0x20000、otadata 0x10000、storage 0x520000）未做
  vendor context；需要按它的分区表单独构造，通用 base 会“能启动但应用失败”。
- META TV IR / BitMap16 虽然通过启动基底进入应用，但仍无首帧，需按各自构建分区/外设继续排查。
- PaperMono 的 stock base 已配置，但本轮没有匹配的 PaperMono app-only 样本可复验。
- M5GO / Fire / Xiaozhi 仍无模拟器档案；`STICKC` 映射已补，但历史任务无缓存 BIN，无法复跑。
- 物理设备复跑：`NOT RUN`。
