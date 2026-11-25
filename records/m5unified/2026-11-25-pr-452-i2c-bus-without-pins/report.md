# M5Unified #452 只读评审报告

## 1. 条目与背景

| 项 | 值 |
| --- | --- |
| 条目 | https://github.com/m5stack/M5Unified/pull/452 |
| 标题 | I2C_Class: a bus without pins does nothing; isEnabled() means it has pins |
| 作者 | ainyan03 |
| 状态 | OPEN，非 draft，MERGEABLE/CLEAN |
| head | `17fc0aecacad235037a1e68a4f5f90c5e3860dbd`（`i2c_bus_without_pins`） |
| base | `0ca3a4374766e1d09a92342e811bbffb2b991502`（develop，含已合并的 #451） |
| 规模 | 4 文件 +24/-5：`M5Unified.hpp`、`M5Unified.inl`、`I2C_Class.hpp`、`I2C_Class.inl` |
| 语言 | 英文（标题与正文），回复使用英文 |

这是 #451 的后续。`I2C_Class` 用两种方式表示“本板没有这条总线”：

- 外部 I2C 引脚缺失时 `Ex_I2C` 停在初始 port `-1`；
- 内部 I2C 引脚缺失时 `In_I2C` 被 `setPort(I2C_NUM_MAX, …)`。

旧 `isEnabled()` 是 `_port_num >= 0`，于是第一种情况返回 false（但 `begin()` 没有护栏），
第二种情况返回 true。PR 把 `isEnabled()` 改成看引脚，并给 `I2C_Class` 的每个总线操作加护栏。

## 2. 改动面逐条核对（code-level）

| 声明 | 源码位置 | 核对结果 |
| --- | --- | --- |
| `isEnabled()` 只看引脚 | `src/utility/I2C_Class.hpp:136` `_pin_sda >= 0 && _pin_scl >= 0` | 成立；`setPort()`/`begin(port,sda,scl)` 之外的路径不会写引脚，默认 -1 |
| 每个调用在 `!isEnabled()` 时不动总线 | `I2C_Class.inl:34,40,46,52,58,64,70,76,82,91,97,103,109,115` | 成立；`scanID(addr)` 走 `start() && stop()`、`scanID(bool*)` 走前者，均被覆盖；`readRegister8` 返回 0 与其他错误路径一致（`value_or(0)`） |
| `M5.begin()` 里的 Ex 检查改用 `isEnabled()` | `M5Unified.hpp:533`；`M5Unified.inl:2886,2891,2895,2911` | 成立；`ex_i2c_sda/scl/port` 保留给 M5Unit 显示头，`(void)` 抑制未使用告警 |
| 负端口 + 有效引脚也算启用 | 同上 | 成立（与 M5GFX `isSoftPort()` 的负端口语义一致） |
| PC 构建下 `begin()` 返回 false | `lgfx/v1/platforms/sdl/common.hpp` 的 `i2c::init()` 恒 `return {}` | 由源码可得；本轮未构建 PC 目标 |
| 无用代码 | `M5Unified.inl:2885` 之后删除的两行注释 | 与新语义相符，属清理 |

补充检查：

- 55 行 `_pin_table_i2c_ex_in`（`evidence/pintable-consistency.txt`）中 SDA/SCL 都是成对置空，
  所以“引脚成立但端口是 `I2C_NUM_MAX`”这种误判组合目前不可达。
- 仓库内没有其他直接调用 `m5gfx::i2c::*` 绕过 `I2C_Class` 的路径会用到 `In_I2C`/`Ex_I2C` 的端口；
  `in_i2c_bulk_write()` 只经 `I2C_Class::writeRegister`，同样受护栏保护。
- `examples/` 与 `docs/` 中没有任何 `Ex_I2C.begin()` 用法，因此示例无需随语义调整。

## 3. 运行时验证（virtual-device validation）

### 3.1 方法

- 用同一份探针固件（`code/probe-main.cpp`）链接两个 M5Unified 版本：develop
  `0ca3a43`（pre）与 PR head `17fc0ae`（post）。除 `BUILD_TAG` 字符串外源码完全相同。
- 探针在 `app_main` 创建的 16 KB 任务里执行：`M5.begin()` → 打印板号/`M5.begin` 耗时/
  `In_I2C`、`Ex_I2C`、`Rtc`、`Imu` 的 `isEnabled()` → 对 `Ex_I2C`、`In_I2C` 和一个默认构造的
  `I2C_Class` 依次做 `begin()`、112 地址 `scanID()`、`readRegister8(0x51,0x02)`，并逐项打印。
  探针在 `M5.begin()` **之后**才动 `Ex_I2C`，正好对应 PR 描述里 “`M5.Ex_I2C.begin()` in a sketch”。
- 镜像：ESP-IDF v6.1、esp32s3、8 MB dio，bootloader `0x0` / 分区表 `0x8000` / app `0x10000`
  合并成单镜像后由本机 Device Service 导入（`artifact` → `firmware/import` → `sessions`），
  串口按 offset 增量读取，`M5SW_I2C_TRACE=1` 打开会话级 I2C 追踪。
  镜像 SHA256 与构建差异见 `evidence/build-summary.txt`。
- 设备：`paperdiy`（board 34，无 Grove/外部 I2C 引脚）、`cardputer`（board 14，无内部 I2C 引脚）、
  `sticks3`（board 26，两总线都有，作为对照）。profile 摘录见 `evidence/device-profiles.txt`。
- 每个会话读完 `MARK_DONE` 后立即 `DELETE /sessions/{id}`，不留常驻会话。

### 3.2 结果

见 README 的对照表。要点：

