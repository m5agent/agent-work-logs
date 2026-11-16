# 报告：Touch_ST7123::getTouchRaw() 失败读取解析（M5GFX #417）

## 1. 问题来源

报告者 huntson 在 Tab5（ST7121 面板、触摸固件 01）上发现 M5GFX 0.2.28 的
`Touch_ST7123::getTouchRaw()` 忽略三次 I2C 读取的返回值，并把未初始化的
`adv_info` / `touch_report[]` 当作有效数据解析，提出“零初始化 + 任一读取失败即返回 0”
的补丁，同时指出 `_read_fw_info()` 在读取失败时仍返回 true。

本轮目标是独立核对报告的两个结论，并确认补丁是否覆盖幻触点路径，不修改上游代码。

## 2. 代码事实（M5GFX 28d4794，0.3.0）

### 2.1 三次读取均未检查

`src/lgfx/v1/platforms/esp32p4/Touch_ST7123.inl:109-157` 中：

- `132`：`adv_info_t adv_info;`（未初始化）
- `133`：读 `0x0010`，忽略返回值；`134` 立即用 `adv_info.with_coord` 分支
- `136`：读 `0x0009` 到 `max_touches`，忽略返回值
- `140`：`touch_report_t touch_report[max_touch_points];`（未初始化）
- `141`：读 `0x0014` 起 `7 * max_touches` 字节，忽略返回值
- `143-153`：按 `valid` 位解析每个槽位

`max_touch_points = 10`（`Touch_ST7123.hpp:49`），`touch_report_t` 实测
`sizeof == 7`（编译器填充到 7 字节），`adv_info_t` 为 1 字节。

### 2.2 “失败时缓冲区未动或只填一部分”成立

- `_readParams()`（`:39-44`）返回 `lgfx::i2c::transactionWriteRead(...).has_value()`。
- `transactionWriteRead()`（`src/lgfx/v1/platforms/esp32/common.inl:2650-2662`）依次执行
  `beginTransaction` → `writeBytes` → `restart` → `readBytes`；任一环节失败即带着错误
  返回，不会回滚已写入的字节。
- `readBytes()`（同文件 `:2542-2630`）在循环里逐字节写 `*readdata++ = *fifo_addr;`，
  地址 NACK 时一个字节都不写，传输中途超时则已写入的字节保留，最终返回
  `error_t::connection_lost`（`:2621`）。

因此第三次读取失败时，`touch_report[]` 可能是全未初始化、也可能是前几个槽位被部分
覆盖，后面的槽位仍是栈残留。

### 2.3 与 0.2.28 的对照

0.2.28 标签下文件为 `src/lgfx/v1/platforms/esp32p4/Touch_ST7123.cpp`，其
`getTouchRaw()` 函数体与 master 的 `.inl` 版本逐字相同（本轮用 diff 核对）。报告所说
“0.2.28 已存在、0.3.0 未修”成立。

### 2.4 `_read_fw_info()` 的失败路径

`Touch_ST7123.inl:47-76`：

```cpp
if (_readParams(...) && _readParams(...) && _readParams(...)) {
  ...
  if (sum == 0) { return false; }
}
return true;
```

三次读取全失败时整个 `if` 被跳过，直接返回 `true`。`init()`（`:78-107`）看到
`_read_fw_info()` 为真就置 `_inited = true`、调用 `wakeup()` 并返回 `true`，不会走
六次重试。也就是说芯片完全不应答时触摸初始化仍报成功。

## 3. 复现方法与结果

### 3.1 方法

把 `adv_info_t`、`touch_report_t` 和 `getTouchRaw()` 原样抽到
[`code/get_touchraw_check.cpp`](code/get_touchraw_check.cpp)，用 mock
`_readParams()` 模拟芯片：

- `0x0010` 成功时返回 `0x08`（`with_coord = 1`）
- `0x0009` 成功时返回 5（5 个活动槽位）
- `0x0014` 成功时全 0（无触摸）
- 指定某一次读取失败：缓冲区不写入（或只写 `partial_bytes` 字节）后返回 false

