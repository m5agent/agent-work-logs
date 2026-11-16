# m5stack/esphome-yaml#125 — Voice pyramid setup does not work

## 1. 问题来源与现象

Issue: https://github.com/m5stack/esphome-yaml/issues/125（作者 thisspaceleftblank，2026-11-16T19:49:52Z，OPEN）

作者报告两点：

1. 所有 M5Stack 文档都指向 `examples/voice_assistant/echo_pyramid_example.yaml`，该文件已不存在。
2. 被视为替代文件的 `examples/voice_assistant/atoms3r-voice-pyramid-satellite.factory.yaml`
   在 `!include` 语句处产生大量 “File not found”。

Issue 正文没有给出 ESPHome 版本、当前使用的完整 YAML 或完整报错，本轮按最常见两种用法分别复现。

## 2. 仓库与文档事实

`m5stack/esphome-yaml` 当前 HEAD：`f76024e1527b38170350be62c9c01fe29488319d`（2026-11-06）。

提交 `4121c9539089c6b69b3dc55c34bc8d4e6b98aca6`（2026-11-05，
`feat: update voice pyramid configurations`）一次性完成：

- removed `examples/voice_assistant/echo_pyramid_example.yaml`
- added `common/atoms3r-voice-pyramid-satellite.yaml`
- added `examples/voice_assistant/atoms3r-voice-pyramid-satellite.factory.yaml`

文档仓库 `nuxt-m5-docs` 中三套语言版本的最后修改为 `69e9325ed`（2026-09-28），早于上述迁移，
仍保留旧路径：

| 文件 | 行 | 内容 |
| --- | --- | --- |
| `static/en/homeassistant/components/audio/voice_pyramid.md` | 187 | 链接旧文件 |
| `static/ja/homeassistant/components/audio/voice_pyramid.md` | 187 | 链接旧文件 |
| `static/zh_CN/homeassistant/components/audio/voice_pyramid.md` | 187 | 链接旧文件 |
| `static/en/homeassistant/applications/voice_assistant/atoms3r_voice_pyramid.md` | 23, 28 | `packages.files` 使用旧文件 + 链接旧文件 |
| 同上 ja / zh_CN | 23, 28 | 同上 |

应用页同时写着 “ESPHome version `2025.11.3` or later”，与当前配置的
`esphome.min_version: 2026.10.0` 不一致。

线上页面复核（2026-11-16T19:52Z）：`https://docs.m5stack.com/en/homeassistant/components/audio/voice_pyramid`
仍输出 `echo_pyramid_example.yaml` 链接。

## 3. 配置中的 include 结构

`examples/voice_assistant/atoms3r-voice-pyramid-satellite.factory.yaml`：

```yaml
packages:
  va_connected_wait_for_ble:
    ...
  m5stack-atoms3r-voice-pyramid: !include ../../common/atoms3r-voice-pyramid-satellite.yaml

dashboard_import:
  package_import_url: github://m5stack/esphome-yaml/common/atoms3r-voice-pyramid-satellite.yaml@main
```

`common/atoms3r-voice-pyramid-satellite.yaml`：

```yaml
  lcd_variant: st7735
...
display: !include displays/atoms3r-lcd-${lcd_variant}.yaml
```

两个 include 都是相对路径。ESPHome 的 `!include` 相对“发起 include 的文件所在目录”解析，
且只有较新版本才会对路径做变量替换。

## 4. 环境与命令

环境 A（主）：

- macOS
- CPython 3.13.15（uv 管理）
- `uv pip install esphome` → ESPHome 2026.10.2
- `m5stack/esphome-yaml` 克隆于 `$WORK/repo`，HEAD `f76024e`

环境 B（对照）：

- CPython 3.9.6（系统）
- `pip install esphome` → ESPHome 2025.5.2（该解释器可安装的最新版本）

复现目录（`$WORK` 在证据中替代本机临时目录）：

```
$WORK/repo                          # 仓库完整克隆
$WORK/standalone                    # 仅放 factory 文件
$WORK/dashimport                    # 2026.10.2 的 github:// 包配置
$WORK/dashimport/old                # 2025.5.2 的同一条配置
$WORK/docspath-old                  # 文档原样 packages 块（旧路径）
$WORK/docspath-new                  # 文档 packages 块（新 factory 路径）
```

命令：

```bash
# 1) 仓库内直接校验 factory 配置
cd $WORK/repo
$WORK/venv313/bin/esphome config examples/voice_assistant/atoms3r-voice-pyramid-satellite.factory.yaml

# 2) 仅拷贝 factory 文件的独立场景
cd $WORK/standalone
$WORK/venv313/bin/esphome config atoms3r-voice-pyramid-satellite.factory.yaml

# 3) 文档 packages 块：旧路径
cd $WORK/docspath-old && $WORK/venv313/bin/esphome config config.yaml

# 4) 文档 packages 块：新 factory 路径
cd $WORK/docspath-new && $WORK/venv313/bin/esphome config config.yaml

# 5) dashboard_import 等价的 github:// 包：新旧版本各一次
cd $WORK/dashimport && $WORK/venv313/bin/esphome config atoms3r-voice-pyramid.yaml
cd $WORK/dashimport/old && $WORK/venv/bin/esphome config atoms3r-voice-pyramid.yaml
```

