# m5stack/M5Cardputer-UserDemo #48：rich-click/bitarray 报错来自 ESP-IDF 6.1 环境，不是仓库缺陷

- 日期：`2026-11-23`
- 结果：`PASS`（host-level test 复现并解释了两条报错；未做 4.4.6/6.1 实构建）
- 工作类型：`issue_triage`
- 条目：[m5stack/M5Cardputer-UserDemo#48](https://github.com/m5stack/M5Cardputer-UserDemo/issues/48)
  「Doesn't build」，作者 nuncio-bitis，英文，OPEN，0 条评论，无关联 PR
- 源码：`main` `a897c5f2752003dba6d960b572f4c6ec8e71abea`（2026-11-05，PR #47 合并后）
- 环境：macOS arm64，Python 3.13.15；本机有 ESP-IDF 6.1（tag `v6.1`，6.1.0）
- 已发布回复：待填（1 条，英文；issue 仍 OPEN，未 close、未改上游代码）
- 证据等级：**host-level test**（用 ESP-IDF v6.1 自带检查脚本复现两条报错）+
  **code-level verification**（仓库工具链声明、ESP-IDF v6.1/v4.4.6 requirements）
- 未使用虚拟设备验证：失败发生在固件生成之前的本机 Python 环境检查，
  没有任何镜像/串口/画面可跑，Device Service 与 esp-emulator 都不适用

## 结论

1. 这个 issue 不是本仓库的缺陷。`M5Cardputer-UserDemo` 声明并锁定 **ESP-IDF v4.4.6**
   （`README.md:14`、`dependencies.lock:18`），仓库里没有 `install.sh`，也没有任何
   Python requirements 文件（688 个受控文件里都没有）。用户跑的 `install.sh` 是
   ESP-IDF 自己的；失败的检查是 `$IDF_PATH/tools/check_python_dependencies.py`。
2. `rich-click~=1.9.0` 既不在本仓库，也不在 ESP-IDF 4.4.6（它只要 `click>=7.0`）。
   该约束只出现在 **ESP-IDF v6.1** 的官方 constraints 里
   （`espidf.constraints.v6.1.txt:8`，sha256 `fa2846f1…`）。所以被检查的是
   ESP-IDF 6.1 的 Python 环境，而不是本项目要求的 4.4.6 环境。
3. 真正坏掉的包是 `bitarray`：`No package metadata was found for bitarray` 表示
   包目录还在、`.dist-info` 没了（半安装/被覆盖），`importlib.metadata` 看不到它。
   它来自 esptool → `bitstring<5` → `bitarray` 这条依赖链。这个状态重跑检查脚本
   不会自愈，`pip` 也不会主动修。
4. “每次报不同的包丢了”是检查脚本的诊断假象，不是损坏在变化：
   `check_python_dependencies.py` 在依赖树遍历的 except 里（第 176 行）复用了
   直接依赖循环（第 135 行）的 `req` 变量，而需求列表来自 set，顺序每个进程随机，
   所以冒号前打印的包名会变；冒号后的 `bitarray` 才是一直失败的包。
5. 最可能的环境原因：被检查的环境不是 `install.sh` 正在写入的环境——
   `rich-click 1.8.9` 是更老版本 IDF 装出来的，恰好说明它没被 6.1 的 install 更新；
   而 `bitarray` 半安装说明该环境被别的解释器/pip 动过。回复里要求用户补
   `Diagnostic information:` 块（`IDF_PYTHON_ENV_PATH`、`Python interpreter used`）、
   `idf.py --version` 和 `python -V` 来区分“export 了错误 IDF”与“pip 写进了别的解释器”。

## 关键证据

- `evidence/issue-48.json`：issue 状态、作者、0 评论、完整正文（英文原文）。
- `evidence/repo-toolchain.txt`：main SHA、`README.md:14` 的 v4.4.6、
  `dependencies.lock` 的 `idf 4.4.6`、无 `install.sh`/requirements、
  仓库内 `grep rich-click|bitarray` 无命中。
- `evidence/idf-constraints.txt`：ESP-IDF v6.1 官方 constraints 第 8 行
  `rich-click~=1.9.0`（含 sha256/大小）；v6.1 `requirements.core.txt`；
  v4.4.6 `requirements.txt` 只有 `click>=7.0`、无 rich-click。
- `evidence/checker-source.txt`：v6.1 检查脚本 125–185 行，标出第 135/176 行
  的变量复用。
- `evidence/host-repro-idf61-env.txt`：真实 v6.1 环境先 PASS，仅把 rich-click
  降到 1.8.9 后复现第一条报错。
- `evidence/host-repro-bitarray.txt`：去掉 `bitarray` 的 dist-info 后复现
  “Error while checking requirement '…' … No package metadata was found for bitarray”，
  18 次运行中冒号前的名字在 `packaging` / `bitstring` / `rich-click~=1.9.0` 之间变化；
  其中一次与 issue 原文逐字一致。
- `evidence/constraints61.txt`：官方 constraints 原始文件。
- `code/repro.sh`：可重跑的最小复现脚本（只写 `/tmp`，不碰 `~/.espressif`）。

## 未覆盖项

- `idf.py build`（ESP-IDF v4.4.6）：`NOT RUN`。本记录只回答 Python 环境报错，
  没有安装 4.4.6 工具链做完整构建；仓库“能构建”这一点未被本记录证明。
- `idf.py build`（ESP-IDF v6.1）：`NOT RUN`。6.1 不是本项目声明的工具链，
  修好 Python 后是否还能编译属于另一个问题。
- 用户机器环境：`NOT RUN`。没有拿到 `Diagnostic information:` 块、`idf.py --version`、
  `python -V`，因此“哪个环境被检查”是从约束文件和报错反推的，不是直接观测。
- hardware / virtual-device validation：`NOT RUN`，失败早于固件存在。

## 文件

- `README.md`：快速结论与导航
- `report.md`：完整推理、复现步骤、命令与边界
- `run.json`：机器可读记录
- `evidence/`：issue、仓库工具链、IDF 约束、检查脚本、两次主机复现
- `code/repro.sh`：主机复现脚本