每次调用前用 noinline 的 8 KiB 栈帧填入 `0xFF`，模拟“未初始化栈”。编译命令：

```bash
clang++ -std=c++17 -O0 -fno-inline get_touchraw_check.cpp -o get_touchraw_check
```

`count = 5`。这与报告者的 host 实验设计一致，只是独立重写。

### 3.2 结果

| 场景 | master `28d4794` | 报告补丁 |
| --- | --- | --- |
| 无读取失败 | 0 | 0 |
| `0x0010` 读取失败 | 0 | 0 |
| `0x0009` 读取失败 | 0 | 0 |
| `0x0014` 读取失败、缓冲区未动 | **5**（`id=0 x=16383 y=65535 size=255`） | 0 |
| `0x0014` 读取失败、已填 3 字节 | **4**（首个 `id=1`，同字段值） | 0 |

原始输出：[`evidence/get-touchraw-output.txt`](evidence/get-touchraw-output.txt)。
5 个幻触点正好等于 `count`，因为 `max_touches=5` 且每个 0xFF 槽位的 `valid` 位为 1；
`x_h` 取 `0xFF` 的低 6 位得到 `63`，与 `x_l=255` 组合成 `16383`，`area=255` 即
`size=255`。

### 3.3 `_read_fw_info()` 检查

[`code/fw_info_check.cpp`](code/fw_info_check.cpp) 用同样的 mock：

- 芯片应答且全 0：返回 0（符合预期）
- 三次读取全失败：返回 1（master 行为），即 `init()` 会报成功

原始输出：[`evidence/fw-info-output.txt`](evidence/fw-info-output.txt)。

## 4. 对补丁的评估

报告给出的补丁：

1. `adv_info_t adv_info = {};` 并在第一次读取失败时 `return 0;`
2. `max_touches` 读取失败时 `return 0;`
3. `touch_report_t touch_report[max_touch_points] = {};` 并在报表读取失败时 `return 0;`

这能彻底消除“读取失败后解析栈残留”的路径；第 3 步的零初始化在提前返回之后是冗余的，
但无害，作为防御性写法可以保留。返回 0 与 `getTouchRaw()` 的调用契约一致（无触摸），
也与 `esp_lcd_touch_st7123` 的 `ESP_RETURN_ON_ERROR` 行为对齐。

`_read_fw_info()` 的修正会影响 `init()` 语义（芯片不应答时六次重试后返回 false），
与 `getTouchRaw()` 的修复是两件事。是否合并取决于 M5Stack 对触摸初始化失败的预期，
建议单独提交，避免把行为变化混进一个防御性补丁。

## 5. 未覆盖项与风险

- **物理 Tab5**：`NOT RUN`。本机没有 Tab5，无法在真实 I2C 上注入单次读取失败；报告者
  也说明其实机 74 分钟内失败计数为 0，属于潜在缺陷。
- **虚拟设备**：`NOT RUN`。本地 Tab5 模拟器没有 ST7123 控制器级模型，未做“强制某次
  I2C 读失败”的实验，因此没有 virtual-device validation。
- **完整构建**：只做了 host 逻辑复现，未把补丁编进 M5GFX/固件，未在面板上回归触摸。
- **#418 关联**：本轮不判断补丁是否影响鬼触点；报告者已说明两者独立（其失败计数为 0）。
- **栈布局差异**：host 复现用 `0xFF` 预填和 `-O0`，真实固件的栈内容与优化级别不同，
  幻触点的具体坐标会变；结论是“内容不可预测且会被当作触摸”，不依赖固定数值。

## 6. 结论

报告的事实与补丁方向均成立，证据等级为 **code-level verification**（host 可执行复现 +
源码核对）。物理硬件与虚拟设备验证未执行，不构成对实机失败率的判断。
