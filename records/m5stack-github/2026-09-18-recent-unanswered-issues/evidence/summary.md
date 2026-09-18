# 证据摘要：M5Stack GitHub 公开仓库零评论 Issue 快照

- 采集时间：2026-09-18 10:22–10:45 CST
- 查询：`gh api 'search/issues?q=org%3Am5stack+is%3Aissue+is:open&per_page=100' --paginate`
- 结果：618 个 open issue；其中 `comments == 0` 241 个
- 方法：Search API 拉取全部 618 条后按 `comments` 字段筛选；对每个候选 issue 的仓库做只读
  shallow clone 并核对源码行号；对 9 个 issue 记录 commit SHA 与 `file:line`
- 补充：M5Unified#354 有 4 条评论（m5agent 于 2026-09-17 回复），不属零评论集合

## 近 30 天创建的零评论 issue（10 条）

| 日期 | Issue | 标题 |
| --- | --- | --- |
| 2026-09-17 | StackChan#119 | Weak and highly position-sensitive Wi-Fi signal on StackChan |
| 2026-09-11 | uiflow-micropython#109 | ChainBus on second UART port fails with ESP_FAIL |
| 2026-09-10 | esphome-yaml#109 | AtomS3R + Echo Base continuous speaker noise |
| 2026-09-06 | M5Unit-8Encoder#7 | begin() speed argument truncated by uint8_t _speed |
| 2026-09-02 | M5GFX#276 | CoreS3-SE FT6336U identity warning |
| 2026-08-30 | StackChan#117 | WPA2-Enterprise cannot be joined |
| 2026-08-30 | StackChan#116 | Device reboots when companion app disconnects |
| 2026-08-25 | StackChan-BSP#7 | Motion getters skip the mutex |
| 2026-08-24 | M5_Hardware#19 | StackChan structure file missing |
| 2026-08-20 | M5Unit-NFC#8 | ESP32C5 support request |

## 源码核对快照

| 仓库 | HEAD commit | 核对内容 |
| --- | --- | --- |
| m5stack/M5Unit-8Encoder | a75ab1a0975f034cca4588b2c539d9dbb669cc2d | `uint8_t _speed` 与 `uint32_t speed` 参数截断 |
| m5stack/StackChan-BSP | 8d4d6fc3b7a6be379c6317c45a02a30bff8c492e | Motion getter 缺少 `_mutex` |
| m5stack/StackChan | 1b5765599fba8aaad1811d9a79358ccc7051f5f3 | 企业 Wi-Fi 默认关闭、scan_method 默认 FAST_SCAN、WiFiStation 生命周期、构建依赖脚本 |
| m5stack/M5GFX | 641944bd5b123e42b6f4379ff16768e292e203d1 | FT5x06 身份白名单与告警路径 |
| m5stack/HAT_8Servos_v1.1_Firmware | 4c5dc449493276c44e6881947abdff47813f0ae5 | I2C 长度 clamp 算术 |
| m5stack/esphome-yaml | cc708ddcc9dea7cfc746b408d2495ce281bbf2d2 | NS4150B 上电时序、LP5562 未初始化变量 |
| m5stack/M5Unified | e79eb6e3137a41e50b0ec23c8c38738bdb3a11e2 | VBUS/充电状态 API |
