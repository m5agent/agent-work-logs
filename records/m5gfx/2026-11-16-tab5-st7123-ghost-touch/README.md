# Tab5 ST7123 停止轮询后的鬼触点（M5GFX #418 代码级核对）

- 日期：`2026-11-16`
- 结果：`REVIEW`（仅代码级；物理硬件与虚拟设备均 `NOT RUN`）
- 工作类型：`issue`
- 问题来源：[m5stack/M5GFX#418](https://github.com/m5stack/M5GFX/issues/418)
- GitHub 回复：[issuecomment-6904885353](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6904885353)（英文，单条；issue 保持开启）
- 源码版本：M5GFX `28d47949bdc84f30881623476f555398e2194313`（0.3.0）；
  M5Unified `96576a14247ddc935149145aa6b51943464120f1`
- 环境：macOS 主机 + host C++ 解析复现；本机无 Tab5 硬件，本地 Tab5 模拟器无 ST7123
  控制器级模型；未运行物理或虚拟设备验证

## 结论

报告中的鬼触点是控制器 `valid=1` 的原始上报，M5GFX 会原样转发：`Touch_ST7123` 没有
面积/强度/时长过滤，且把报表中的 `intensity` 字节丢弃；M5Unified 首帧按下即
`touch_begin`。因此“1–2 次扫描的鬼点被当成一次点击”与代码一致。控制器为什么在轮询
间隙后产生这些帧，源码不能证明；作者“暂停期间持续轮询可消除鬼点”的实验指向芯片侧
行为，但本轮未复现。新触摸固件是否存在、是否应在驱动内加阈值，均未确认。

## 关键证据

- `getTouchRaw()` 三次独立读 `0x0010`/`0x0009`/`0x0014`，只把 area 写入 `size`：
  [Touch_ST7123.inl:132-148](https://github.com/m5stack/M5GFX/blob/28d47949bdc84f30881623476f555398e2194313/src/lgfx/v1/platforms/esp32p4/Touch_ST7123.inl#L132-L148)。
- `touch_point_t` 无 intensity 字段：`Touch.hpp:29-35`；面板层与 M5Unified 均无过滤。
- INT（GPIO 23）传入配置但驱动从不配置/读取；驱动不写任何寄存器、不复位芯片。
- 0.2.28 与 0.3.0 的 `getTouchRaw()` 函数体一致。
- host 解析：用作者给出的双边缘点数值，原逻辑返回 2 点；area≥30 且 intensity<25 规则
  返回 0；真实点（area 8 / intensity 45）保留；窄鬼点需 intensity 阈值才能拦住。
- ESPHome 从 `0x0010` 一次读 74 B 并说明读取会清 INT；espp 文档说明 `0x0009` 是最大
  同时触点数、ST7123 不应拨动 `TP_RST`。

## 文件

- [report.md](report.md)：代码事实、对照实现、三问边界和未覆盖项
- [run.json](run.json)：结构化状态与文件身份
- [code/parse_check.cpp](code/parse_check.cpp)：host 解析复现；编译方法见
  [code/README.md](code/README.md)
- [evidence/parse-check-output.txt](evidence/parse-check-output.txt)：本次运行输出
- [evidence/source-pins.json](evidence/source-pins.json)：固定 commit、文件 SHA256 与
  对照驱动说明

## 未覆盖项

物理 Tab5 复现、长时间/多温度测试、虚拟设备复现（无 ST7123 模型）、单事务读取与
INT 门控实验、驱动内强度阈值在真实触摸上的误拒率、触摸固件版本可用性均为 `NOT RUN`
或需要 M5Stack 确认。未修改 M5GFX/M5Unified，未推送代码，未关闭 issue。
