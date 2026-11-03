# UIFlow 全量复验构建与来源基线报告

## 背景与目标

用户要求更新已合并的模拟器，再由 DeepSeek 执行 UIFlow API 与所有 Unit 的完整复验。主 agent 负责计划、根因判断、修复、独立验收和发布；执行器负责实际测试。本记录固定可公开复建的原生 runtime 与源码/资源身份，作为进行中的功能战役前置里程碑。

固定项目源为 [b41eba70eb61f7ddc5c41e0b981341064f9d1d1f](https://github.com/m5agent/m5stack-esp-emulator/commit/b41eba70eb61f7ddc5c41e0b981341064f9d1d1f)。现有服务/API 的版本号不能证明完整 Unit C 模型已进入二进制，因此未把原有 runtime 或源码更新成功当作功能验收。本轮没有产品源码改动。

## 根因与改动范围

发现的验收缺口是原部署二进制缺少已证明的完整 41 层 Unit 来源链，而不是已经定位的 UIFlow 固件功能缺陷。采用 pristine canonical 基线，在独立源/构建目录应用当前项目补丁并重新构建；不覆盖旧源码、用户资源或原始失败记录。

公共复现从 Espressif QEMU `40edccac415693c5130f91c01d84176ae6008566` 开始，应用 source lock 前 47 个 native 层、额外 10 个 `0110..0119` board 层，再应用 41 个 Unit 层。`0110` 期待的一行空白上下文及 canonical 源的空 `.wraplock` 显式记录；没有改变 C 语义。前 57 层与本地 canonical 标识 `75f1d244d0cf6272b27bb3b3091f3aff71c5f0e1` 的 10,443 个文件、模式和符号链接目标逐项相同。公开复建不依赖该本地对象。准确顺序与公共 pins 见[配方](evidence/public-recipe.md)。

## 执行与证据

原生 Xtensa 编译开始于 `2026-11-03T17:57:09.103300+00:00`，完成于 `2026-11-03T17:57:50.501369+00:00`。以已有专用 libgcrypt/libgpg-error 及宿主 GLib/pixman/slirp 为只读依赖，执行全新 configure 和 QEMU object build；这不是所有依赖 fresh build。配置 target 为 `xtensa-softmmu`，保留 gcrypt/slirp，关闭 GUI 和无关可选后端。1,526 个 Ninja 步骤及 ad-hoc 签名验证完成。

实际签名产物为 **22,207,696 bytes**，SHA-256 `0e16a9bcd86b588dae6b3e3b523dfb8610a9eca37c50c141cce5f2ceb4612068`。原始 build manifest SHA-256 `d70af5cdcba348af28e8954b6d064b4aa9deb1c14e40aa7910f90562b0091b14`；公开摘要仅提取 whitelist 字段。源码清单 SHA-256 `3a8e3a172a1df1d1a6c576c54a73a58ebc1c33007848451c07691da92155d792`，41 个 Unit 补丁每层均完成 forward check 与当层 reverse check。

首次构建 harness 因 archive 源目录继承外层 Git 的路径作用域而跳过早期 patch，随后在 `0138` 处停止，未生成二进制或执行 guest。修正为源目录独立 Git 作用域后，从 pristine 基线重新完整执行。首次失败保留，未用后续成功覆盖其历史。

当前 UI/API 源码基线为固定项目提交，控制器资源 `platform/web/public-session-controller.js` SHA-256 为 `8e845070de279746a3930adec7ca0a58c77bad308d2470f465494e7e1d15b250`，资源与该源码一致。此检查是源/资源身份；不是 guest 或全契约功能证明。内部部署端点、进程、状态及历史配置按归档规则排除在公开记录之外。

## 验收分层

| 层级 | 状态 | 证据与边界 |
| --- | --- | --- |
| build | PASS | 完整 41 层 Unit 原生 Xtensa fresh object build、产物 SHA 与签名核验 |
| source reconstruction | PASS | 公共上游 + native lock + board 层，经显式中性上下文归一，与 canonical 10,443 项零差异 |
| source/asset identity | PASS | 固定项目版本与控制器资源 SHA 一致；不授予功能 PASS |
| flash | PASS（限定三例） | 同一固件 SHA 与运行中 evidence/会话身份匹配；不扩展到其它固件 |
| transport | PASS（限定三例） | GPIO 输入/输出和 ENV III I2C 路径与串口标记对应 |
| device_response | PASS（限定三例） | 官方 constructor/已执行方法及现场控制器状态 |
| data_behavior | PASS（限定三例） | Button raw GPIO 的0/1、Relay on/off/status及ENV III补偿数据随输入变化 |
| visual_or_physical | PARTIAL | 三例均有非空应用帧与精确 SHA；未授完整浏览器视觉或物理属性 PASS |
| delivery | PARTIAL | 本阶段证据已独立核对并归档；全量战役仍在执行 |

## 三项 CoreS3 canary：独立限定验收

主 agent 于 `2026-11-03T18:02:56.268211+00:00` 独立接受三项结果；摘要见 [cores3-canary-summary.json](evidence/cores3-canary-summary.json)。运行时均为本次 `0e16a9bc…12068` 原生构建，分开绑定三份完整固件 SHA、probe SHA、会话别名及 hash、实际输入、串口、应用帧和现场控制器状态。所有 ZIP member 的 SHA/大小、运行中采证、会话/进程/runtime/固件匹配、停止后历史和进程退出均复核通过。

- Button：原始 `ButtonUnit` constructor/ready 成功；通过 Unit input 端点注入 pressed true/false 四次，guest 的独立 `machine.Pin.value()` 产生 `UNIT_BUTTON 0/1`，live controller 记录 4 次输入事件。**不是 ButtonUnit read/callback API 全面可用的证据**，也不是实际浏览器鼠标输入验收。
- Relay：原始 `RelayUnit.on()/off()/get_status()` 产生交替 `UNIT_RELAY 1/0`，live GPIO output-level 两值均观察到，末次控制器记录8次输出转换。没有声称真实触点或负载行为。
- ENV III：原始 `ENVUnit.read_temperature()/read_humidity()/read_pressure()` 经SHT30/QMP6988模型补偿，合成输入 `31.5°C / 67%RH / 98765 Pa` 对应 `UNIT_ENV 31.500 67.000 98765.000`；控制器记录32次事务、66读字节、22写字节。合成 fixture 不等于硬件测量或精度结果。

**仍须补测 ButtonUnit 公共读/查询方法及按下、松开和事件 callback 路径**；不能按 Unit ID 去重，把 constructor + raw Pin canary 计成完整 Button API 覆盖。

三例均为 CoreS3、`runtime=qemu`，只关闭各自准确范围；不转移到其它 Unit、主机或完整 API。全部固件/探针/结果/帧/原始 ZIP/成员及 root audit hash 已在摘要绑定。完整战役仍为 **PARTIAL / in progress**。

## 完整复验的分母与判定

[source inventory](evidence/inventory-scope-summary.json) 是 **REVIEW/provisional**：160 个 catalog row（158 implemented/partial、2 planned/DEFER）及 245 个声明的 host/Unit 组合；principal runner 覆盖 151 个独立 Unit 标识，另有 7 个已映射 implemented 标识需补执行安排。这些不是已执行数或 PASS 数。

API source inventory 包含 system 4,613 项、hardware 460 项、UI 36 surfaces/620 members，widget 28 classes/505 methods。集合彼此重叠，包含常量、可选附件或并非可调用/导出的文档成员，不能相加成为一个全量测试分母。

每个正向功能结果须绑定原始 import/driver/constructor/method、固件 SHA、runtime SHA/profile、会话身份、实际输入、新鲜 guest 输出及控制器/总线数据面。官方驱动缺失时官方 API 可用性记 `NOT RUN`；raw machine 总线交易或候选固件只能证明自己的层级。每个 Unit/API 项最终均须明确 `PASS/PARTIAL/FAIL/NOT RUN/REVIEW`，脚本 exit0 不等于应用 PASS。

## 未覆盖项与风险

本次 canonical 源没有 ESP32-C6 machine，所以 C6 后端、P4/Tab5 与浏览器 WASM 都不能继承该 Xtensa 构建结果。`mini-bps-v11`、`mini-pdm` 两项 DEFER 仍保留。更多固件/主机、跨主机矩阵、长期运行及完整清场证据待当前战役归档。物理 RF、电气、光学、声学和机械行为未执行。

既有浏览器 regular publication Worker 回收及 StackChan 原跳舞启动/独立触摸缺口，仍按[固定项目状态](https://github.com/m5agent/m5stack-esp-emulator/blob/b41eba70eb61f7ddc5c41e0b981341064f9d1d1f/docs/project-status.md)独立跟踪，当前原生构建不关闭它们。

## 回滚与后续

此次以独立新产物供服务显式绑定，旧 runtime、源树和证据保留；需要回退时由操作者恢复原 runtime 绑定，不删除会话历史。功能测试全部经 Device Service 会话执行，先导出 evidence 再停止并保留历史。主 agent 后续核对 DeepSeek 实际回执、失败归因及所有分母，另追加受限功能结果；在此之前不宣称全量验收或任务完成。

本记录不包含二进制、ROM、固件、Flash、构建机路径、端点或唯一设备/会话标识；所有 JSON evidence 均为派生 summary。


## 2026-11-04 后续里程碑：五例 Unit pilot、五板 system 与 HTTP 行为复测

本节追加独立执行与验收，不覆盖前述三项 CoreS3 canary、首次 harness 失败或原始 receipt。全量战役仍为 **PARTIAL / in progress**，并未宣布所有 Unit 或 UIFlow 接口可用。以下均为 **virtual-device validation**；使用相同 `0e16a9bc…12068` 原生 runtime，实际固件、探针和证据包分别绑定完整 SHA。

### 五例追加 Unit pilot

独立复核 SSR、PIR、Ultrasonic-I2C、RGB、Angle 五例的实际输入/输出断言、完整 ZIP 成员哈希/大小、固件与执行身份、先取证后停止、保留历史及同一已绑定进程退出。22 个主要 runner 字节与固定 inventory 一致；五例生成 guest 与原始 probe 共 **67 次文件比较、零差异**。摘要见 [five-case-unit-pilot-summary.json](evidence/five-case-unit-pilot-summary.json)。

| 产品 | 执行 lane | 本次通过的准确范围 |
| --- | --- | --- |
| SSR | stock frozen Unit API | 原驱动 GPIO 输出、两值与转换；无虚构 I2C 事务 |
| PIR | unchanged official-source overlay | 两个 GPIO 边沿、IRQ 禁用和重新启用 |
| Ultrasonic-I2C | unchanged official-source overlay | 初始值和两组变化读回；转换准备、未知命令与 uint24 单位负控 |
| RGB | unchanged official-source overlay | 三灯实际 RMT/GRB 捕获及短帧负控 |
| Angle | unchanged official-source overlay | 原 IDF 曲线拟合微伏、单调性及选定 12-bit ADC transfer |

四例 overlay 保留官方源文件，不能合并为 stock frozen 模块可用性的结论；五例均只授予原 recipe 参数域。没有声称实物 SSR 负载、红外感应、声学距离、LED 光学或 ADC 电气精度。通用 harness 的剩余守卫另保留 REVIEW；五份具体回执已被独立核对，没有用泛化 auditor 的自报 PASS 代替这次核对。

### 五板 system-runtime：250 PASS + 5 STATE_PASS

从五份实际串口逐行重新解析，每板 **50 PASS + 1 STATE_PASS**，合计 **255 个观测行**。这些是已执行断言/调用行，**不是 255 个独立 API**；每次运行有 49 个不同 API 名称，包含重复的文件系统挂载操作，亦不表示全模块或全部参数域覆盖。板型与逐行 recipe/状态见 [five-board-system-runtime-summary.json](evidence/five-board-system-runtime-summary.json)。

| 板型 | PASS 行 | STATE_PASS 行 |
| --- | ---: | ---: |
| CoreS3 | 50 | 1 |
| Cardputer ADV | 50 | 1 |
| StopWatch | 50 | 1 |
| StickS3 | 50 | 1 |
| Core2 | 50 | 1 |

原生 FAT/LittleFS 使用普通 RAM block 接口完成格式化、二进制写读、重挂载、枚举和删除；另有 Flash 文件操作、实际 guest TCP readiness、异常格式化和 UUID 向量等观测。RAM 文件系统不授予 SD 控制器 PASS；随机字节变化不证明密码学质量；UUID 构造不证明 BLE 控制器/RF。五个 `os.dupterm` 均只记 **STATE_PASS（supported）**，不升级为完整 UART detach/reattach 生命周期验证。

CoreS3 首场探针曾额外修改一个仅针对 Core2 的 dupterm 异常判定；实际返回 supported，没有进入该额外异常分支。摘要保留该次真实 source SHA、原始 FAIL receipt 与只读 parser 修正的独立身份，**没有将旧探针换名为后续修正配方，也没有把 receipt 修正当作新固件执行**。

### CoreS3 HTTP：15 PASS + 1 FAIL，保留外层解析缺口

本次实际 `protocol-results` 有 16 行：**15 PASS，1 FAIL**。受控 peer 验证 HTTP 方法、JSON、响应状态/头/正文及文件对象上传；`requests2.urlencode` 的保留字符/UTF-8 form roundtrip 原样失败（观测值 false）。这是准确冻结库、固件和参数域下的行为反例，不由外层退出码推断。证据见 [cores3-http-protocol-summary.json](evidence/cores3-http-protocol-summary.json)。

外层 receipt 原先误报 `NOT_RUN_EMPTY`，并把条件性的 `audio_fixture` / `device_data` 缺省当成 manifest 错误，原始 receipt 的 **FAIL 与 exit 1 原样保留**。独立 ZIP 成员、执行身份、网络证据、取证顺序和进程退出检查与实际 16 行结果分开记录；不能把外层 parser 缺陷写成另一项库缺陷，也不能用后续解析修正覆盖真实 urlencode FAIL。

### 后续边界

本里程碑只追加上述准确结果；先前三例范围、Button 公共读/callback 补测要求、160 catalog 与 245 声明组合的完整分母均保留。其余 Unit、主机组合、系统/网络/UI/硬件 API、候选修复、长期运行与通用 harness 守卫继续独立跟进；原始失败、raw/overlay/stock lane 和未执行项不得互相抵消。公开摘要只保留产品型号、会话/进程别名及内容哈希，删除端点、本机路径、进程编号和原始唯一标识。