1. `paperdiy`：`Ex_I2C` 的 `begin()` 在 pre 返回 **1** 且随后 112 地址扫描花了 **107 ms**；
   post 返回 **0**、扫描 **0 ms**。`In_I2C`（port 1，G41/G42）在两边都 `begin()=1`，
   扫描都能命中 0x6E（78/79 ms），说明护栏没有波及真正的内部总线。
   这正是 #451 评审里记录的现象（当时实测 `ret=1`），本 PR 把它关掉。
2. `cardputer`：`In_I2C` 状态为 `port=2 / sda=-1 / scl=-1`。pre 的 `isEnabled()` 仍是 **1**，
   `M5.begin()` 因此在一条不存在的总线上探测 RTC/IMU，`begin_ms=2165`；post 为 **0**，
   探测被跳过，`begin_ms=1875`。方向与作者硬件表里的 −61 ms 一致，量级差异来自虚拟设备
   不模拟真实 I2C 超时。
3. `sticks3` 对照：`In_I2C(47/48)`、`Ex_I2C(9/10)` 都保持 `isEnabled()=1`、`begin()=1`，
   内/外扫描分别命中 3/4 个地址，`Imu.isEnabled()=1`、`displays=1`。语义收紧没有回退正常板型。
4. 默认构造的 `I2C_Class`（port -1、无引脚）在三块板上都从 `begin()=1` 变为 `0`。

### 3.3 证据边界

- QEMU 不建模 GPIO 矩阵/引脚复用，所以“内部总线引脚被软件 I2C 抢用后电气上会发生什么”
  没有被复现；能证明的是**这些引脚上确实产生了 I2C 事务**（扫描耗时与 `begin()` 返回值），
  以及改动后不再产生。
- `paperdiy` 镜像未开 PSRAM，面板不可用（`displays=0`）；被测逻辑与面板无关，但本轮没有画面证据。
- `cardputer` 的 Cardputer/ADV 变体探测在虚拟设备上无人应答，最终仍解析为 board 14。

## 4. 兼容性与影响面

- 公开 API 语义变化：`I2C_Class::isEnabled()` 从“有端口”变成“有引脚”。第三方代码若把它当
  “总线已配置”使用，行为更严格；仓库内没有此类用法。
- `begin()` 在无引脚时返回 false：调用方原本也拿不到可用的总线（旧代码只是把 port -1 交给
  M5GFX 的软件端口），因此对正确编写的调用方无行为回退；对依赖“port -1 + 残留引脚”的写法
  是刻意的行为变更。
- `release()/stop()/write()/read()` 在禁用总线上从“把失败转嫁给 M5GFX”变成直接返回 false，
  返回值语义不变（都是失败），只少了 M5GFX 内的无效调用。
- 启动时间：无内部总线的板子少一次 RTC/IMU 探测；有内部总线的板子不变（`sticks3` 对照）。

## 5. 非阻塞观察

1. **引脚单一真值 + 端口未校验**：`isEnabled()` 只看引脚，`_setup_i2c()` 在内部 SCL 未定义时
   写的是 `setPort(I2C_NUM_MAX, in_sda, in_scl)`。当前 55 行 pin table 全部成对置空，组合不可达；
   若将来只置空其一，`isEnabled()` 会对一个 `m5gfx::i2c::init()` 必然拒绝的端口报 true。
   可选加固：`begin()` 里同时要求 `_port_num < I2C_NUM_MAX || _port_num < 0`（负端口是合法的
   软件端口），或在 `setPort()` 里对端口与引脚做一致性断言。
2. **M5Unit OLED 自动探测仍要求 `i2c_port >= 0`**（`M5Unified.hpp:554` 一带），
   所以“负端口 + 有效引脚”的 `Ex_I2C` 虽然 `isEnabled()` 为真，仍无法让该自动探测接上。
   这是改动前就存在的限制，本 PR 未回退也未修，与 PR 描述“软件端口也算启用”略有落差。
3. 每个方法重复 4 行护栏：与仓库风格一致，未建议改动。

## 6. 复现方式

1. 取 `m5stack/M5Unified@0ca3a43`（pre）与 `@17fc0ae`（post）、`m5stack/M5GFX@28d4794`。
2. 用 `code/probe-main.cpp`、`code/app-CMakeLists.txt`、`code/sdkconfig.defaults`
   建 ESP-IDF 工程；本地 IDF v6.1 下把两个组件的 `CMakeLists.txt` 换成
   `idf_component_register()` 包装并去掉 `idf_component.yml`（见 `evidence/build-summary.txt`），
   源码不作任何改动。
3. `idf.py build` 后按 `flasher_args.json` 把 bootloader/分区表/app 合并为单镜像。
4. 通过本机 Device Service 上传、`firmware/import`（`device_id=paperdiy|cardputer|sticks3`）、
   建会话，读取串口直到 `P2 MARK_DONE`。

## 7. 未覆盖项、风险与回滚

| 项 | 状态 | 说明 |
| --- | --- | --- |
| 真实硬件 | `NOT RUN` | 无 PaperDIY/Cardputer/Stamp 实机；作者 `begin_ms` 表未复现 |
| PC/SDL 构建 | `NOT RUN` | 仅源码推断 SDL stub 的 `init()` 恒成功 |
| 作者计时表 6 块板 | `NOT RUN` | StampC3/C3U/S3/P4、NanoC6/H2 本机无可启动 M5Unified 目标 |
| 引脚复用电气后果 | `NOT RUN` | QEMU 不建模 GPIO 矩阵 |
| Arduino 构建 | `NOT RUN` | 本轮只做 ESP-IDF v6.1 构建 |

风险与回滚：改动只涉及 I2C 就绪判定与早退路径；若下游依赖旧语义，可回滚 `17fc0ae`
单提交（无状态、无持久化影响）。
