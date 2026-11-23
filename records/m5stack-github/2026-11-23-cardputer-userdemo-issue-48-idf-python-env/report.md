# 报告：M5Cardputer-UserDemo#48 "Doesn't build"

## 1. 问题来源与现象

- Issue：<https://github.com/m5stack/M5Cardputer-UserDemo/issues/48>
- 作者：nuncio-bitis；语言：英文；状态：OPEN；评论：0（2026-11-23T17:58:43Z）
- 正文（原文）：

  ```
  The following Python requirements are not satisfied:
  Requirement 'rich-click~=1.9.0' was not met. Installed version: 1.8.9
  Error while checking requirement 'packaging'. Package was not found and is required by the application: No package metadata was found for bitarray

  No amount of running "install.sh" helps. Everytime it's run, a different package goes missing from ESP-IDF
  ```

现象发生在 `idf.py` 启动前的 Python 依赖检查，构建尚未开始，因此没有编译器输出、
没有固件、没有串口或画面。

## 2. 假设与判定

| 假设 | 判定 | 证据 |
| --- | --- | --- |
| H1 仓库缺少依赖声明或 install.sh | 排除 | 688 个受控文件中没有 `install.sh`、没有 Python requirements；`grep rich-click\|bitarray` 无命中 |
| H2 仓库要求更新的 ESP-IDF，与用户工具链不符 | 成立 | `README.md:14` 与 `dependencies.lock:18` 都锁 v4.4.6；`rich-click~=1.9.0` 只属于 v6.1 |
| H3 被检查的 Python 环境是旧的/半损坏的 | 成立 | 1.8.9 是旧约束装出的版本；`bitarray` 缺 `.dist-info` |
| H4 `idf.py` 跑在 `IDF_PYTHON_ENV_PATH` 之外的解释器 | 未确认 | 用户未贴 `Diagnostic information:` 块，脚本会打印该警告 |
| H5 检查脚本的报错包名不可信 | 成立 | 第 176 行复用第 135 行的 `req`，set 顺序随机导致名字每次不同 |

## 3. 根因

### 3.1 工具链版本不匹配

- 仓库 `README.md:14`：`ESP-IDF v4.4.6`；`dependencies.lock:18`：`version: 4.4.6`。
- `flash.sh` 也固定 `IDF_PATH=$HOME/esp/esp-idf-v4.4.6`。
- ESP-IDF v4.4.6 的 `requirements.txt` 只有 `click>=7.0`，没有 `rich-click`
  （`evidence/idf-constraints.txt`）。
- `rich-click~=1.9.0` 只出现在 ESP-IDF v6.1 的官方 constraints
  `https://dl.espressif.com/dl/esp-idf/espidf.constraints.v6.1.txt:8`，
  sha256 `fa2846f1e93ec3e604553a0b8a576a61c47737055360871b7be08523e1e47325`，
  16507 bytes（`evidence/constraints61.txt`）。
- 结论：运行环境是 ESP-IDF 6.1 的工具链；本项目声明的是 4.4.6。

### 3.2 真正失败的包是 bitarray，不是每次打印的那个

`tools/check_python_dependencies.py`（v6.1，sha256 `11b5c8ed…`）：

- 第 135 行 `for req in new_req_list[:]` 只覆盖直接依赖；
- 第 150 行起的 `while new_req_list` 遍历依赖树，第 172–178 行的 except 里
  打印的却是第 135 行留下的 `req`；
- 因此 “Error while checking requirement 'X'” 的 X 是上一次循环的残留值。
  需求集合来自 `set`，字符串哈希每个进程随机，X 每次运行都可能不同。
- 冒号后的异常文本 `No package metadata was found for bitarray` 才是事实：
  `importlib.metadata` 找不到 `bitarray` 的分发包元数据。

`bitarray` 的来源是 esptool → `bitstring<5`（v6.1 constraints 第 32–33 行注释
“bitstring (esptool dependency)”）→ `bitarray`。`bitstring` 4.x 依赖 `bitarray`。

所以“每次丢不同的包”有两种叠加原因：报错名字随机（脚本缺陷），
以及环境里确实有一个半安装的 `bitarray`（`pip` 认为没装、目录却存在，
重跑 `install.sh` 若没有真正作用于该环境就不会修好）。

### 3.3 环境为什么没被 install.sh 修好

直接证据不足，只列可检验的推断：

- `rich-click 1.8.9` 满足 ESP-IDF 6.0 的 `>=1.8.1,<2.0`，不满足 6.1 的 `~=1.9.0`；
  说明该环境是旧约束装出来的，且 `install.sh` 没有把新约束应用到这个环境。
- 常见原因：`$IDF_PATH`/`IDF_PYTHON_ENV_PATH` 指向另一个 IDF 版本或另一个
  Python 环境；或者 `pip` 由 PATH 上的其他解释器执行，写入位置与检查位置不一致。
- 需要用户提供 `Diagnostic information:`（`IDF_PYTHON_ENV_PATH`、
  `Python interpreter used`，以及“not running from IDF_PYTHON_ENV_PATH”警告）、
  `idf.py --version`、`python -V`、`$IDF_PATH` 的 `git rev-parse --short HEAD`
  才能落到具体一种。

