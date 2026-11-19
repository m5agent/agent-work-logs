# M5GFX #436 报告：LP I2C 的 ACK 终端 read 后 endTransaction 等待 25 ms

## 1. 背景与目标

ToughC5（ESP32-C5）的触摸 `Touch_CHSC6540` 每调用一次 `M5.update()` 就停约 37.5 ms；
按住时约 80 ms。作者把区间定位到 `Touch_CHSC6540::getTouchRaw()` 的
`endTransaction()`：一次成功的 `endTransaction()` 约 36.5 ms，返回
`connection_lost`。同一固件的 Core（ESP32，HP I2C）为 3.5 µs；LP 端口的
ST25R3916 用 NACK 终端读取时也没有等待。作者给出的分界点是 #423
（`cc60eaa`）之前 `b48dce0` 无等待，之后出现。

本次工作要回答三件事：

1. 报告描述的代码路径是否真实存在，行号与版本是否对得上；
2. #423 是否应回退，还是应在 read 终端/驱动侧修；
3. 在没有 C5 实机的条件下，能给出到什么程度的结论。

## 2. 代码路径

固定 `develop` = `44324f34748812ce557e0dea39fb173cf9a73952`（2026-11-19）。

### 2.1 默认 ACK 终端

`src/lgfx/v1/platforms/common.hpp:275`：

```cpp
cpp::result<void, error_t> readBytes(int i2c_port, uint8_t *data, size_t length, bool last_nack = false);
```

`Touch_CHSC6540.inl:70-85`：

```cpp
if (lgfx::i2c::beginTransaction(_cfg.i2c_port, _cfg.i2c_addr, _cfg.freq, false))
{
  static constexpr uint8_t reg_number = 2;
  if (lgfx::i2c::writeBytes(_cfg.i2c_port, &reg_number, 1)
  && lgfx::i2c::restart(_cfg.i2c_port, _cfg.i2c_addr, _cfg.freq, true)
  && lgfx::i2c::readBytes(_cfg.i2c_port, tmp, 1)          // :73  ACK 终端
  && (tmp[0] != 0))
  {
    ...
    if (points && !lgfx::i2c::readBytes(_cfg.i2c_port, &tmp[1], points * 6 - 2))  // :78 也是 ACK 终端
    ...
  }
  if (lgfx::i2c::endTransaction(_cfg.i2c_port)) {}        // :84 返回值被丢弃
}
```

`readBytes()` 内部在 `last_nack == false` 时把最后一个字节作为 ACK 读；第二个
`readBytes()` 仍未传 `last_nack`，所以整个事务以 ACK 结束。

### 2.2 #423 把 LP 的 read 终端送入控制器 STOP

`src/lgfx/v1/platforms/esp32/common.inl`：

```cpp
// :1971
static constexpr uint32_t i2c_stall_limit_us = 25000;

// :2072
const bool force_stop_read = (i2c_context[i2c_port].state == i2c_context_t::state_read)
                           && !isLpPort(i2c_port);
...
else
{
  i2c_set_cmd(dev, 0, i2c_cmd_stop, 0, false, i2c_context[i2c_port].check_ack);
  i2c_set_cmd(dev, 1, i2c_cmd_end, 0);
  static constexpr uint32_t intmask_ = I2C_TIME_OUT_INT_RAW_M | I2C_ARBITRATION_LOST_INT_RAW_M | I2C_TRANS_COMPLETE_INT_RAW_M;
  updateDev(dev);
  dev->int_clr.val = intmask_ | I2C_ACK_ERR_INT_RAW_M | I2C_END_DETECT_INT_RAW_M;
  dev->ctr.trans_start = 1;
  uint32_t ms = lgfx::millis();
  taskYIELD();
  while (!(dev->int_raw.val & intmask_) && ((millis() - ms) < (i2c_stall_limit_us / 1000))) { taskYIELD(); }  // :2099
  ...
  if (res.has_value() && (...))
  {
    res = cpp::fail(error_t::connection_lost);
    i2c_context[i2c_port].state = cpp::fail(error_t::connection_lost);
    i2c_stop(i2c_port);   // :2110
  }
}
```

