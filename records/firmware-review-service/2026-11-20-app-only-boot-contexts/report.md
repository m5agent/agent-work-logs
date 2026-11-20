# 完整报告：app-only 启动上下文、错误文案与设备映射修复

## 1. 现象

2026-11-16 至 11-20 共 11 条 app-only 相关错误：

| 错误码 | 数量 | 设备 / 固件 |
| --- | --- | --- |
| `E_APP_ONLY_UNSUPPORTED_DEVICE` | 8 | Cardputer ×5（Saitama、CardBuddy、META TV IR ×2、BitMap16 DX）；StickS3 ×2（Intercom、K85OS 8.9）；Paper ×1（Slow Draw） |
| `E_APP_ONLY_BASE_REQUIRED` | 2 | Cardputer-ADV Meshtastic ×2 |
| `E_APP_ONLY_TARGET_MISMATCH` | 1 | Cardputer-ADV Micropython editor（应用 16 MB，设备 8 MB） |

这些 BIN 只含应用分区，不含 bootloader/分区表。审查服务需要“设备+启动基底”都验证过才会
自动组合；此前 `app_boot_bases` 为空，`STOCK_BOOT_RECIPES` 只有 `cardputer-adv` 和
`core2`，`app_vendor_boot_contexts` 只绑定了 EMBER 和 2048 两个具体应用哈希。

## 2. 改动

### 2.1 错误文案

`service/firmware_intake.py`：

- `E_APP_ONLY_UNSUPPORTED_DEVICE`：
  `该 BIN 仅含应用分区，没有 bootloader/分区表；当前 {device} 没有已验证的启动基底。请上传完整合并镜像，或提供同工具链的 bootloader+分区表启动基底。`
- `E_APP_ONLY_BASE_REQUIRED`：
  `该 BIN 仅含应用分区，没有 bootloader/分区表；{device} 已有启动 recipe，但尚未配置已验证的启动基底。请上传完整合并镜像，或配置同型号启动基底。`
- `E_APP_ONLY_TARGET_MISMATCH`：
  在原有芯片/Flash 信息后加 `这是构建目标与设备不匹配，不是启动上下文缺失。`
- `firmware-intake.json` 增加 `device_id` 和
  `requires=full_flash_image_or_toolchain_boot_context`，UI 可直接提示需要完整烧录包。

`service/app.py` 的 `E_NO_SIM_PROFILE` 文案也改为“当前模拟器没有该设备的可用档案”，并附加
具体原因（如原版 M5Paper、Xiaozhi、M5GO、Fire）。

### 2.2 设备映射

- 新增 `STICKC`/`M5STACK_STICKC` → `stickc`，`M5STICK` → `m5stick`；
- 移除 `PAPER`/`M5STACK_PAPER` → `papermono`。原版 M5Paper 是 ESP32 classic，
  PaperMono 是 ESP32-S3；混用会让应用在错误的芯片目标上被拒绝；
- 新增 `UNSUPPORTED_DEVICE_REASONS`，为 `PAPER`、`XIAOZHI_CARD_KIT`、`M5GO`、`FIRE`
  给出明确原因，不再只显示 `no emulator profile`。

### 2.3 启动基底

| 设备 | 基底 | 版本/布局 |
| --- | --- | --- |
| `cardputer` / `cardputer-adv` | 官方 UIFlow2 v2.5.4 Cardputer 8 MB 镜像 | 8,384,512 B；factory 0x10000，槽 0x541000 |
| `papermono` | 官方 UIFlow2 v2.5.3 PaperMono 16 MB 镜像 | 16,773,120 B；factory 0x10000，槽 0x710000 |
| `sticks3` | default_8MB boot prefix | 65,536 B；otadata 0xE000，ota_0 0x10000，槽 0x330000 |

