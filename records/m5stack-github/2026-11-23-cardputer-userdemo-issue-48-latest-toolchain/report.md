# 完整报告：M5Cardputer-UserDemo #48 第 3 轮（工具链政策 / “最新工具”要求）

## 1. 问题来源与现象

`m5stack/M5Cardputer-UserDemo#48` 作者 nuncio-bitis 在 2026-11-23T18:21:33Z 追加：

> Building from source shouldn't involve changing the tools from within the source.
> The project should build using the latest version of the tools. If that's not the case,
> then you need to include the tools necessary to successfully build the project.

这是对前一轮回复（ADV 分支按 ESP-IDF v5.4.2 构建、先跑 `fetch_repos.py` 拉 5 个组件）的
原则性反对，包含三个可核查的主张：

1. 从源码构建不应要求改源码内的工具；
2. 项目应能用“最新版本工具”构建；
3. 否则仓库应自带构建所需工具。

## 2. 核查对象与环境

- 仓库：`m5stack/M5Cardputer-UserDemo`，分支 `CardputerADV`，
  commit `9d7190317d49ff87fa98db345b049ed77c5a1780`（2026-11-05）。
- 本机 ESP-IDF：`v6.1`（6.1.0），GCC `xtensa-esp-elf 15.2.0_20251204`，
  Python 3.13.15，venv `idf6.1_py3.13_env`。
- 克隆与组件拉取：`git clone -b CardputerADV --depth 1`，随后 `python3 ./fetch_repos.py`。
- 构建：`idf.py build`（target 由 `sdkconfig.defaults` 的 `CONFIG_IDF_TARGET="esp32s3"` 决定）。

## 3. 事实与证据

### 3.1 仓库没有修改工具链

根目录受控文件仅：`CMakeLists.txt README.md dependencies.lock fetch_repos.py main
partitions.csv repos.json sdkconfig.defaults`。没有 `install.sh`，没有 Python
requirements，没有 `$IDF_PATH` 写操作。

`fetch_repos.py` 的行为（`fetch_repos.py:6-57`）：对 `repos.json` 里每一项
`git clone` / `git fetch` + `checkout <branch>` 到 `components/<name>`，可选
`git apply` 一个补丁。实际数据：

- `repos.json:1-27`：M5GFX `0.2.15`、M5Unified `0.2.10`、mooncake `v2.2.0`、
  mooncake_log `v1.3.0`、smooth_ui_toolkit `v2.4.0`；
- 每条记录都没有 `patch` 字段（`grep -c '"patch"' repos.json` → `0`）；
- `.gitignore` 忽略 `components/` 与 `managed_components/`；
- 拉取后实际版本与 `repos.json` 完全一致（见 `evidence/component-refs.txt`）。

结论：这一步装的是**项目依赖**（git 组件），不是编译器/SDK/pip 包。仓库根 `CMakeLists.txt`
只有 ESP-IDF 项目样板 `include($ENV{IDF_PATH}/tools/cmake/project.cmake)`。

### 3.2 工具链是“声明”而不是“内置”

- `README.md:13-15`：`### Tool Chains` → `ESP-IDF v5.4.2`（链接到 v5.4.2 文档）。
- `dependencies.lock:54-57`：`idf: {source: {type: idf}, version: 5.4.2}`。
- `main/idf_component.yml`：`idf: version: '>=4.1.0'`（无上界）；
  组件依赖 `espressif/esp-now ^2.5.2`、`espressif/esp_tinyusb ^1.1`、
  `jgromes/radiolib ^7.2.1`。

ESP-IDF 是数 GB 的 SDK + 交叉工具链，由用户按版本单独安装并用 `export.sh` 进入 shell，
这是 ESP-IDF 项目的通用契约。仓库用 README + lock file 固定版本，已经属于“声明所需工具”；
把它 vendoring 进仓库既不可行，也会变成另一个 SDK fork。

### 3.3 用“最新工具”（v6.1）构建：第一处失败（configure）

原样 `idf.py build`：

