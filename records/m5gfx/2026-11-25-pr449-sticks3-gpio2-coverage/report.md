# M5GFX #449 报告：StickS3 M5PM1 gpio2 功能位与 board_t 覆盖测试

## 1. 任务背景

PR #449 是两个独立改动（两个 commit）：

1. `5b65db1` StickS3：把上电序列里 `0x16` 的清除掩码由 `0x04` 改为 `0x30`。
   作者指出 M5PM1 的 GPIO 功能寄存器每引脚 2 bit，gpio2（LCD 电源）是 `0x16` 的 bit5:4，
   原来的 `0x04` 清的是 gpio1 的功能位；PM1 寄存器跨 ESP32 复位保留，所以应用设过的
   gpio2 功能位不会被清掉，而 gpio1 每次启动都被改。
2. `3e50e3c` 新增 `extras/board_spec/test/board_id_coverage.test.js`：对每个 `lgfx::board_t`
   值要求 catalog 中有同 `legacy_board_id` 的板子、且某个 `<chip>_boards[]` 表里注册了
   同 id 的 `board_desc_t`；刻意不覆盖的值与未发布板分别列入排除表/预告表。

评审目标：确认掩码与寄存器布局一致、影响面、host/CI 是否真的覆盖、覆盖测试是否真的会失败。

## 2. 代码事实

### 2.1 掩码与寄存器布局

`src/board_detect/m5/pmic_ops.hpp:86-93`（head）：

```cpp
static constexpr ops::op_t sticks3_power_on[] = {
  ops::i2c_write8(0, 0x09, 0x00),
  ops::i2c_bit_off(0, 0x16, 0x30), // gpio2 function (2 bits per pin): gpio
  ops::i2c_bit_on(0, 0x10, 0x04),  // GPIO_MODE bit2 = gpio2 输出
  ops::i2c_bit_off(0, 0x13, 0x04), // GPIO_DRV  bit2 = push-pull
  ops::i2c_bit_on(0, 0x11, 0x04),  // GPIO_OUT  bit2 = 输出高（LCD 供电）
};
```

`ops::i2c_bit_off(dev, reg, bits)` = `i2c_masked8(dev, reg, 0, bits)`（`ops.hpp:169-172`），
即写 value 0、mask=bits。

- M5Unified `src/utility/power/M5PM1_Class.inl:31` `M5PM1_REG_GPIO_FUNC0 = 0x16`（gpio0..3），
  `:32` `FUNC1 = 0x17`（gpio4..7）；`:149-161` `setGPIOFunction()` 用
  `shift = num * 2`、`mask = 0x03 << shift`。gpio2 → shift 4、mask `0x30`。
- 枚举 `gpio_function_t`：`gpio = 0b00`、`irq = 0b01`、`special = 0b11`（`M5PM1_Class.hpp:44`），
  所以“清 bit5:4”就是把 gpio2 切回 GPIO 功能，和紧随其后的 MODE/DRV/OUT 操作配套。
- M5GFX 自己在 `src/M5GFX.cpp:156` 与 `:644` 给 P4 Hub / 另一块板的 GPIO3 写
  `0x16` 掩码 `0xC0`（bit7:6），与 2 bit/引脚 的布局一致，属仓库内独立佐证。
- ToughC5、PaperDIY 的序列早已是 `i2c_bit_off(0, 0x16, 0x30)`（`pmic_ops.hpp:117,195`）。
- catalog `extras/board_spec/boards/m5sticks3.json` 明确 `pmic.pins.gpio2.roles =
  ["dev:lcd.power"]`，与注释“gpio2 (LCD power)”一致。

结论：`0x30` 正确，`0x04` 确实落在 gpio1（bit3:2）上；旧代码把 gpio1 的功能位由
`0b11` 清成 `0b10`（datasheet 保留值），并放任 gpio2 保持应用留下的功能。

### 2.2 同步点是否齐全

`0x16` 的旧值出现在三处，PR 都改了：

