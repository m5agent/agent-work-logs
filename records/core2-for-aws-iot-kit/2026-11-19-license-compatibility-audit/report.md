# Core2-for-AWS-IoT-Kit Issue #108：与上游 cryptoauthlib 的许可证兼容性

## 1. 背景

外部报告（`LicenseProliferation`，2026-11-19）提出：本仓库根 `LICENSE` 为 MIT，但
`Blinky-Hello-World/utilities/AWS_IoT_registration_helper/requirements.txt:10` 声明
`cryptoauthlib==20250916`；后者的上游 `MicrochipTech/cryptoauthlib` 根 `license.txt` 规定
"仅可随 Microchip 产品使用"。报告的结论是 MIT 与该方法律条款不兼容：MIT 未带用途限制，
若单独适用即等于允许在其他硬件上使用，并会遗漏 Microchip 要求的限制条款。

同时，报告称依赖关系来自 GitHub Dependents 页面（运行时索引），未展开仓库内部结构。

## 2. 目标与验收层级

- 目标：判断"MIT 根许可 + Microchip 依赖"是否构成许可证缺陷；若是，给出可执行的最小修正。
- 验收层级：`review`（静态授权分析）。`build` / `flash` / `transport` / `device_response` /
  `data_behavior` / `visual_or_physical` 对该问题不适用——许可证结论不由运行行为决定，
  故未启动 Device Service、QEMU 或实机。

## 3. 取证

全部证据见 `evidence/`，命令在 `e1c3750` 的 `--depth 50` 检出上重跑得到。

### F1 根许可为 MIT，且无范围说明、无第三方 NOTICE

```
LICENSE:2  The MIT License (MIT)
LICENSE:4  Copyright (c) 2020 Amazon Web Services
```

全树 `find -iname '*NOTICE*'` 仅命中 AWS IoT SDK 自带的两份（`esp-aws-iot/aws-iot-device-sdk-embedded-C/NOTICE.txt`），
没有任何覆盖 `esp-cryptoauthlib` 的归集文件。GitHub `/license` 接口：
`spdx_id=MIT path=LICENSE name=MIT License`——平台侧将整仓标注为 MIT。

### F2 依赖是内联的，不限于 `requirements.txt`

5 个示例（`Blinky-Hello-World`、`Factory-Firmware`、`Getting-Started`、
`Hardware-Features-Demo`、`Smart-Thermostat`）各带一份
`components/esp-cryptoauthlib/cryptoauthlib/`，`version.txt` 均为 `cryptoauthlib-v3.7.9`。
该目录是 Espressif 的 `esp-cryptoauthlib` 移植（其 README 自述为 Microchip `cryptoauthlib` 的子集），
每份都保留 Microchip `LICENSE`（文件头 `(c) 2015-2023 Microchip Technology Inc.`，
5 份 sha256 全为 `17f8ada09570f01b9e2c3c995f220fce01ffb61c6b8c0199f6f6ac2f355cd7d2`）。

含义：Microchip 许可的再分发条款（须随附条款与免责声明）在**源文件层面已满足**；
缺陷不在"漏发许可证文件"，而在仓库顶层没有把这些第三方条款汇总声明出来。

### F3 组件被编入固件

```
Blinky-Hello-World/main/CMakeLists.txt:3
  set(COMPONENT_REQUIRES "nvs_flash" "esp-aws-iot" "esp-cryptoauthlib" "core2forAWS")
Blinky-Hello-World/components/core2forAWS/CMakeLists.txt:36
  list(APPEND COMPONENT_REQUIRES "esp-cryptoauthlib")
```

`components/core2forAWS/core2forAWS.h` 与 `atecc608/atecc608.c` 均 `#include "cryptoauthlib.h"`。
即 MIT 声明的应用代码静态链接了 Microchip 代码，产物是"MIT + 带用途限制的第三方代码"的混合体。

### F4 仓库内联分发预编译 BIN

`find . -path '*/esp_cryptoauth_utility/sample_bins/*.bin'` 共 55 个（5 个示例 × 11 个目标），
例如 `sample_bins/esp32/secure_cert_mfg_esp32.bin`。二进制再分发同样触发 Microchip 条款的随附义务。

### F5 pip 依赖：文档缺口而非再分发

`requirements.txt:10` = `cryptoauthlib==20250916`，被 4 个文件 `from cryptoauthlib import *`
（`trustplatform/common_helper.py:5`、`certs_handler/create_cert_defs.py:30`、
`manifest_helper/tng_manifest_helper.py:25`、`manifest_helper/tflx_manifest_helper.py:26`）。

