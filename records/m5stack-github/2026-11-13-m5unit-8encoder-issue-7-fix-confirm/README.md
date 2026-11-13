# M5Unit-8Encoder issue 7 — I2C speed truncation fix confirmation

- 日期：`2026-11-13`
- 结果：`PASS`（声明的验收层级：host harness / 库逻辑；硬件 `NOT RUN`）
- 工作类型：`issue`
- 问题来源：https://github.com/m5stack/M5Unit-8Encoder/issues/7
- 源码版本：`m5stack/M5Unit-8Encoder @ 7447df753d`（PR #8 合并提交），对照基线 `59a8a0a`
- 环境：macOS；Apple clang 21.0.0；host C++ harness + 录制型 `Arduino.h` / `Wire.h` mock；无 Unit-8Encoder 硬件、无 Arduino-ESP32 核心

## 结论

维护者已在 `7447df75`（合并 PR #8）把 `UNIT_8ENCODER::_speed` 从 `uint8_t` 改为 `uint32_t`，即本 issue 报告的唯一根因。用真实 `UNIT_8ENCODER.cpp` 对录制型 `TwoWire` mock 编译执行，修复前 `begin(..., 100000UL)` 传给 `Wire.begin()` 的是 **160** Hz，修复后是 **100000** Hz；`400000UL` 由 **128** 变为 **400000**。报告的症状（S3 上 I2C 时钟被截断）在库逻辑层已消除。

修复只改了 `src/UNIT_8ENCODER.h` 一行，`src/UNIT_8ENCODER.cpp` 未变；`readBytes()` 不检查 `requestFrom()` 返回值这一既有问题仍然存在（失败时 `getEncoderValue(0)` 仍返回 `-1`），与本 issue 无关但同属该文件的健壮性缺口。

## 关键证据

- 运行：主机构建两组 harness，分别链接 `59a8a0a` 与 `7447df75` 的库源码，输出见 `evidence/harness-output.txt`。
- 源码：`7447df75:src/UNIT_8ENCODER.h:23` 为 `uint32_t _speed;`；`begin()` 声明 L28-L29 仍为 `uint32_t speed`。
- 版本：`library.properties` 仍为 `version=0.0.1`，仓库 tag 只有 `0.0.1`，修复只在 `main` 上，尚未对应新的发布版本号。
- 日志：`evidence/harness-output.txt` 含两组输出与所用源文件 SHA256。

## 文件

- `report.md`：完整报告
- `run.json`：结构化记录
- `evidence/harness-output.txt`：harness 输出与源文件哈希
- `code/`：harness、mock 头文件与可重跑脚本

## 未覆盖项

- 未在真实的 Unit-8Encoder + ESP32-S3 上测量 SCL 频率与实际通信稳定性（`NOT RUN`，无硬件）。
- 未运行 Arduino-ESP32 核心的 `Wire.begin()`，因此没有覆盖核心对目标频率的分频与钳制行为。
- 未验证 Library Manager 发布包是否包含该修复（`library.properties` 未升版）。
- `readBytes()` 未检查 `requestFrom()` 返回值的问题未修复，也未在本记录中提出 patch。