| 位置 | 作用 | 改动 |
| --- | --- | --- |
| `src/board_detect/m5/pmic_ops.hpp:89` | 生产序列 | `0x04` → `0x30` |
| `test/board_detect/ops_host.cpp:143-149` | legacy 序列对照表 | `keep 0xFB` → `0xCF`（`mask = ~keep = 0x30`） |
| `test/board_detect/fixtures/s3.txt:177` | descriptor 快照 | `6:0,22,0,4` → `6:0,22,0,48` |

`assert_same_sequence()` 用 `write_mask = ~keep | value` 反推，因此 `0xCF` 对应
mask `0x30`、value `0`，与生产序列一致；同表里 `0x13` 仍是 `keep 0xFB`（mask `0x04`），
因为 GPIO_DRV 是“每引脚 1 bit”，不是功能寄存器 —— 这一处不动是正确的。

`grep -rn "0x16" src/ extras/ test/` 未发现第四处 StickS3 相关拷贝。

### 2.3 覆盖测试做了什么

`extras/board_spec/test/board_id_coverage.test.js`（128 行）：

- `stripCode()` 去注释/字符串，遇到 raw string literal 直接失败（避免漏解析）。
- `parseBoardEnum()` 严格解析 `enum board_t`：显式十进制（不許前导 0）/十六进制/别名；
  数字重复但不是别名 → 报错；未知别名 → 报错；其它语法 → 报错而不是跳过。
- catalog：`boards/*.json` 的 `legacy_board_id` 集合。
- definition：`src/board_detect/m5/**` 里 `board_desc_t desc_x = {{ id(lgfx::board_Y) ... }}`
  且被某个 `board_entry_t <chip>_boards[]` 表以 `{ &desc_x, ... }` 引用。
- 未覆盖/未发布名单各带“缺什么 + 原因”，名单与现状不符、或值已不在 `board_t` 中即失败；
  未发布板每次 `t.diagnostic()` 打印提醒复核。
- 明确把“是否可自动识别”留给 detector order 测试（本测试只保证 fixed 可选）。

## 3. 执行与证据

### 3.1 host（head `5b65db1`）

```text
cd extras/board_spec && npm test        -> tests 222, pass 217, fail 0, skipped 5
cd extras/board_spec && npm run check   -> check passed: 64 board(s), 91 resolved combination(s)
bash test/board_detect/run.sh           -> C++ test programs: 34 passed
```

5 个 skip 是 `M5Unified checkout not found` / `absent`，与本次改动无关。

快照一致性：在 `M5GFX_UPDATE_SNAPSHOTS=1` 下重跑 `run.sh`，`git status --porcelain` 为空，
说明 PR 对 `fixtures/s3.txt` 的改动正是生成器的输出，而不是手改对齐。

覆盖测试的“会失败”验证（在同一棵 head 树上做，做完即还原，`git status` 干净）：

| 变异 | 结果 |
| --- | --- |
| 删掉 `m5sticks3.json` 的 `legacy_board_id` | FAIL：`26 board_M5StickS3: no catalog` |
| 在 `board_t` 里加 `board_M5ProbeGhost = 26` | FAIL：`board_M5ProbeGhost = 26 repeats the value of another board` |
| 从 `esp32s3_boards[]` 删掉 `desc_sticks3` 行 | FAIL：`26 board_M5StickS3: no definition` |
| 把该行从 `esp32s3_boards[]` 挪到 `esp32p4_boards[]` | **PASS**（未被发现，见 3.3） |

### 3.2 虚拟设备（`sticks3` profile）

探针固件（ESP-IDF v6.1，S3，8 MB flash，同树只换 M5GFX 源）：

```text
m5gfx::detect_config_t cfg; cfg.fixed_board = board_M5StickS3;
display.setDetectConfig(cfg); display.init();
// 读 PM1(0x6E) reg 0x16
```

