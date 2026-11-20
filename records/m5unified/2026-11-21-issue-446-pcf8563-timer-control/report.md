# M5Unified #446 调查报告：PCF8563 `begin()` 会清掉 Timer_control (0x0E) 的 TE

## 1. 背景

[m5stack/M5Unified#446](https://github.com/m5stack/M5Unified/issues/446)（作者 atgcgcta，日语，
2026-11-20，0 条评论）报告：在 CoreInk 上使用 PCF8563 的周期定时器 IRQ，但每次
`M5.begin()` 都会清掉 Timer_control 寄存器 (0x0E) 的 TE 位并改变 TD，导致定时器停止。
`cfg.disable_rtc_irq = false` 无法规避；把 `writeRegister8(0x0E, 0x03)` 改成
`writeRegister8(0x00, 0x00)` 后行为符合预期。

目标代码是 M5Unified 0.3.0（`96576a14247ddc935149145aa6b51943464120f1`）的
`src/utility/rtc/PCF8563_Class.inl:22`。

## 2. 根因

`PCF8563_Class::begin()` 执行三步：

```cpp
writeRegister8(0x00, 0x00);                 // 空写
_init = writeRegister8(0x00, 0x00)          // Control_status_1: 清 TEST/STOP
     && writeRegister8(0x0E, 0x03);         // Timer_control: TE=0, TD=0b11
```

PCF8563 的 Timer_control (0x0E) 中 bit7 是 TE，bits1:0 是 TD（00=4.096 kHz、
01=64 Hz、10=1 Hz、11=1/60 Hz）。因此写 `0x03` 有两个副作用：

- TE 被清 0，周期定时器停止；
- TD 被改成 0b11（1/60 Hz）。

原本为 `0x82`（TE=1，TD=0b10 = 1 Hz）的定时器，在写入 `0x03` 后停止。

`M5.begin()` 的内部顺序也与报告一致。`_begin_rtc_imu()` 先调用
`M5.Rtc.begin(&M5.In_I2C, M5.getBoard())`（`src/M5Unified.inl:2874`），之后才判断
`cfg.disable_rtc_irq`（同文件 2883-2884 行）。`false` 时不会调用 `disableIRQ()`，
但 `Rtc.begin()` 内部已经写了 0x0E=0x03，所以无法避免。`true`（默认）时
`disableIRQ()` 还会再写 0x0E=0x00（`PCF8563_Class.inl:281`），两种情况下定时器都会停。

## 3. 验证方法

### 3.1 证据等级选择

本机没有 CoreInk 实机，Device Service 的 36 个 profile 中也没有 CoreInk
（`evidence/device-service-profile.txt`）。但 `dial`（M5Dial）profile 在 QEMU 中带有
PCF8563 I2C 模型，且 profile 明确标注 RTC 已验证。该缺陷位于 `PCF8563_Class` 与
PCF8563 寄存器语义内，不依赖某一板卡的初始化细节，因此用 M5Dial 虚拟设备执行同一条
驱动路径。

- 证据等级：**virtual-device validation**（M5Dial / QEMU / PCF8563 model）
- hardware validation：**NOT RUN**（没有 CoreInk 实机）
- CoreInk 的 virtual-device validation：**NOT RUN**（没有该 profile）

### 3.2 构建

- M5Unified `96576a14247ddc935149145aa6b51943464120f1`（0.3.0）
- M5GFX `28d47949bdc84f30881623476f555398e2194313`（0.3.0）
- ESP-IDF `7101770dc6db2667b3c477cc31365dd1acd6db4e`（v6.0.2）
- target `esp32s3`，8 MB flash，无 PSRAM
- `idf.py set-target esp32s3 && idf.py build && idf.py merge-bin`

复现应用在 `code/pcf8563-446/`。在 `M5.begin()` 之前先直接初始化内部 I2C 并写
0x0E=0x82，模拟 MCU 复位后 PCF8563 仍持续供电、定时器仍在运行的状态。然后调用
`cfg.disable_rtc_irq=false` 的 `M5.begin(cfg)`，读回 0x0E。

五个阶段：

1. `M5.begin()` 前写 0x0E=0x82 并读回；
2. `M5.begin(cfg)`（`disable_rtc_irq=false`）后读 0x0E；
3. `M5.Rtc.setTimerIRQ(1000)` 后读 0x0E / 0x01 / 0x0F；
4. 再次执行 `M5.Rtc.begin(&M5.In_I2C)`（`M5.begin()` 用的同一函数）后读 0x0E；
5. 再次 `setTimerIRQ(1000)` 后读 0x0E。

## 4. 结果

### 4.1 未修改的 M5Unified

`evidence/serial-original.log`（3809 bytes (LF; raw UART 3888 bytes CRLF; trailing spaces stripped)，SHA256 `c66adda11e278b4b2c6b13a5ab94eddeaedf2baa412353926cd442df4a9f66ef`）：

```text
PCF8563_446_BOOT
PRE_ARM init=1 write=1 TC=0x82
I (105) M5GFX: [Autodetect] board_M5Dial
M5_BEGIN done board=12 rtc=1
POST_BEGIN port=1 TC=0x03 C2=0x00 CNT=0x00
SET_TIMER ok=1 applied=1000
ARMED port=1 TC=0x82 C2=0x09 CNT=0x01
RTC_BEGIN_AGAIN ok=1
AFTER_REBEGIN port=1 TC=0x03 C2=0x09 CNT=0x01
REARM ok=1 applied=1000
AFTER_REARM port=1 TC=0x82 C2=0x09 CNT=0x01
PCF8563_446_DONE
```

- `PRE_ARM` 的 0x82 是 TE=1 / TD=1 Hz。
- `POST_BEGIN` 的 0x03 是 TE=0 / TD=1/60 Hz；即使 `cfg.disable_rtc_irq=false`，
  仅 `M5.begin()` 就会停掉定时器。
- `setTimerIRQ(1000)` 后回到 0x82，C2=0x09（TIE=1，TF=0），CNT=0x01。
- 再次执行同一个 `begin()` 又变回 0x03；这对应下一次启动时的状态。
- 再调用 `setTimerIRQ()` 可恢复到 0x82（应用侧的现有规避方式）。

### 4.2 验证报告者提出的修改

应用 `patches/0001-pcf8563-preserve-timer-control.patch` 的一行修改后重新构建，
`evidence/serial-fixed.log`（3809 bytes (LF; raw UART 3888 bytes CRLF; trailing spaces stripped)，SHA256 `cee849c043b297181ba8454b3edf29e9ca974a01e355e57b420b0bc9b60621eb`）：

```text
PRE_ARM init=1 write=1 TC=0x82
M5_BEGIN done board=12 rtc=1
POST_BEGIN port=1 TC=0x82 C2=0x00 CNT=0x00
SET_TIMER ok=1 applied=1000
ARMED port=1 TC=0x82 C2=0x09 CNT=0x01
RTC_BEGIN_AGAIN ok=1
AFTER_REBEGIN port=1 TC=0x82 C2=0x09 CNT=0x01
REARM ok=1 applied=1000
AFTER_REARM port=1 TC=0x82 C2=0x09 CNT=0x01
PCF8563_446_DONE
```

替换后，`M5.begin()` 后和再次 `begin()` 后都保持 0x82。默认的
`disable_rtc_irq=true` 仍由 `disableIRQ()` 写 0x0E=0x00，因此符合
“默认关闭 IRQ / 显式 false 时保留”的配置语义。

## 5. 改动范围与兼容性

- 只改 `PCF8563_Class::begin()` 里写 0x0E 的一行。
- `disable_rtc_irq=true`（默认）的行为仍由 `disableIRQ()` 负责，不变。
- `false` 的用户可以保留 `M5.begin()` 之前设置的周期定时器。
- 直接调用 `Rtc.begin()` 的用户若要停定时器，需要显式调用 `disableIRQ()` 或
  `setTimerIRQ(0)`。这不是破坏性变化，而是让“初始化不再静默覆盖定时器设置”。
- 第二次写 0x00 是为了保留既有“先空写、再正式写”的两次写模式；它只是再次把
  Control_status_1 的 TEST/STOP 清 0，没有寄存器语义上的副作用。
- 没有向上游 push 或创建 PR；patch 只是建议，是否采纳由 maintainer 决定。

## 6. 未覆盖项

- CoreInk 实机上的复现与修复确认：**NOT RUN**（无实机）。
- CoreInk 的虚拟 profile：**NOT RUN**（Device Service 中没有）。
- INT 引脚的真实波形、长期周期漂移、切到 1/60 Hz 后的功耗：**NOT RUN**。
- 默认 `disable_rtc_irq=true` 路径的实测：**NOT RUN**（仅从代码确认
  `disableIRQ()` 会写 0x0E=0x00）。
- 上游是否采纳、是否进入 release：**NOT RUN**。

## 7. 回复正文（日语，实际发布）

> お世話になります。再現と切り分けの結果をご報告します。
>
> 結論：ご指摘のとおりです。`src/utility/rtc/PCF8563_Class.inl:22` の
> `writeRegister8(0x0E, 0x03)` が、`PCF8563_Class::begin()` のたびに
> Timer_control の TE(bit7) を 0 にし、TD(bits1:0) を 0b11（1/60 Hz）へ変えます。
> `M5.begin()` は `Rtc.begin()` を先に呼び、`cfg.disable_rtc_irq` の判定はその後
> （`src/M5Unified.inl:2874`、`2883-2884`）なので、`false` ではこの書き込みを
> 回避できません。既定の `true` では後段の `disableIRQ()` が 0x0E=0x00 を書きます。
>
> 証拠レベル：virtual-device validation（M5Dial / QEMU、PCF8563 モデル）。
> CoreInk の実機・仮想プロファイルは未実行です。M5Unified 0.3.0 `96576a1`、
> M5GFX 0.3.0 `28d4794`、ESP-IDF v6.0.2 でビルドした最小アプリで、
> `cfg.disable_rtc_irq=false` の `M5.begin(cfg)` 前後を読みました。
>
> 再現結果（0x51 / 0x0E）：
> - 開始前：0x82（TE=1, TD=1 Hz）
> - 未修正の `M5.begin(cfg)` 後：0x03（TE=0, TD=1/60 Hz）
> - `setTimerIRQ(1000)` 後：0x82（C2=0x09, CNT=0x01）
> - 同じ `Rtc.begin()` 再実行後：0x03
> - ご提案の `0x0E,0x03` → `0x00,0x00` に置換したビルド：`M5.begin(cfg)` 後も
>   0x82、`Rtc.begin()` 再実行後も 0x82
>
> したがって、`begin()` から 0x0E への書き込みを外す（または 0x03 を書かない）
> ことで、`disable_rtc_irq=false` のときにタイマー設定を保持できます。既定の
> `true` は従来どおり `disableIRQ()` で停止するため、互換性への影響は限定的と
> 考えられます。現状の回避策は `M5.begin()` 後に `M5.Rtc.setTimerIRQ()` を
> 呼び直す方法です。
>
> 詳細と生ログ：<public permalink>
>
> 未カバー：CoreInk 実機、CoreInk 仮想プロファイル、INT ピンの実波形・長期周期、
> 消費電流。

## 8. 证据文件

- `evidence/issue-446.json`：公开 issue 的元数据与正文。
- `evidence/device-service-profile.txt`：Device Service profile 摘要
  （无 CoreInk，M5Dial 的 RTC 已验证）。
- `evidence/build-and-run.txt`：构建环境、artifact / firmware SHA256、session ID。
- `evidence/register-readback.txt`：寄存器读回整理。
- `evidence/serial-original.log` / `evidence/serial-fixed.log`：原始串口日志。
- `patches/0001-pcf8563-preserve-timer-control.patch`：可应用到 base `96576a1` 的一行 patch。
- `code/pcf8563-446/`：复现应用与 Device Service 执行脚本。
