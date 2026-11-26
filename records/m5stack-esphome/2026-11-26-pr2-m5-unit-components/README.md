# m5stack/esphome#2 Unit ToF4M / NCIR2 / ACSSR 组件新增评审

- 日期：`2026-11-26`
- 结果：`REVIEW`
- 工作类型：`pr_review`
- 问题来源：https://github.com/m5stack/esphome/pull/2
- 已发布回复：https://github.com/m5stack/esphome/pull/2#issuecomment-7180947997
- 源码版本：`m5stack/esphome @ e8acee5ca547f83e2311f97e8140ef2f6d2da239`（PR head），base `m5-dev @ 6c84e04afe0985a73c705094f88b4f773ed4b6e9`
- 环境：macOS arm64；CPython 3.13 + 仓库 requirements（ESPHome 2026.11.0-dev）；交叉构建工具链 esp32-idf / ESP-IDF 5.5.6；本机 Device Service 的 `cores3` profile（QEMU，16 MB flash，无 PaHub 与 Unit 模型）

## 结论

三个组件（`m5_unit_ncir2`、`m5_unit_acssr`、cherry-pick 的 `vl53l1x`）的寄存器映射与厂商库、两颗 Unit 的内部固件一致，
host 单测 31 项通过，esp32-idf 组件构建通过，PR 正文示例去掉 `relation` 后可在 ESP32-S3 与 CoreS3 上完整编译，
固件可在 CoreS3 虚拟设备上启动到 `setup() finished successfully!`。未发现阻塞性缺陷。

需要在回复中提出的 4 点：

1. **PR 正文示例在本分支不成立**：`esphome: devices:` 的 `relation` 键只在 upstream `esphome/dev` 的
   `DEVICE_SCHEMA` 中存在（upstream 已改为 `cv.Required(CONF_RELATION)`），`m5-dev` 的 schema 没有该键，
   `esphome config` 直接失败；去掉三行 `relation` 后配置有效并完整编译。属分支落后于 upstream + 示例未按本分支校验。
2. **NCIR2 的 YAML 告警/发射率写入未落盘**：`write_settings_()` 只写寄存器，不写 `REG_SAVE_SETTINGS(0x80)`；
   宿主测试证明 0x22 写入生效而 0x80 始终为 0。Unit 掉电重启后从自身 flash 恢复旧值，而 number 实体仍显示 YAML 值。
3. **NCIR2 在 setup() 失败后没有恢复路径**：`mark_failed()` 之后 `update()`/`loop()` 都不再运行（宿主测试证明 Unit 稍后上线也不会恢复）。
   NCIR2 内部固件在 `main()` 里先 `HAL_Delay(500)` + 读 MLX90614 才 `HAL_I2C_EnableListen_IT()`，与 ESP 同时上电时存在竞态；
   同一个作者给 ACSSR 加了 10×1 s 重连窗口，NCIR2 没有。虚拟 CoreS3 上（PaHub 缺失）实测正是这个不对称：
   `m5_unit_ncir2` 被永久标 FAILED，`m5_unit_acssr` 只报警告并继续重试。
4. **次要**：NCIR2 的 buzzer switch 忽略 `restore_mode`（总是发布 Unit 当前状态），ACSSR 的 relay 则按 restore_mode 处理，两者语义不一致；
   另外 ACSSR 的 relay/LED 读回值来自 Unit 固件的影子寄存器（`i2c_slave_update()` 保存主机写入的字节），
   不能证明继电器触点真的闭合——正文的“read back from the unit”需要按这个边界表述。

## 关键证据

- 构建：
  - `script/test_build_components.py -c m5_unit_ncir2,m5_unit_acssr,vl53l1x -t esp32-idf` → 1 passed / 0 failed
  - `esphome compile`（PR 正文示例，去 `relation`）→ esp32-s3-devkitc-1、m5stack-cores3 均 `Successfully compiled program`
  - `firmware.factory.bin` sha256 `df05bb829524901d7d7c538bca4a32225c484f090c0af842fb1b522c790a7d6f`
- 主机单测：`script/cpp_unit_test.py m5_unit_ncir2 m5_unit_acssr vl53l1x` → 31 tests PASSED
- 针对性探针（本轮新增，评审后已从工作树删除）：`LateUnitAfterFailedSetup`、`YamlSettingsAreNotSavedToFlash` 均通过，
  即上面第 2、3 点可复现
- 虚拟设备：`cores3`（QEMU，16 MB flash）启动到 `setup() finished successfully!`；I2C 总线恢复成功、总线扫描列出板载设备；
  三个组件因无 Unit 模型全部走到失败分支 —— NCIR2 `FAILED`、ACSSR 10 次重试后 `warning`、vl53l1x `Boot timeout`
- 代码级核对：NCIR2 地址 0x5A、寄存器 0x00/0x10/0x20/0x30(3 字节步进)/0x40(5 字节步进)/0x50/0x60/0x70/0x80/0x90/0xFE、
  写入长度（发射率 len 3、LED len 4、保存 len 2）与 `M5Unit-NCIR2` 库及 `M5Unit-NCIR2-Internal-FW` 一致；
  ACSSR 0x50、relay 0x00、LED 0x10-0x12、version 0xFE 与 `M5Unit-ACSSR` 库及内部固件一致，
  且 `initial_control()` 确实把 relay 置 0 并延后 3 s 才起 I2C，正文描述属实
- cherry-pick 完整性：`vl53l1x` 5 个文件与 upstream `41c3bbff25cac5a04c96e4820846e9ca94d4574e` 的 blob sha 完全一致，
  `tests/components/vl53l1x/*` 也是同一提交内容

## 文件

- `report.md`：完整报告（命令、发现、边界）
- `run.json`：结构化记录
- `evidence/`：配置校验输出、host 单测与探针输出、虚拟设备串口、构建摘要、探针源码

## 未覆盖项

- 没有 NCIR2 / ACSSR / ToF4M 实体：虚拟设备与硬件均未接入三款 Unit，传感器读数、告警声、继电器带载、Modbus 模式全部 NOT RUN。
- 虚拟设备上 `tca9548a`(PaHub) 与 Unit 均未建模，因此只验证到失败分支，未验证任何 Unit 功能。
- 未验证 Home Assistant 子设备呈现、rtttl 实际音调、Unit 内部 flash 掉电保持。
- 未在实机复核；结论等级为 host-level test + virtual-device validation（仅启动/错误路径）+ code-level verification。
