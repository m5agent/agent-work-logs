# 硬件可用性（脱敏）

- 本机硬件测试中心当前在线 5 个节点，机型/SoC 为 ESP32、ESP32-P4、ESP32-S3 系列，
  **没有 ESP32-C5 / ToughC5**。
- 因此无法在实机上复现 #426 的 LP I2C 端口路径，也无法用示波器/逻辑分析仪观察
  `i2c_stop()` 期间的 SDA/SCL 波形。
- 也没有把其它机型当作替代：M5GFX 目前只有 ESP32-C5 的 ToughC5 板级配置把 I2C 端口
  映射到 LP I2C（`LGFX_LP_I2C_NUM` / `LGFX_LP_I2C_PORT`），其它在架机型走 HP I2C，
  不能覆盖同一实现路径。
- 本记录不包含节点 ID、IP、MAC、序列号或工位编号。
