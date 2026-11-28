# 报告：M5Unified #455 Buzzer 注释澄清与 build_test 等待上限

## 1. 背景与目标

[#454](https://github.com/m5stack/M5Unified/pull/454) 新增 `M5.Buzzer` 后已合并进
develop（`48799c2`）。m5agent 在 #454 的评审中留了两条非阻塞建议：

1. CoreMatrix 上 PWM 蜂鸣器优先于外部 Speaker 输出，`isEnabled()` 的 “any output”
   表述在该板上不成立，需要在注释里说明；
2. `examples/Test/build_test` 的 `test_buzzer()` 用无界 `while (isPlaying())` 等待
   有限音结束，若 C61 上两次停止写都失败，`isPlaying()` 会一直为 true，示例会自旋。

#455 声称只改这两处、库行为不变，请求复核。

## 2. 改动面

`git diff 48799c2 b05f46e`：2 文件 +4/−3。

| 文件 | 内容 |
| --- | --- |
| `src/utility/Buzzer_Class.hpp` | `isEnabled()` 注释改为“M5.begin() 配置的 Speaker 输出（随后续 Speaker 设置变化）；CoreMatrix 始终使用 PWM 蜂鸣器，即使配置了 Speaker 输出” |
| `examples/Test/build_test/main/main.cpp` | `while (isPlaying())` → `for (int i = 0; i < 200 && isPlaying(); ++i)`，循环体仍为 `M5.update(); M5.delay(1);` |

## 3. 源码核对

### 3.1 注释与 C61 分支一致

- `src/M5Unified.inl:1704-1710`：`CONFIG_IDF_TARGET_ESP32C61` 下
  `case board_M5CoreMatrix` 无条件 `new M5IOE1_Class`、`begin()`、`_attachIOE1(*ioexp)`，
  没有失败回退分支，因此 CoreMatrix 上 `_ioe1` 总是非空。
- `src/utility/Buzzer_Class.inl:34-40`：`isEnabled()` 先判 `_ioe1`，非空直接返回 true，
  之后才回落到 `_speaker->isEnabled()`。
- `src/utility/Buzzer_Class.inl:57-62, 88`：`tone()` 在 C61 上把 `use_pwm` 设为
  `_ioe1 != nullptr`，PWM 路径 `_startIOE1()` 在 Speaker 分支之前 `return`，所以即使
  `_speaker` 已挂接，CoreMatrix 也不会走 Speaker。
- `src/utility/Speaker_Class.hpp:99-106`：`Speaker::isEnabled()` 就是
  `_cfg.pin_data_out >= 0`，所以注释中 “following later Speaker settings” 也成立。

结论：新注释准确。

### 3.2 上限覆盖了真正的挂死路径

- `src/utility/Buzzer_Class.inl:218-238` 的 `update()`：到截止时间后先尝试
  `_disablePwmLocked()`；失败则每 20 ms 重试，`_stop_attempts` 用尽后调用
  `_cutPowerLocked()` 并清空 `_deadline_us`。
- `_cutPowerLocked()`（`.inl:194-201`）只有在 G2 断电写成功时才把
  `_ioe1_playing` 置 false。若 PWM 关闭和 G2 断电两次写都失败，
  `_ioe1_playing` 保持 true，`_deadline_us` 变成 0，后续 `update()` 直接早退，
  `isPlaying()` 永远为 true——旧的无界 `while` 会永久自旋。
- 新循环最多 200 次，必然退出；退出后 `tone(1000)` / `stop()` 继续尝试恢复。

结论：上限有效，且正好覆盖作者在提交信息里描述的场景。

## 4. 构建

- 工具链：ESP-IDF 6.1（`esp32c61` target），M5GFX develop `603092a`（0.3.0）。
- 命令：在 `examples/Test/build_test` 下
  `idf.py set-target esp32c61 && idf.py build`，`M5GFX_PATH` 指向 M5GFX 组件。
- 结果：PASS。`M5Unified-build-test.bin` 361104 字节（`0x58290`），
  SHA-256 `f8bafe352cc5feffdf27b36d06388b3964d836ab33fc84bcd70bfd3b82377a87`；
  `CONFIG_IDF_TARGET="esp32c61"`、`CONFIG_FREERTOS_HZ=100`。
- CI：`gh pr checks 455` 37/37 pass，包括 `esp32c61 (IDF 6.1)`、Arduino
  `esp32/esp32s3/esp32c3/esp32c6/esp32h2/esp32c5/esp32p4` 的 `3.0.7`/`3.2.1`/`3.3.13`/`4.0.0`
  行、`m5stack_core`/`m5stack_cores3` 与 SourceCheck。

## 5. 虚拟设备验证

环境：本机 Device Service（`/api/v1`，端口 8787）的 `cardputer-adv` profile，
ESP32-S3 虚拟设备，8 MB flash；固件以 merged 方式导入。

### 5.1 同一段循环的 IDF 探针

为测量循环的真实时长，用同一 M5Unified head 构建了一个 IDF `esp32s3` 探针：执行
`tone(2000, 50)` 后跑 PR 中的 200 次循环，用 `esp_timer_get_time()` 计时，再执行
`tone(1000); stop()`。合并镜像 SHA-256
`877270010ede25464d93d2e833af11e39e63c161e349357625b204839c80eb77`，session
`35ddf89cad004795b5f48b7ff88c5caf`。

串口（`evidence/idf-probe-serial.txt`，每行重复一次是采集侧现象）：

```
P455T board=24 buzzer=1
P455T loop_i=200 dt_ms=0 playing=1
P455T delay20_ms=0
P455T DONE
```

含义：

- 上限生效：循环在第 200 次退出，没有挂死；
- 50 ms 的有限音在退出时仍在播放（`playing=1`），随后被 `tone(1000)` 覆盖；
- `dt_ms=0` 且 `delay20_ms=0`：在 IDF 构建中 `M5.delay(1)` 没有产生 1 ms 等待。

原因在 `src/M5Unified.hpp:308-311`：`delay(msec)` 实现为
`vTaskDelay(msec / portTICK_PERIOD_MS)`；IDF 默认 `CONFIG_FREERTOS_HZ=100`，
`portTICK_PERIOD_MS=10`，`1/10` 整数除法得 0，`vTaskDelay(0)` 只是让出 CPU。
Arduino-ESP32 构建用 1 kHz tick，`delay(1)` 才是 1 ms。

### 5.2 build_test 测试体

给 `examples/Test/build_test/main/main.cpp` 加串口打印（仅本地副本，未改动上游），
用 Arduino `esp32s3` 8 MB `huge_app` 构建并在同一 `cardputer-adv` profile 运行
（session `91319ac96c9b4b92a35984aa496c2ebf`，镜像 SHA-256
`fb3b724604f00d156cf7b764b4b4c56a94a11c0d7d2b1b950c737b6e4067b7a1`），
`before/after test_buzzer` 及其余步骤全部到达 `P455 DONE`，`board=24`、`buzzer=1`。

说明：未插桩的 build_test 只在 `test_log()` 打一行日志，虚拟设备采集窗口内没有
可见输出，因此用插桩副本证明测试体走通，不把它当作“原样固件 pass”。

## 6. 评审意见

无阻塞。

非阻塞建议（可选）：IDF 构建下等待不是约 200 ms 而是 200 次 `M5.update()`。若作者
希望正常路径上真的等到 50 ms 音结束，可用 `M5.delay(10)`（一个 tick）并相应减少
次数，或 `vTaskDelay(1)`；如果目的只是“保证不挂死”，当前写法已经满足。

## 7. 未覆盖与风险

- CoreMatrix 的 IOE1 PWM 实际时序、G2 掉电和 I2C 重试：本机没有 C61/CoreMatrix
  profile，`NOT RUN`；
- 真实硬件的蜂鸣器声音/响度/电气行为：`NOT RUN`；
- 未在作者 fork 的实机上复现；
- CI 只编译不运行，运行证据来自上述虚拟设备。

## 8. 回滚与影响

只读评审：没有改上游代码、没有 push、没有关闭条目；虚拟设备 session 已停止。