```
-- Building ESP-IDF components for target esp32s3
NOTE: [6/6] idf (6.1.0)
CMake Error at .../tools/cmake/build.cmake:380 (message):
  Failed to resolve component 'usb' required by component
  'espressif__esp_tinyusb': unknown name.
HINT: USB host layer ('usb' component) was removed from ESP-IDF. Please use 'usb'
component from IDF component manager instead.
```

即：IDF 6.x 把 `usb` 组件移出 SDK，`esp_tinyusb 1.7.6~1` 仍按老布局 `REQUIRES usb`。
这与 `fetch_repos.py`、与本仓库源码都无关，是 SDK 大版本不兼容。

### 3.4 补上 `espressif/usb` 后：第二处失败（组件编译）

仅执行 `idf.py add-dependency espressif/usb`（唯一改动，写入 `main/idf_component.yml`），
清空 `build/` 与 `sdkconfig` 后重建，构建推进到 `[1164/1515]` 后失败：

```
FAILED: esp-idf/M5GFX/.../lgfx_qrcode.c.obj
components/M5GFX/src/lgfx/utility/lgfx_qrcode.h:42:23: error: 'bool' cannot be defined via 'typedef'
   42 | typedef unsigned char bool;
      |                       ^~~~
note: 'bool' is a keyword with '-std=c23' onwards
```

失败命令带 `-std=gnu23`（IDF 6.1 默认）。`lgfx_qrcode.h:40-45` 在 `#ifndef __cplusplus`
分支里 `typedef unsigned char bool; static const bool false = 0; ...`，在 C23 下不合法，
且工程开了 `-Werror`，直接失败。该文件来自锁定的 M5GFX `0.2.15`。

因此“用最新工具构建”需要：升级 M5GFX（及核查 M5Unified/mooncake 对 6.x 的兼容）、
在 `main/idf_component.yml` 增加 `espressif/usb`、然后完整构建 + 实机回归。
这是上游组件的移植与验证工作，不是本 issue 回复能完成的修改（本会话也不改上游仓库）。

### 3.5 可选的失败前置

`main/idf_component.yml` 的 `idf: '>=4.1.0'` 无上界，导致 6.x 被接受、错误出现在深层编译。
建议 maintainer 收紧为 `>=5.4.2,<6.0`，让不匹配在 configure 阶段直接报出版本要求。
（建议，未改上游代码。）

## 4. 改动范围 / 兼容性

无上游改动。仅在 `/tmp/cpadv48` 的临时克隆里加了 `espressif/usb` 依赖做第二次构建，
用于确认第二处失败的性质；该临时目录不提交、不推送。

## 5. 执行过程（可重建）

```bash
git clone -b CardputerADV https://github.com/m5stack/M5Cardputer-UserDemo.git /tmp/cpadv48
cd /tmp/cpadv48 && python3 ./fetch_repos.py
. ~/Documents/esp-idf-6.1/export.sh
idf.py build                      # 失败 1：usb 组件（configure）
idf.py add-dependency espressif/usb
rm -rf build sdkconfig
idf.py build                      # 失败 2：M5GFX 0.2.15 lgfx_qrcode.h C23 bool
```

原始日志摘录见 `evidence/idf61-configure-fail.txt`、
`evidence/idf61-compile-fail.txt`。

## 6. 未覆盖项与风险

- 没有 5.4.2 工具链，**未执行**声明工具链的完整构建；“按 README 用 5.4.2 可构建”仍是
  文档声明 + 前一轮的组件布局分析，未在本轮重新证明。
- 6.1 构建在第一个组件错误处停止，后续是否还有更多不兼容未验证（`PARTIAL`）。
- 组件管理器把 `dependencies.lock` 从 2.0.0 升级为 3.0.0 并提示可更新版本，属于工具行为，
  不作为结论依据。
- 没有硬件/虚拟设备验证：失败发生在镜像生成之前。

## 7. 回滚

无仓库改动；删除 `/tmp/cpadv48` 即可清理。