`git show cc60eaa` 的差分只有 `force_stop_read` 的引入：HP 仍走
`i2c_stop()` 的 GPIO 路径；LP 的 read 终端改为控制器 `STOP` + `END`，并等待
`TRANS_COMPLETE`。25 ms 等待与 `i2c_stop()` 恢复在 #423 之前就是 write 终端/错误
路径的一部分，不是 #423 新增的。

### 2.3 机制

I2C 主机读最后一个字节并回 ACK，表示「还要下一个字节」。从机因此继续驱动 SDA；
主机随后发 STOP 时，SDA 无法在 SCL 高电平期间上升，STOP 不成立。控制器等不到
`TRANS_COMPLETE`，25 ms 后超时；`i2c_stop()` 再用 9 个时钟 + STOP 强制恢复。
这解释了「成功的一次 `endTransaction()` 仍要 36.5 ms」以及返回值
`connection_lost`。

作者把点数读取改成 `last_nack = true` 后 `endTransaction()` 降到 29〜35 µs，
说明 STOP 本身和控制器路径没有问题，差异在从机是否释放 SDA。这与上面的机制一致。

## 3. 回归来源与责任边界

- #423（`cc60eaa`，merge `2121308`）的方向正确：LP 端口以 read 结束时，需要让
  STOP 真正出现在总线上，#421 才不会复发。
- 问题不在 #423 的 STOP 命令，而在「以 ACK 结束的 read」这个调用方式。回退 #423
  会让 #421 复发，因此不应回退。
- `Touch_CHSC6540.inl:84` 丢弃 `endTransaction()` 的返回值，使错误不可见。这是
  独立的可观测性缺陷，应修；但它只隐藏症状，不消除 25 ms 等待。

## 4. 同类驱动分布

| 驱动 | 点数读取 | 坐标读取 | 事务是否 ACK 终端 |
| --- | --- | --- | --- |
| `Touch_CHSC6540.inl` | `:73` ACK | `:78` ACK | 是（0 点或有点都是） |
| `Touch_FT5x06.inl` | `:118` ACK | `:127` ACK | 是（0 点也是） |
| `Touch_CSTxxx.inl` (CST816S) | `:208` ACK | `:213` ACK | 是（0 点也是） |
| `Touch_GT911.inl` | `:150` ACK | `:158` NACK | 有点时否；0 点（未触摸）时是 |

因此作者列的四个驱动中，GT911 只在「没有触摸点」的分支留下 ACK 终端；其余三个
在有点/无点时都以 ACK 结束。只要它们挂在 LP 端口上，理论上都会进入同一条 25 ms
等待（未在实机确认）。

## 5. 修复方向

### 5.1 案 A：驱动侧一次读完并 NACK 终端

以 CHSC6540 为例，把「点数 1 字节 + 坐标 `points*6-2` 字节」合并成一次固定上限的
`readBytes(..., last_nack = true)`，再从缓冲区首字节取点数。这样最后一个字节是
NACK，事务结束前从机已释放 SDA。

优点：改动局限在触摸驱动，不动 I2C 核心，风险面小。
缺点：每个驱动都要改；CHSC6540/FT5x06/CST816S 三处重复；GT911 的 0 点分支仍需
额外处理（点数读取必须保持 ACK 才能在有点时继续读坐标，0 点时又需要一次 NACK
终端）。此外固定上限读取会多读若干字节，需要确认触摸 IC 在报告长度之外仍能正常
返回。

### 5.2 案 B：LP 的 endTransaction 在 STOP 前补 NACK 字节

在 `readBytes()` 中记录「本次事务最后一个 read 字节是否为 ACK 终端」，在
`i2c_wait(port, true)` 的 LP read 终端分支里，先发 1 字节 `READ` + NACK，再发
`STOP` + `END`。示意（未编译、未实机验证）：