| 构建 | 串口 | 画面 |
| --- | --- | --- |
| head `5b65db1` | `fixed_init=1 board=26 fixed=26 display=135x240`；`func0_after_init=0x00 gpio2_func=0 gpio1_func=0` | 135×240 `fa740237…8357` |
| base `34a5756` | 同上，`func0_after_init=0x00` | 同 SHA256 |

含义与边界：

- 打补丁后的板级启动路径在虚拟 StickS3 上正常：PM1 上电序列、面板初始化、背光与绘制都完成；
  `0x16` 在 `begin` 之后读回 `0x00`，与作者真机“`0x16` reads `00` after begin”一致。
- base 在同一 profile 的 `0x16` 复位值也是 `0x00`，所以这一轮**不能**区分两版掩码；
  区分力来自 host 快照/ops 对照与 2.1 的寄存器布局事实。
- 自动识别未跑通：M5GFX 检测器在该 profile 上 `candidate=0`（不确认 StickS3），
  因此用 `fixed_board`；`select_fixed_board()` 与自动识别走同一 descriptor、同一段
  `sticks3_power_on`，但“检测路径”本身 `NOT RUN`。

未能构造“复位前遗留功能位”场景（因此该场景 `NOT RUN`）：

1. 固件 `esp_restart()` 后串口没有第二次启动输出；Device Service `POST /reset`
   在 boot 阶段 `Guru Meditation … LoadProhibited`（测试基础设施问题，与被测改动无关）。
2. 在 `M5GFX::init()` 之前先用 IDF `i2c_master` 建总线写 `0x16` 再删总线（或先用
   `lgfx::i2c` 读写），fixed 启动会失败：`fixed=26` 已接受但 `init=0`，且 `0x16`
   保持预置值、上电序列一个 op 都没执行；把预置值改成 `0x00` 同样失败。
   即该 profile 上无法在同一 boot 内预置 PM1 寄存器，未能定位到具体失败步骤。

### 3.3 覆盖测试的一处缺口（非阻塞）

测试只要求 definition 出现在“任一” `<chip>_boards[]` 表，没有把表所属芯片与 catalog 的
`chip` 字段对应。`select_fixed_board()` 只查当前 target 的表（`detection_package.inl:65-90`），
所以把行挪到别的芯片表会让该板在本机失效、在错机可选，而测试仍然 PASS（上表第 4 行实测）。

现状：用同一套正则统计 64 块 catalog 板子的 `chip` 与所在表，0 处不一致；每块板只出现在
一张表里。因此补“表名与 catalog `chip` 一致”的断言不需要白名单，也不需要新增例外。

## 4. 上游 CI

`gh pr checks 449`：40/40 pass，含 `Catalog and generated sources`（即 `extras/board_spec`
的 `npm test`，新测试实际在 CI 里跑过）、`host`（board_detect host 测试）、
Arduino 2.0.17–4.0.0 与 IDF 5.1.6–6.0.2 的构建矩阵。PR `MERGEABLE`，非 draft。

## 5. 风险与回滚

- 风险面：只改 StickS3 上电序列的一个掩码，外加一个只读测试文件；不影响其它板型。
- 旧代码在“gpio2 已被应用改成非 GPIO 功能”时会让 LCD 电源打不开；若真有应用依赖
  “启动时顺带把 gpio1 功能清成 0b10”，属于依赖 bug 的行为，没有合理用例。
- 回滚：单独 revert `5b65db1` 与 `3e50e3c` 即可，两者互不依赖。

## 6. 未覆盖项

- hardware validation `NOT RUN`：无 StickS3 实物；作者的真机读数只作引用。
- “复位前遗留 `0x16` ≠ 0”的端到端场景 `NOT RUN`（原因见 3.2）。
- 自动识别路径 `NOT RUN`（该 profile 上检测器不确认 StickS3）。
- 旧掩码对 gpio1（按键/中断等）的实际功能影响未在真机观察。
- 未验证 PM1 在真实掉电/电池切换下是否真的保留 `0x16`（QEMU 模型不复现该电气行为）。
