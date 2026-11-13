# M5Unit-8Encoder issue 7：I2C 速度截断修复复核

## 背景

2026-09-18 我们在 https://github.com/m5stack/M5Unit-8Encoder/issues/7 报告并复现了
`UNIT_8ENCODER::begin()` 的 `uint32_t speed` 被赋给 `uint8_t _speed` 的截断问题：
`begin(&Wire, ENCODER_ADDR, 21, 22, 100000UL)` 实际把 **160** 传给 `Wire.begin()`。

2026-11-12，报告者 nak435 提交 PR #8（`Fix I2C speed truncation by changing ...`），
维护者 renletao 于 `2026-11-12T10:37:05Z` 合并为 `7447df753d` 并关闭 issue。
本轮复核该修复是否真正覆盖我们报告的症状，并确认是否还有同路径遗留。

## 根因与修复

- 根因：`src/UNIT_8ENCODER.h` 中 `_speed` 声明为 `uint8_t`，`begin()` 的 `uint32_t speed`
  在赋值处被隐式截断（`100000 & 0xFF = 160`）。
- 修复（PR #8，只有一行）：`_speed` 改为 `uint32_t`。`begin()` 声明与
  `src/UNIT_8ENCODER.cpp` 的赋值/调用路径未变，因此不存在签名兼容性问题。

## 验证方式

用上游真实的 `UNIT_8ENCODER.cpp` 编译一个 host harness，`Wire.h` 换成录制型 mock：

- `TwoWire::begin(sda, scl, frequency)` 记录收到的频率；
- `requestFrom()` 可被强制失败，用来观察 `readBytes()` 的返回值处理；
- 两组构建分别使用 `59a8a0a`（修复前）与 `7447df75`（修复后）的 `UNIT_8ENCODER.h`，
  `.cpp` 在两者间完全相同（sha256 `034f6da8…`）。

命令（`code/reproduce.sh` 可重跑）：

```bash
g++ -std=c++17 -I include -I prefix prefix/UNIT_8ENCODER.cpp harness.cpp -o harness_prefix
g++ -std=c++17 -I include -I fixed  fixed/UNIT_8ENCODER.cpp  harness.cpp -o harness_fixed
./harness_prefix; ./harness_fixed
```

## 结果

| 调用 | 修复前 `59a8a0a` | 修复后 `7447df75` |
| --- | ---: | ---: |
| `begin(..., 100000UL)` | 160 | 100000 |
| `begin(..., 400000UL)` | 128 | 400000 |
| `sda/scl` 透传 | 21 / 22 | 21 / 22 |
| `requestFrom()` 失败后 `getEncoderValue(0)` | -1 | -1（未变） |

结论：报告中的截断症状在库逻辑层已消除，参数与 sda/scl 透传均正确。

## 影响面与遗留

- `src/UNIT_8ENCODER.cpp` 未改动，其余 API 行为不变。
- `readBytes()` 仍不检查 `requestFrom()` 返回值：总线失败时照常读 4 字节并返回 `-1`，
  调用方无法区分“真实值 -1”与“传输失败”。这是同文件既有缺口，不在本 issue 范围，
  本次未提交 patch。
- `library.properties` 仍为 `0.0.1`，仓库只有 `0.0.1` tag；修复当前只在 `main` 上，
  通过 Library Manager 安装的发布包是否已包含该修复未验证。

## 证据

- `evidence/harness-output.txt`：两组 harness 输出、所用头文件与 `.cpp` 的 SHA256。
- 修复提交：`7447df753d`（Merge pull request #8 from nak435/patch-1）。
- 修复前基线：`59a8a0a`（`Update UNIT_8ENCODER.h` 的父提交）。

## 限制

- 没有 Unit-8Encoder 硬件，未测量真实 SCL 频率与通信稳定性。
- 未链接 Arduino-ESP32 核心，未覆盖其频率分频/钳制逻辑。
- 结论等级为库逻辑层（host harness），不是硬件验证。
