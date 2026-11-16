# 第九轮：真实触摸原始表与起始规则核对

- 来源评论：huntson，2026-11-16T20:27:33Z，
  [issuecomment-6919732178](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6919732178)
- 数据：同一台 Tab5，画面正常、LCD_RST 驱动（pinned M5Unified）、触摸 FW 01；16 次真实
  按压的 first/peak area、intensity、held ms；报告者另说明第 16 号按压的真实首帧
  raw `(44,1144)`、area 35、intensity 50 被 area-only 规则丢弃
- 证据等级：报告者 `hardware validation`（单台、单面板）；本记录为
  `code-level verification`（对其两张表做算术核对，脚本见文件列表）

## 核对结果

1. **本表数值范围**：first intensity 33–56、first area 3–20；peak intensity 36–66、
   peak area 4–42；held 145–2283 ms；真实点最小 `|x|` = 35、距 719 最小 26，无一落在
   `x=0`/`x=719`。
2. **area-only 规则的实证代价**：本表第 8、10 号按压 peak 帧 area 31/42、intensity
   53/61，若规则作用于全程会被整帧丢弃；start-only 范围使其不影响。第 16 号的真实首帧
   （area 35 / intensity 50）确实被旧规则丢弃，与其描述一致。
3. **新规则 `area>=30 && intensity<25` 在起始帧不可达**：门禁先要求 intensity >= 25，
   同一候选点不可能同时满足 `< 25`。若门禁按点执行，则面积子句在起始路径永不触发，
   实际过滤器只有强度门禁。若面积子句也作用于非起始帧，则它只在 intensity < 25 时触发，
   即抬指/衰减帧；在 M5Unified 无去抖的前提下，丢一帧等于“松开 + 重新按下”。
4. **“余量 8”只在本次表内成立**：更早 20 次按压的 first-scan 下限是 26，鬼点上限 22。
   以 26 为约束，门禁 25 的实侧余量 1、鬼侧 3；23/24/25 分别为 (1,3)/(2,2)/(3,1)。
   观察空带是 23–25，24 是两侧各 2 的唯一取值。
5. **两列都是幸存者样本**：`first` 列是“通过过滤的第一帧”，不是按压第一帧。第 16 号
   即是反例（真实首帧 int 50 被丢，表中记 int 34）。低于门禁的值在两表里都不可能出现，
   故实侧下限只被上界约束。
6. **轨道分离度够但不增加拒绝力**：鬼点全部 `x∈{0,719}` 且 intensity ≤ 22，当前门禁
   已全部拦住；只有当出现“起始 intensity ≥ 25 的轨上鬼点”时才需要轨道条件。故先记录
   `x` 与 intensity，不先加规则。
7. **两次 x≈719 边缘按压未登记是过滤器与边框的歧义**：落在轨上、intensity < 25 的真实
   按压与鬼点签名相同，会被门禁拒绝，而现有日志只记被放行的帧，无法与“按到边框”区分。
   需要记录被拒的起始候选 `(x, y, area, intensity)` 与计数。

## 未覆盖

- 单台、单面板类型、FW 01；无轻触、手套、低温、第二台数据，23–25 空带是测量结果而非
  物理上不可能。
- 无强制读，被门禁拒绝的点完全不可见；轻触是否会把真实起始压到 25 以下未知。
- 本机无物理 Tab5；虚拟设备 `NOT RUN`：`/api/v1/devices` 仍是 `tab5_enabled: false`，
  ST7123 触摸为固件 GDB 邮箱，无 `0x43` 扩展器与 reset 线模型，被拒起始路径与轨道坐标
  都无法在那里产生。

## 文件

- [code/real_touch_table.py](../code/real_touch_table.py)：表值、门禁余量、
  area-only 丢弃、死子句、轨道距离、幸存者偏差的核对脚本
- [real-touch-table-check.txt](real-touch-table-check.txt)：运行输出