`STOCK_BOOT_RECIPES` 新增 `cardputer`、`papermono`、`sticks3`；`cardputer-adv` 复用
Cardputer 8 MB 配方。运行时 `app_boot_bases` 配置 `cardputer`/`cardputer-adv`/`papermono`；
StickS3 通过 `app_vendor_boot_contexts` 绑定 Intercom 的 app SHA，使用 default_8MB
vendor context（OTA 选择器哈希 `f94c5d78…` 与既有 `_ARDUINO_BOOT_APP0_SHA256` 一致）。

## 3. 复审结果

| 任务 | 固件 | 修复前 | 修复后 | 说明 |
| --- | --- | --- | --- | --- |
| `job-3937ca75e53d` | CardBuddy（Cardputer） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | `done/SIM_VERIFIED` | 60.1 s，UI 1444 B |
| `job-7332bee8ee00` | Saitama（Cardputer） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | `done/SIM_VERIFIED` | 60.1 s |
| `job-d40fa9a90c9b` | Meshtastic（Cardputer-ADV） | `E_APP_ONLY_BASE_REQUIRED` | `E_NETWORK_PARTIAL` | 已启动/观察；只剩网络 |
| `job-4de071397ee7` | Intercom（StickS3） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | `E_NETWORK_PARTIAL` | 已启动；交互 PASS；只剩网络 |
| `job-ea619c05e10b` | META TV IR（Cardputer） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | `E_NO_FRAME` | 已启动但无首帧 |
| `job-1dd264165cf2` | BitMap16 DX（Cardputer） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | `E_NO_FRAME` | 已启动但无首帧 |
| `job-0b91a054ce39` | Slow Draw（PAPER） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | `E_NO_SIM_PROFILE` | 明确“原版 M5Paper 未建模” |
| `job-d4c72ab5225a` | K85OS 8.9（StickS3） | `E_APP_ONLY_UNSUPPORTED_DEVICE` | 仍不支持（新文案） | 需要完整镜像/同工具链基底 |

## 4. 为什么不是所有设备都能“套一个 base”

K85OS 的分区表（来自其仓库 `partitions.csv`）是：

```text
nvs       0x9000   0x6000
phy_init  0xf000   0x1000
otadata   0x10000  0x2000
ota_0     0x20000  0x280000
ota_1     0x2A0000 0x280000
storage   0x520000 0x2E0000
```

应用在 `0x20000`，还需要 `storage` LittleFS。用 default_8MB/官方 Cardputer 的 factory
基底会出现“能启动但 `partition "storage" could not be found`，应用退出”的假失败。因此
K85OS 需要按它的分区表单独构造 vendor context（app_offset 0x20000、otadata 0x10000、
额外 storage 分区），不能复用通用 base。

META TV IR / BitMap16 虽然通过 Cardputer base 进入应用，但仍无首帧；这更可能是各自
构建分区或外设需求不匹配，不是启动上下文缺失。需要按应用继续定位，不能直接判固件失败。

## 5. 部署与回滚

- 代码提交：`479a852`（文案/映射/Cardputer+PaperMono base）、`9e62882`
  （StickS3 default_8MB vendor context），均已推送 `main`。
- 常驻服务：仓库当前 `main` 与运行时并非同一分支；本轮按相同逻辑同时修正仓库与运行时，
  并在运行时重启后验证 `/api/health` 正常。部署前保留 `app.py`/`firmware_intake.py`/
  `config.json` 备份。
- 复审均为 saved-snapshot、`submit=false`；未回传 Burner，未修改模拟器仓库。
- 回滚：恢复备份文件并重启；或 revert 上述提交后重新部署。

## 6. 未覆盖项

- K85OS 自定义 OTA/storage vendor context：`NOT RUN`。
- META TV IR / BitMap16 无首帧的应用/分区定位：`NOT RUN`。
- PaperMono stock base 的匹配 app-only 样本：`NOT RUN`（本轮无匹配样本）。
- M5GO / Fire / Xiaozhi 机型档案：`NOT RUN`；`STICKC` 历史任务无缓存 BIN，未复跑。
- 物理设备复跑：`NOT RUN`。
