# 原生长按数据面

单点长按由原生 ST7123 Part 保持实际触点坐标，按 guest 虚拟时钟刷新 GPIO23 中断，并在计时结束时释放。API 回执要求客体读回按下和释放，以及至少一次刷新。旧版单点触摸 Part 通过独立 guest 探针对照。GT911 仍使用自身的点按和单指拖动路径。

无匹配 ELF 的同一原版 Arduventure 中，短按电源图标保持帧，空白区域长按正常释放。长按电源图标绘制原版 POWER OFF 画面，随后在 I²C1 上向 PI4IO 的 OUT_SET 写入十次变化。原生后端没有整机关机电源锁存模型，一次观测到的看门狗复位保留在证据中。

独立干净的代码归档与运行时用于正常 saved-snapshot 审核。该轮原生 720×1280 帧、九个点按应用断言和中心长按回执均来自同一会话，观察 60.620 秒共 12 次取证。整单 `SIM_PARTIAL / E_INTERACTION_CLAIM_PARTIAL`。该轮没有执行终态关机条件。

平台运行 2341 项测试，其中 8 项跳过，CI 两项均通过。隔离会话已停止，释放 Flash，零租约。测试未连接真实设备。应用轨迹、固件和运行时指纹可在有界摘要复查。

- [公开源码及独立探针复现](https://github.com/m5agent/m5stack-esp-emulator/blob/dc6853453a64f315a09b691c3631d9c2d4b3c08e/docs/evidence/2026-11-17-tab5-st7123-hold/README.md)
- [源码 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44091063244)
