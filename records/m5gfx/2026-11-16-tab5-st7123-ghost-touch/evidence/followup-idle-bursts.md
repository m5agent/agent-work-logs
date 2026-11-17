# 第十一轮：空闲期 164 次 burst、形状与统计口径

- 来源评论：huntson，2026-11-17T03:16:11Z，
  [issuecomment-6936996813](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6936996813)
- 条件：同一台 Tab5，pinned 库（M5GFX d91077b9 / M5Unified 8530f53），LCD_RST 驱动，
  画面正常绘制，无人触碰，触摸 FW 01
- 数据：329 分钟内 164 次 burst（29.9 次/小时），间隔 4–400 s 不规则；burst 定义为一次
  读取内出现 ≥3 个弱起始候选；通常连续两次读，间隔约 24 ms；全部候选低于门禁 24，
  均由被拒起始候选日志计数
- 形状：
  - 中列，raw x = 358（面板半宽），最多 10 点沿 y 分布，intensity 7–8、area 1–7
  - 两端轨 x = 0 与 719 同时出现，10 点，intensity 10–11、area 1–18
  - 偶发单点，如 (669, 631)，area 32、intensity 13
- 同评论附带 host 侧更动：此前追踪的画面闪烁不是面板问题，是固件写 flash 日志时
  stall PSRAM，与显示读取冲突；正把写入移出画面活跃时段，与触摸 burst 无关

## 核对结果

1. **恒定 x 来自控制器，不是 host 解析**：`getTouchRaw()` 对每个 slot 用该 slot 自己的
   `x_h/x_l` 组装 x（[Touch_ST7123.inl:143-148](https://github.com/m5stack/M5GFX/blob/b48dce04c80d3e3c9874b7ba946c43d672129c28/src/lgfx/v1/platforms/esp32p4/Touch_ST7123.inl#L143-L148)），
   代码中没有把某一点 x 复制到其余 slot 的路径；字节偏移或撕裂读会让各 slot 的 x 不同。
   故“10 个点共享同一 x、y 变化”只能是控制器发出的内容。作者 29 次真实按压均为单点、
   x 35–693，与这些帧不是同一类。
2. **“10 点”是 10 个 slot 全部 valid，不是 10 个触点**：`0x0009` 是最大触点数
   （`ST7123_MAX_TOUCHES_REG`，`init()` 里作为能力值读取），驱动按 `7 × max_touches`
   一次读 70 B 再逐 slot 输出（[Touch_ST7123.inl:132-152](https://github.com/m5stack/M5GFX/blob/b48dce04c80d3e3c9874b7ba946c43d672129c28/src/lgfx/v1/platforms/esp32p4/Touch_ST7123.inl#L132-L152)）。
   一帧内全部 slot 置 valid 且字段极弱，是整表扫描状态，不是多指接触。
3. **强度分布下移，门禁 24 不变**：新鬼点 7–13，早前鬼点 10–22，真实首帧下限 24。
   (669, 631) 的 area 32 / intensity 13 是这批数据里最有价值的一点：面积与真实按压同级、
   位置不在轨道，只有 intensity 能把它分开，再次说明面积规则不可用作起始判据。
4. **两次空闲统计不是同一口径**：29.9 次/小时 vs 早前“约一小时 4 次”。按 burst 计是
   7.5 倍，按读取计（每 burst 通常两次读）约 15 倍。可分离的差异候选有两个：屏幕内容/
   背光状态（作者已测同一 60 轮里 0→35/60），以及写 flash 日志造成的轮询停顿。
5. **日志写停顿同时停 CPU 与 PSRAM**：CPU 停顿正是作者已测的出鬼条件（上传期间 20 分钟
   74 次；独立 sketch 10 次启动 0/60）。若空闲运行在计数时同步写 flash，该运行不满足
   “无轮询停顿”的前提，计数工具可能正在制造它统计的触发条件。
6. **形状级后备规则（可选，非建议必做）**：一次读内 ≥3 点共享完全相同的 x 不可能是真实
   接触（真实帧均单点），故“同 x 多点即整帧丢弃”能在强度漂移时兜底；但 (669, 631)
   不在轨道，轨道规则仍会漏，说明以 intensity 为主判据、形状规则只作后备是合适的分层。

## 未覆盖

- 芯片侧机制未证：单电极/整列扫描结果、坐标回退值（x=358 是否恰为芯片 max x 的一半）、
  扫描模式切换，均需原始 10 slot 行与 `0x0005/0x0006` 才能区分。
- 单台、单面板类型、FW 01；没有真正“无停顿”的空闲对照运行。
- boot 窗口鬼点、DCS 读、M5Unified#367 上拉黑屏、amp 单样本对，本轮均未涉及。
- 本机无物理 Tab5；虚拟设备 `NOT RUN`：`/api/v1/devices` 当日仍为 `tab5_enabled: false`，
  features 中 `qom`/`device_state` 为 false，catalog warning 仍写明 ST7123 触摸是
  固件 GDB 邮箱而非 I2C 芯片模型，且无 0x43 扩展器与 reset 线模型，无法产生或读取
  10 slot 报表帧。