仓库不含该 wheel/sdist，安装由用户侧 `pip install -r` 完成。核验该固定版本的实际发行物
（`cryptoauthlib-20250916.tar.gz`，sha256 `c73272d6…`）：`PKG-INFO` 为 `License: Other` /
`License :: Other/Proprietary License`，其 `LICENSE.txt`（sha256 `ddab06e5…`）写明
"You may use this software and any derivatives exclusively with Microchip products."
因此该行确有"引入受限许可依赖且未在仓库层面告知"的问题，但性质是文档缺口。

### F6 示例之间的许可本身已不一致

| 路径 | 头两行 | 归属 |
| --- | --- | --- |
| `Getting-Started/LICENSE` | Apache License 2.0 | 示例级 |
| `Smart-Thermostat/LICENSE` | Apache License 2.0 | 示例级 |
| `Alexa_for_IoT-Intro/LICENSE` | ESPRESSIF MIT License（同样带"仅限 Espressif 产品"） | 示例级 |
| `Hardware-Features-Demo/LICENSE.md` | MIT, M5Stack | 示例级 |
| `Factory-Firmware/LICENSE.md` | MIT, AWS | 示例级 |
| `Blinky-Hello-World/`、`Smart-Spaces/` | 无本地 LICENSE | 落到根 MIT |

同仓已存在另一种"带用途限制的 MIT"（Espressif），说明"用途限制型宽松许可 + 根 MIT"的结构性
问题并非 cryptoauthlib 独有；也说明单点补一条说明不足，需要一份统一的第三方清单。

## 4. 对报告结论的判定

| 报告论点 | 判定 | 依据 |
| --- | --- | --- |
| 仓库依赖 cryptoauthlib | 成立，且比报告描述更广（内联 + 链接 + BIN），不只是 `requirements.txt` | F2/F3/F4 |
| 上游许可含"仅限 Microchip 产品" | 成立（"use ... exclusively with Microchip products"） | `evidence/04` |
| 下游以 MIT 提供 | 成立（根 MIT + GitHub 判定整仓 MIT） | F1 |
| 二者"不兼容"、MIT 单独适用会遗漏限制 | 部分成立：属授权范围/条款披露缺陷，而非版权式互斥 | 见下 |

关键区分：Microchip 许可是"宽松 + 用途限制"，不是 copyleft。两种许可可以在同一仓库共存，
各自约束各自代码；只要随附 Microchip 条款（F2 已做到），再分发即合规。真正的风险是
**根 MIT 未限定范围**：读者（含 GitHub 平台与下游打包者）会把整仓当 MIT，从而误认为可以把
Microchip 代码用于非 Microchip 硬件、或省略该限制——这是 MIT 无权授予的，也正是报告要指出的
误导。`requirements.txt` 一行不构成再分发，但同样没有告知。

## 5. 建议的最小修正（未在本仓实施）

本任务授权为只读核查 + 单条回复，未改动对方仓库、未推送分支。建议维护者：

1. 新增根 `NOTICE` / `THIRD_PARTY_LICENSES.md`，至少列出：内联 `esp-cryptoauthlib` v3.7.9
   （Microchip 许可 + 用途限制）、55 个 `sample_bins/*.bin`、pip `cryptoauthlib==20250916`，
   并指向各示例自带的 LICENSE。
2. 在根 `LICENSE` 增一句范围说明：MIT 仅覆盖一方代码，除组件自带许可者外。
3. README 增加示例级许可一览表，消除 F6 的不一致（可同时覆盖 Apache-2.0 与 Espressif MIT）。
4. 可选：在 `AWS_IoT_registration_helper` 的安装说明中提示该依赖的许可与用途限制。

改动面仅文档，无 API、构建或行为影响；回滚即删除新增文件与那一句范围说明。

## 6. 未覆盖项与风险

- `build` `NOT RUN`：未编译示例；"组件进入最终 BIN"由 `COMPONENT_REQUIRES` 与 `#include`
  推定，未做产物符号/字符串核验。
- 发行渠道 `NOT RUN`：本仓无 Release 资产，docs/M5Burner 等渠道是否随附条款无法从源码确认。
- 法务定性 `NOT RUN`：是否接受用途限制型许可、以及在 ESP32（非 Microchip 芯片）上搭配
  ATECC608 是否满足"exclusively with Microchip products"，属维护者/法务判断，本记录不下结论。
- 历史 `NOT RUN`：`--depth 50` 浅克隆，未追溯该组件引入时间与历次 LICENSE 变更。
