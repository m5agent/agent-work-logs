# m5stack/esphome-yaml#125 Voice pyramid setup does not work

- 日期：`2026-11-17`
- 结果：`PARTIAL`
- 工作类型：`issue`
- 问题来源：https://github.com/m5stack/esphome-yaml/issues/125
- 源码版本：`m5stack/esphome-yaml @ f76024e1527b38170350be62c9c01fe29488319d`；相关删除提交 `4121c9539089c6b69b3dc55c34bc8d4e6b98aca6`
- 环境：macOS；uv 管理的 CPython 3.13.15 + ESPHome 2026.10.2（pip wheel）；对照环境 CPython 3.9.6 + ESPHome 2025.5.2。未接入硬件，未使用虚拟设备。

## 结论

报告属实，根因在文档与配置的组合方式，不在 Config 内容本身：

1. 文档（en / ja / zh_CN 的 Voice Pyramid 组件页与应用页）仍指向 2026-11-05 已删除的
   `examples/voice_assistant/echo_pyramid_example.yaml`，且仍写“ESPHome 2025.11.3 或更高”。
   当前配置声明 `min_version: 2026.10.0`。
2. `atoms3r-voice-pyramid-satellite.factory.yaml` 不是独立文件：它用
   `!include ../../common/atoms3r-voice-pyramid-satellite.yaml` 引用同仓库文件，被引用的
   common 文件又用 `!include displays/atoms3r-lcd-${lcd_variant}.yaml` 引用同目录子目录。
   只把 factory 文件拷进 ESPHome 配置目录必然报 File not found。
3. `!include` 路径中的 `${lcd_variant}` 替换需要 ESPHome 2026.4.0 及以上（2026.3.0 及以前
   会把字面量当作文件名），而该配置本身要求 2026.10.0。

按仓库布局直接校验、以及把文档里的 `packages:` 块文件路径换成新 factory 文件（ESPHome
2026.10.2）均得到 `Configuration is valid!`。文档尚未修改，实机未运行，故整体为 PARTIAL。

## 关键证据

- 仓库内校验：`esphome config examples/voice_assistant/atoms3r-voice-pyramid-satellite.factory.yaml`
  → `INFO Configuration is valid!`（2026.10.2）
- 文档旧路径：文档中的 `packages.files: [examples/voice_assistant/echo_pyramid_example.yaml]`
  → `examples/voice_assistant/echo_pyramid_example.yaml does not exist in repository.`
- 文档新路径：同一 `packages:` 块改为新 factory 文件 → `Configuration is valid!`
- 独立拷贝：只保留 factory 文件 → `Error including file '../../common/atoms3r-voice-pyramid-satellite.yaml': ... No such file or directory`
- 版本差异：`github://m5stack/esphome-yaml/common/atoms3r-voice-pyramid-satellite.yaml@main`
  在 2026.10.2 通过；在 2025.5.2 报
  `common/displays/atoms3r-lcd-${lcd_variant}.yaml: No such file or directory`

## 文件

- `report.md`：完整报告（含命令、版本、判断边界）
- `run.json`：结构化记录
- `evidence/`：ESPHome CLI 原始输出（已把本机临时目录替换为 `$WORK`）与文档/仓库历史摘录

## 未覆盖项

- 未烧录、未在 AtomS3R + Voice Pyramid 实机上启动；音频、触摸、RGB、显示行为均未验证。
- 未执行 `esphome compile`，因此 C++ 编译与固件产物未验证；本轮只做配置解析与组件 schema 校验。
- 未修改文档仓库；文档链接与最低版本号的修复待文档侧处理。
- 本机 Device Service 无 Voice Pyramid / Voice Base profile，无对应固件镜像，故未做虚拟设备验证。