## 4. 环境与命令

- 主机：macOS arm64；Python 3.13.15（uv）；本机 ESP-IDF 6.1（tag `v6.1`）。
- 检查脚本：`~/Documents/esp-idf-6.1/tools/check_python_dependencies.py`
  sha256 `11b5c8edc2aaac5854fad759cb4d4ae50ed98ee944b4f5cf8c26725672ddc00e`。
- 复现 A（真实 6.1 环境）：

  ```bash
  python3.13 -m venv /tmp/idf61-repro2
  /tmp/idf61-repro2/bin/pip install -r "$IDF/tools/requirements/requirements.core.txt" \
      -c ~/.espressif/espidf.constraints.v6.1.txt
  IDF_PYTHON_ENV_PATH=/tmp/idf61-repro2 /tmp/idf61-repro2/bin/python \
      "$IDF/tools/check_python_dependencies.py" -r "$IDF/tools/requirements/requirements.core.txt" \
      -c ~/.espressif/espidf.constraints.v6.1.txt          # PASS
  /tmp/idf61-repro2/bin/pip install rich-click==1.8.9
  # 再跑同一检查 -> Requirement 'rich-click~=1.9.0' was not met. Installed version: 1.8.9
  ```

- 复现 B（bitarray 元数据缺失）：

  ```bash
  python3.13 -m venv /tmp/idf61-repro-c
  /tmp/idf61-repro-c/bin/pip install packaging rich-click==1.8.9 bitstring==4.4.0
  SP=$(/tmp/idf61-repro-c/bin/python -c "import sysconfig;print(sysconfig.get_paths()['purelib'])")
  mv "$SP"/bitarray-*.dist-info /tmp/bitarray-dist-info-quarantine   # 只移元数据，模块仍在
  printf 'packaging\nrich-click\nbitstring\n' > /tmp/repro-req.txt
  printf 'rich-click~=1.9.0\n' > /tmp/repro-constraints.txt
  /tmp/idf61-repro-c/bin/python "$IDF/tools/check_python_dependencies.py" \
      -r /tmp/repro-req.txt -c /tmp/repro-constraints.txt
  # 每次输出两行；冒号前的名字在 packaging / bitstring / rich-click~=1.9.0 之间变化，
  # 冒号后的 "No package metadata was found for bitarray" 不变
  ```

- 可重跑脚本：`code/repro.sh`（用 `IDF_PATH`、`PYTHON` 两个变量驱动，只写 `/tmp`）。

## 5. 证据

| 文件 | 内容 |
| --- | --- |
| `evidence/issue-48.json` | issue 元数据与原文 |
| `evidence/repo-toolchain.txt` | main SHA、README/dependencies.lock 的 4.4.6、无 install.sh/requirements、无 rich-click/bitarray |
| `evidence/idf-constraints.txt` | v6.1 官方 constraints 第 8 行、v6.1 core 列表、v4.4.6 requirements.txt、sha256 |
| `evidence/constraints61.txt` | 官方 constraints 原始文件 |
| `evidence/checker-source.txt` | v6.1 检查脚本 125–185 行与行号说明 |
| `evidence/host-repro-idf61-env.txt` | 复现 A 完整输出（PASS → 降级 → FAIL） |
| `evidence/host-repro-bitarray.txt` | 复现 B：18 次运行的包名随机化，含与原文一致的一次 |
| `code/repro.sh` | 最小复现脚本（已执行，退出 0） |

## 6. 回复策略

- 语言：英文（issue 标题/正文均为英文）。
- 结构：结论 → 证据等级（host-level test + code-level verification）→
  机制与修复命令 → 未覆盖项；不关闭 issue、不改上游代码。
- 修复建议：
  1. 先打印 `idf.py --version`、`$IDF_PATH` 的 commit、`$IDF_PYTHON_ENV_PATH`、
     `command -v python`、`python -V`；
  2. 删除诊断块里给出的那一个环境目录（先判空），从同一个 IDF checkout 重跑
     `./install.sh esp32s3`（Windows 为 `install.bat`）并 `source export.sh`；
  3. 本项目用 v4.4.6：`git clone -b v4.4.6 --recursive ...` 后重新安装再 `idf.py build`；
  4. 若仍失败，请贴诊断块与版本信息，用于区分“export 错 IDF”与“pip 写错解释器”。
- 明确写：没有在 6.1 下构建本项目；6.1 不是声明工具链，后续报错属于另一个问题。

## 7. 未覆盖项与风险

- `NOT RUN`：ESP-IDF v4.4.6 完整构建（未安装 4.4.6 工具链，仓库可构建性未证明）。
- `NOT RUN`：ESP-IDF v6.1 下构建（非声明工具链）。
- `NOT RUN`：用户机器复现；未取得诊断块，环境归因是反推。
- `NOT RUN`：hardware / virtual-device validation；失败早于固件存在。
- 风险：若用户其实已在 4.4.6 环境里操作，那么 `rich-click~=1.9.0` 不可能出现，
  说明其 shell 里 `idf.py`/`$IDF_PATH` 指向 6.1——回复里的第一条命令就是让这一点显式化。
