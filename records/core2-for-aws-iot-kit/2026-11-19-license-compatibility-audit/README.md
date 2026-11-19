# Core2-for-AWS-IoT-Kit Issue #108 许可证兼容性核查

- 日期：`2026-11-19`
- 结果：`REVIEW`
- 工作类型：`issue`
- 问题来源：https://github.com/m5stack/Core2-for-AWS-IoT-Kit/issues/108
- GitHub 回复：https://github.com/m5stack/Core2-for-AWS-IoT-Kit/issues/108#issuecomment-7011415744
- 源码版本：`m5stack/Core2-for-AWS-IoT-Kit @ e1c3750e204e714ca62b93f6c20aabd7f7ce286d`
- 环境：macOS，只读仓检视（`git clone --depth 50`）；不涉及设备、固件构建或服务

## 结论

报告指出的方向成立，但依赖面比报告更大，且性质不是"许可证互斥"而是"仓库级授权范围不清"。

- `cryptoauthlib` 不只是 pip 依赖：7 个示例中的 5 个内联了 `components/esp-cryptoauthlib/cryptoauthlib/`
  （Espressif 移植版，内含 Microchip 代码，`version.txt` = `cryptoauthlib-v3.7.9`），每份都保留了
  Microchip 原始 `LICENSE`（5 份文件 sha256 相同）。因此"再分发须附带条款"这一条在文件层面已满足。
- 该组件被编进固件：`Blinky-Hello-World/main/CMakeLists.txt:3`、
  `components/core2forAWS/CMakeLists.txt:36` 都 `COMPONENT_REQUIRES esp-cryptoauthlib`，
  `atecc608.c` 直接 `#include "cryptoauthlib.h"`。MIT 的应用代码静态链接了 Microchip 代码。
- 仓库还内联分发 55 个预编译 `secure_cert_mfg*.bin`。
- 根 `LICENSE` 为 MIT（`Copyright (c) 2020 Amazon Web Services`），既无范围说明，也没有任何
  第三方 `NOTICE`（全树仅 AWS IoT SDK 自带的两个 `NOTICE.txt`）；GitHub `/license` 接口对整仓
  返回 `spdx_id=MIT`。`Blinky-Hello-World`、`Smart-Spaces` 没有本地 LICENSE，读者只能看到根 MIT。
- `requirements.txt:10` 的 `cryptoauthlib==20250916` 是用户侧 `pip install` 拉取，仓库不再分发
  wheel/sdist，属文档缺口而非再分发违规。

正确的最小动作是补第三方声明与限定 MIT 范围，而不是移除依赖；是否接受"带用途限制的宽松许可"
属维护者/法务判断，未在本次核查中定论。

## 关键证据

- `evidence/01-license-artifacts.txt`：根/各示例 LICENSE 头、NOTICE 检索、GitHub 许可证识别。
- `evidence/02-vendored-component.txt`：5 个示例的内联组件与版本、LICENSE 哈希、链接关系、55 个 BIN。
- `evidence/03-pip-dependency.txt`：`requirements.txt` 命中行、4 处 `from cryptoauthlib import *`、
  PyPI sdist 元数据与 `LICENSE.txt` 关键句。
- `evidence/04-upstream-license-clauses.txt`：上游 `license.txt` 三条操作性条款原文（含 permalink）。
- `evidence/06-reply.md`：GitHub 回复原文（英文，与条目语言一致）。

## 文件

- `README.md`：本页
- `report.md`：完整分析、证据链与建议改动
- `run.json`：结构化记录
- `evidence/`：原始命令输出与许可证摘录

## 未覆盖项

- 固件构建 `NOT RUN`：未编译示例，故"组件确实进入最终 BIN"由链接配置推定，未做二进制符号核验。
- 发行渠道 `NOT RUN`：docs/M5Burner 等渠道是否随附 Microchip 条款，无法从本仓库确认；仓库无
  Release 资产，内联 BIN 仅限 vendor 的 provisioning 样例。
- 法务定性 `NOT RUN`：MIT 与"仅限 Microchip 产品使用"的兼容性结论不在本记录范围内。