`github://` 包配置内容（与工厂 YAML 的 `dashboard_import.package_import_url` 等价）：

```yaml
substitutions:
  name: atoms3r-voice-pyramid
  friendly_name: AtomS3R Voice Pyramid

packages:
  m5stack.atoms3r-voice-pyramid-satellite: github://m5stack/esphome-yaml/common/atoms3r-voice-pyramid-satellite.yaml@main
```

文档原样的 `packages:` 块：

```yaml
packages:
  remote_package_files:
    url: https://github.com/m5stack/esphome-yaml
    files: [examples/voice_assistant/echo_pyramid_example.yaml]
    ref: main
    refresh: 1d
```

## 5. 结果

| # | 场景 | ESPHome | 结果 | 关键输出 |
| --- | --- | --- | --- | --- |
| 1 | 仓库内 factory 配置 | 2026.10.2 | PASS | `INFO Configuration is valid!` |
| 2 | 仅拷贝 factory 文件 | 2026.10.2 | FAIL（预期，用法错误） | `Error including file '../../common/atoms3r-voice-pyramid-satellite.yaml': ... No such file or directory` |
| 3 | 文档 packages 块，旧路径 | 2026.10.2 | FAIL | `examples/voice_assistant/echo_pyramid_example.yaml does not exist in repository.` |
| 4 | 文档 packages 块，新 factory 路径 | 2026.10.2 | PASS | `INFO Configuration is valid!` |
| 5 | `github://.../common/...@main` | 2026.10.2 | PASS | `INFO Configuration is valid!`（外部组件 m5-dev / feat-voice-pyramid / audio-stack 均拉取并校验，动画与音频资源下载成功） |
| 6 | 同 #5 | 2025.5.2 | FAIL | `Error reading file .../common/displays/atoms3r-lcd-${lcd_variant}.yaml: ... No such file or directory` |
| 7 | 实机烧录 / 启动 | — | NOT RUN | 无 Voice Pyramid 硬件 |
| 8 | `esphome compile` | — | NOT RUN | 本轮只验证配置解析 |
| 9 | 虚拟设备 | — | NOT RUN | Device Service 无 Voice Pyramid / Voice Base profile，无对应镜像 |

版本边界补充：对比 ESPHome 各 tag 的 `esphome/yaml_util.py`，`IncludeFile`（带变量替换的
`!include`）在 2026.4.0 出现，2026.3.0 及更早没有。因此 `displays/atoms3r-lcd-${lcd_variant}.yaml`
这类写法在 2026.3.0 及以前会把 `${lcd_variant}` 当字面文件名。该配置自身又声明
`min_version: 2026.10.0`，实际可用下限以 2026.10.0 为准。

## 6. 根因判断

- 作者第一条（文件不存在）成立：文档未随 2026-11-05 的配置迁移更新，旧路径已删除。
- 作者第二条（`!include` 报 File not found）可由两种用法复现：
  1. 把 factory YAML 当独立文件拷入 ESPHome 配置目录 → 相对 `../../common/...` 不存在；
  2. 使用 ESPHome 2026.3.0 及更早版本 → `!include` 路径不做变量替换，找不到
     `atoms3r-lcd-${lcd_variant}.yaml`。
- 在仓库完整布局下，或使用 `packages:` / `github://` 包并配合 ESPHome ≥ 2026.10.0 时，
  当前配置本身可正常解析，未发现配置内容错误。

## 7. 建议（未执行）

- 文档侧：把 en / ja / zh_CN 组件页与应用页的示例路径改为
  `examples/voice_assistant/atoms3r-voice-pyramid-satellite.factory.yaml`，并把最低 ESPHome
  版本改为 2026.10.0。
- 仓库侧（可选）：在 README 或 factory 文件头部注明“factory YAML 依赖仓库相对路径，
  请用 `packages:` 引用，勿单独拷贝”。

## 8. 未覆盖项与风险

- 未在真实 AtomS3R + Voice Pyramid 上烧录启动；音频链路、触摸、RGB、显示均未验证。
- 未执行 `esphome compile`，未生成固件，未验证 C++ 编译与分区/尺寸。
- 未修改任何仓库，未关闭 issue。
- 若作者的 ESPHome 版本 ≥ 2026.10.0 且使用的是文档 `packages:` 块，仍可能因本地缓存或
  自定义文件产生其他错误；已在回复中请其补充版本、完整 YAML 与报错。
