# CoreS3 UIFlow2 绘图例程修复

- 日期 2026-11-25
- 工作类型 fix，virtual-device validation
- 设备 CoreS3，Chrome 158.0.8127.37
- 问题来源 [模拟器 #249](https://github.com/m5agent/m5stack-esp-emulator/issues/249)
- 结果 PASS，显式 v2.5.5 绘图预设中运行原版程序，完整 QR 解码为 Hello
- 正式托管、真机和分享链接自动启动未执行

通过浏览器工作台选择绘图预设并启动。实际加载原版 Python 后，来宾串口报告 320×240，屏幕完整显示图形、文字、标志及二维码。独立解码获得 `Hello`。同一导出中的默认 v2.5.3 工作台连续两次执行原编辑器初始程序。两组会话均正常停止并清理。

- [复现步骤、根因与范围](report.md)
- [结构化执行记录](run.json)
- [工作台、串口、像素和回收证据](evidence/workbench.summary.json)
- [独立 LittleFS 组合哈希](evidence/composition.summary.json)
