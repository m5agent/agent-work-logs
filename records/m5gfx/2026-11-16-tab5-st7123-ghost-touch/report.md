# M5GFX #418：Tab5 ST7123 停止轮询后的鬼触点，代码级核对

## 现象与结论

报告者 huntson 在 M5Stack Tab5（ST7121 面板、触摸固件版本 01、M5GFX 使用的
`Touch_ST7123` 驱动）上观察到：主机停止轮询 1.3–2.5 s 后恢复，触摸控制器会在没有人
接触时上报 `valid=1` 的点，持续 1–2 次扫描，位置集中在两条长边（raw x=0 或 719），
面积/强度与真实触摸明显不同。作者已排除 I2C 读失败（失败计数 0），并实验证明在暂停
期间由另一个任务持续每 20 ms 读取可以消除鬼触点。

本次为只读代码级核对，结论是：**M5GFX 侧没有任何过滤，控制器上报什么就发布什么；
`intensity` 字节虽然读入结构体但被丢弃。** 因此 1–2 次扫描的 `valid=1` 帧会在
M5Unified 里立即成为一次按下。至于控制器为何在轮询间隙后产生这些帧，源码无法证明，
本轮也没有可用的 Tab5 硬件或虚拟 ST7123 模型，属于未确认项。

- 证据层级：`code-level verification`
- 源码版本：M5GFX `0.3.0` / master `28d47949bdc84f30881623476f555398e2194313`；
  M5Unified master `96576a14247ddc935149145aa6b51943464120f1`
- 只读核对：没有修改 M5GFX/M5Unified，没有向对方仓库推送，没有关闭 issue

## 代码事实

| 事实 | 位置 |
| --- | --- |
| `getTouchRaw()` 用三次独立 I2C 事务读 `0x0010`（adv_info）、`0x0009`（max touches）、`0x0014`（10×7 B 报表） | `Touch_ST7123.inl:132-141` |
| 报表 7 B：byte 4 = area，byte 5 = intensity；只有 area 被写入 `touch_point_t.size` | `Touch_ST7123.inl:148` |
| `touch_point_t` 只有 x/y/size/id，没有 intensity 字段 | `Touch.hpp:29-35` |
| `wakeup()`/`sleep()` 为空；驱动只读寄存器，不写扫描模式/阈值/噪声配置，也不复位芯片 | `Touch_ST7123.hpp:41-42` |
| Tab5 的 INT 是 GPIO 23，板级构造把它作为 `pin_int` 传入，但 `Touch_ST7123` 从不配置或读取它 | `esp32p4.inl:78`、`esp32p4_construct.inl:124-130`、`Touch_ST7123.inl` 全文 |
| 面板层的 `getTouch()` 只做 `getTouchRaw()` + 坐标变换，没有过滤 | `Panel_Device.inl:538-543` |
| M5Unified 首帧 `pressed` 即进入 `touch_begin`，没有去抖；`TOUCH_MIN_UPDATE_MSEC=4 ms` | `Touch_Class.inl:26,58-100`、`Touch_Class.hpp:40-41` |
| 0.2.28 的 `Touch_ST7123.cpp` 中 `getTouchRaw()` 函数体与 0.3.0 相同 | tag `0.2.28` 对照 |

补充：`0x0009` 按公开寄存器说明是“固件配置的最大同时触点数”，不是当前帧的触点数；
本机读到 10，所以驱动实际上每帧都读满 10 个槽位。三次读不是原子操作，帧边界可能落在
两次读之间，原则上可混合两帧的字段；但在完全无手指时这不能自行制造 `valid` 位。

## 主机解析复现

把 `getTouchRaw()` 的解析逻辑（结构体、循环、area→size）原样抽到主机 C++，用报告者
给出的鬼触点数值构造 10 槽报表：

```text
sizeof(touch_report_t)=7 offsetof(intensity)=5 offsetof(area)=4
driver as shipped, ghost frame: 2 point(s)
  id=0 x=0 y=635 area(size)=34
  id=1 x=719 y=633 area(size)=36
area>=30&&intensity<25 filter, same frame: 0 point(s)
real tap (area 8, intensity 45) under same filter: 1 point(s)
narrow ghost (area 1, intensity 10), driver as shipped: 1 point(s)
narrow ghost under intensity<25 rule: 0 point(s)
```

这说明：原始逻辑会把该鬼触点帧发布成两个点；area≥30 且 intensity<25 的规则能过滤该帧
并保留真实点；窄鬼点（area 1）只有 intensity 阈值能拦住。强度值在公开 API 中不可见，
因此任何强度规则只能放进驱动内部。

## 对照实现

- **M5Stack 自己的 Tab5 参考驱动**（M5Tab5-Keyboard-UserDemo `b4c3622`，
  `esp_lcd_touch_st7123.c`）：同样的三次读、同样不检查返回值的风格，`strength` 取 area，
  没有过滤；`adv_info` 做了零初始化。
- **ESPHome `st7123`**（`eebe66da6205`）：从 `0x0010` 一次读到 `0x0014 + max_touches*7`
  （74 B），避免跨帧；INT 为下降沿，空闲时保持高电平，读取报表会清除 INT；把 intensity
  作为 raw quality 上报；同样没有鬼点过滤。
- **espp `st7123touch` 1.4.2 文档**：明确 `0x0009` 为固件配置的最大同时触点数；
  并特别说明 ST7123 不应拨动 `TP_RST`，触摸引擎由显示初始化时的 `LCD_RST` 使能。

这些对照只能说明协议和 M5GFX 的行为，不能证明控制器在空闲后切换了扫描模式。

## 对报告者三个问题的回答边界

1. **是否已知固件行为**：无法从源码确认。驱动不发任何模式切换命令；如果控制器在停止
   读取后进入低功耗/空闲扫描，那是芯片固件内部行为。作者“暂停期间持续轮询可消除鬼点”
   的实验是目前最强的芯片侧证据，但本轮未复现。
2. **是否有更新触摸固件**：M5GFX 只读 `0x0000` 并打印版本，没有升级路径；公开资料没有
   触摸固件版本说明（版本 1=ST7121、3=ST7123）。此项需要 M5Stack 硬件/FAE 确认。
3. **应在驱动过滤还是修固件**：优先芯片侧修复。单台标定的阈值对轻触、手套、低温和
   面板差异有风险，通用库硬编码阈值会静默丢点。若必须先缓解，驱动内部是当前唯一位置
   （intensity 未暴露）；建议先验证“一次事务读取”和“记录鬼点时的 INT 电平”以区分
   跨帧撕裂与芯片真实上报，再决定阈值规则。

## 未覆盖项

- 物理 Tab5 上的复现、长时间浸泡、不同温度/批次：`NOT RUN`（本机无 Tab5）
- 虚拟设备复现：`NOT RUN`（本地 Tab5 模拟器没有 ST7123 控制器级模型）
- 单次事务读取对鬼点率的影响：`NOT RUN`（需要实机/驱动改动）
- INT 门控读取、驱动内强度阈值在真实触摸上的误拒率：`NOT RUN`
- 芯片固件版本与更新可用性：未有公开信息，需 M5Stack 确认
