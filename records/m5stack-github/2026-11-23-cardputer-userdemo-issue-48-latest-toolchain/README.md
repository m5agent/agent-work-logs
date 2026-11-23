# m5stack/M5Cardputer-UserDemo #48 第 3 轮：仓库不改工具链，但用 ESP-IDF 6.1 构建需要上游移植

- 日期：`2026-11-23`
- 结果：`PASS`（在真实 ESP-IDF v6.1 上执行了 configure 与 build，两处失败均可复现；未完成 5.4.2 构建）
- 工作类型：`issue_triage`
- 条目：[m5stack/M5Cardputer-UserDemo#48](https://github.com/m5stack/M5Cardputer-UserDemo/issues/48)
  「Doesn't build」，作者 nuncio-bitis，英文，OPEN
- 被回复评论（2026-11-23T18:21:33Z）：要求“构建不应改源码内的工具；项目应使用最新工具构建，
  否则应把构建所需工具包含在仓库里”
- 源码：`CardputerADV` 分支 `9d7190317d49ff87fa98db345b049ed77c5a1780`（2026-11-05）
- 环境：macOS arm64；ESP-IDF `v6.1`（6.1.0，`~/Documents/esp-idf-6.1`，GCC 15.2.0，
  Python 3.13.15，venv `idf6.1_py3.13_env`）
- 已发布回复：（发布后补）
- 证据等级：**code-level verification（build-executed）**——在真实 v6.1 工具链上执行
  configure/build；没有源码修改，第二次构建只额外添加 `espressif/usb` 依赖
- 未使用虚拟设备验证：两处失败都发生在固件镜像生成之前（configure 阶段与组件编译阶段），
  没有可烧录镜像、串口输出或画面；Device Service / esp-emulator 不适用

## 结论

1. **仓库没有修改工具链。** 根目录只有 6 个受控文件，没有 `install.sh`、没有 Python
   requirements；`fetch_repos.py` 只把项目自己的 5 个 git 组件按 tag 克隆进 `components/`
   （该目录被 `.gitignore` 忽略），不碰 `$IDF_PATH`、不跑 pip、不装编译器；`repos.json`
   里 `patch` 条目数为 0。这是“项目依赖”，不是“工具”。
2. **ESP-IDF 是声明版本而不是内置**：`README.md:15` 写 ESP-IDF v5.4.2，
   `dependencies.lock:54-57` 锁 `idf: 5.4.2`。按 ESP-IDF 生态惯例，SDK 由用户单独安装，
   仓库用文档+锁文件声明版本；把数 GB SDK 塞进仓库不可行，也不是“改源码里的工具”。
   要避免动现有环境，做法是另装一份 5.4.2 并在该 shell 里 export，而不是改全局 IDF。
3. **“用最新工具构建”目前不成立，需要上游移植。** 用 v6.1 原样构建：
   configure 失败，`Failed to resolve component 'usb' required by component
   'espressif__esp_tinyusb'`——IDF 6.x 把 `usb` 组件移出了 SDK（IDF 自己的 HINT 让改用
   组件管理器的 `espressif/usb`）。
4. 只补 `espressif/usb` 后，构建到 `1164/1515` 又在锁定组件里失败：
   `components/M5GFX/src/lgfx/utility/lgfx_qrcode.h:42: 'bool' cannot be defined via 'typedef'`。
   IDF 6.1 的 GCC 15 默认 `-std=gnu23`，`bool` 成了关键字，M5GFX `0.2.15` 的
   `typedef unsigned char bool;` 因此报错。也就是说 6.x 需要同时更新 M5GFX 等第三方组件，
   再跑完整构建与实机回归，属于 maintainer 的移植工作，不是 issue 回复能改的。
5. 可以低成本改善的一点：`main/idf_component.yml` 目前只写 `idf: '>=4.1.0'`，没有上界，
   所以 6.x 会被接受并在深层编译时才炸；改成 `>=5.4.2,<6.0` 能在 configure 阶段就给出
   明确版本错误（建议，未改上游）。

## 关键证据

- `evidence/issue-48.json`：issue 状态、4 条评论、最新评论作者/时间/正文。
- `evidence/repo-toolchain-declaration.txt`：分支/commit、`README.md` v5.4.2、
  `dependencies.lock` 的 `idf: 5.4.2`、`main/idf_component.yml` 的 `idf >=4.1.0`、
  `repos.json` 的 5 个 tag、`patch` 条目 0、`.gitignore` 的 `components/`、根目录文件清单。
- `evidence/component-refs.txt`：`fetch_repos.py` 执行后实际检出的组件版本
  （M5GFX 0.2.15 / M5Unified 0.2.10 / mooncake v2.2.0 / mooncake_log v1.3.0 /
  smooth_ui_toolkit v2.4.0，与 `repos.json` 一致）。
- `evidence/idf61-configure-fail.txt`：v6.1 configure 失败原文（`usb` 组件、HINT）。
- `evidence/idf61-compile-fail.txt`：补 `espressif/usb` 后的 M5GFX C23 `bool` 编译错误、
  `-std=gnu23`、`BUILD_RC=2`。
- `code/repro.sh`：可重跑脚本（克隆分支 → `fetch_repos.py` → v6.1 `idf.py build`）。

## 未覆盖项

- `idf.py build`（ESP-IDF v5.4.2）：`NOT RUN`。本机没有 5.4.2 工具链，所以“声明工具链可构建”
  没有被本记录重新证明。
- 6.1 构建：`PARTIAL`。在第一个组件编译错误处停止，其后可能还有更多 6.x 问题未暴露。
- 6.1 上的依赖解析：lock file 版本 2.0.0 被组件管理器就地升级为 3.0.0，并提示若干组件有新版；
  这不是本轮结论依据，仅作记录。
- hardware / virtual-device validation：`NOT RUN`，失败早于固件存在。

## 文件

- `README.md`：结论与导航
- `report.md`：完整过程、命令、失败原文与边界
- `run.json`：机器可读记录
- `evidence/`：issue、仓库声明、组件版本、两次构建失败日志
- `code/repro.sh`：复现脚本