```cpp
// common.inl, STOP branch
const bool ack_ended_read = isLpPort(i2c_port)
                         && (i2c_context[i2c_port].state == i2c_context_t::state_read)
                         && !i2c_context[i2c_port].last_read_nack;
if (ack_ended_read)
{
  i2c_set_cmd(dev, 0, i2c_cmd_read, 1, true);   // dummy byte, NACK
  i2c_set_cmd(dev, 1, i2c_cmd_stop, 0, false, i2c_context[i2c_port].check_ack);
  i2c_set_cmd(dev, 2, i2c_cmd_end, 0);
}
else
{
  i2c_set_cmd(dev, 0, i2c_cmd_stop, 0, false, i2c_context[i2c_port].check_ack);
  i2c_set_cmd(dev, 1, i2c_cmd_end, 0);
}
```

理由与边界：

- 作者已实测「NACK 终端 read → `endTransaction()` 29〜35 µs 成功」，说明 LP 上
  NACK read 之后的 STOP 能成立；案 B 只是把这个顺序补在 ACK 终端 read 的末尾。
- NACK 只发生在事务最后，不会破坏「点数 ACK → 坐标继续读」的语义；作者实验中
  「点数 NACK 后继续读坐标会坏」正好说明 NACK 不能放在事务中间。
- 需要新增一个 context 标志，记录最后一个 read 是否 NACK 终端；否则无法区分
  「已经 NACK」和「ACK 终端」两种结束。
- 代价是事务结束前多读 1 字节。对依赖「跨事务延续内部 read 指针」的设备，可能
  改变下一次读的起点；M5GFX 常规的 `beginTransaction()` 会重新设置寄存器地址，
  预期无实害，但未验证。
- 该路径只对 LP 端口生效，HP 端口与 write 终端不变。

### 5.3 结论

优先案 B：一处修复覆盖 CHSC6540 / FT5x06 / CST816S，以及 GT911 的 0 点分支，
并保持 #423 的 LP STOP 设计。若只想先给 ToughC5 止损，案 A 对 CHSC6540 的局部
修改也可接受，但应同时修 FT5x06 / CST816S，避免同类问题继续存在。

## 6. 验证与证据

- `evidence/issue-status.txt`：条目 OPEN、0 comments、作者 GOB52、报告版本。
- `evidence/code-facts.txt`：固定 commit 的行号、源码摘录、#423 差分。
- `evidence/environment.txt`：Device Service 36 个 profile / 硬件测试中心 5 个节点
  的脱敏盘点；无 ESP32-C5，无 Arduino / ESP-IDF 工具链。
- `evidence/duplicate-check.txt`：没有找到同问题的重复 issue 或修复 PR。

本次没有执行任何运行验证；报告中的 ToughC5 数值全部是作者实机数据。

## 7. 未覆盖项与风险

- hardware validation `NOT RUN`：没有 ToughC5 / ESP32-C5 实机，无法复测 37〜80 ms
  或验证案 B。
- virtual-device validation `NOT RUN`：Device Service 没有 C5 profile；现有 QEMU
  profile 不含 C5，无法启动该板型。C6/P4 的 LP I2C 也没有可用于该读法的触摸配置。
- build `NOT RUN`：本机没有 Arduino / ESP-IDF 工具链，未编译最小 sketch 或案 B。
- 案 B 的实现、编译、实机确认 `NOT RUN`；上文的代码只是方向示意。
- C6 / P4 的 LP 端口是否出现同一等待 `NOT RUN`；代码路径共用，但没有板级确认。
- 风险：案 B 多读 1 字节改变设备内部 read 指针；需要在有跨事务延续语义的设备上
  确认。若从机在 NACK 后不释放 SDA，25 ms 等待仍会存在，需要实机验证。

## 8. 已发布回复

待发布后补充固定链接。
