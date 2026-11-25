# CoreS3 WASM 来宾热复位修复

- 日期 2026-11-25
- 工作类型 fix，virtual-device validation
- 结果 PASS，覆盖指定浏览器来宾的 machine.reset()、文档 WDT 和宿主复位
- 设备 CoreS3，Chrome 158.0.8127.37，Apple Silicon macOS
- 问题来源 [模拟器 #254](https://github.com/m5agent/m5stack-esp-emulator/issues/254)
- 源码基线 b8f5df6a36b749f20f79d87fea0622416470dba8，候选 5548a553f583b0697247fe1481a7378853ff3609
- 真机、原生运行时与正式托管发布 NOT RUN

ESP32-S3 RTC 软件复位由目标核心执行。CoreS3 来宾先后通过 machine.reset()、文档 WDT 超时和宿主 QMP Reset。在原浏览器会话中，旧程序取消，新的 READY 到达，UART 编辑器执行了带验证标记的新程序。宿主复位也从已设置的 PROCPU 停顿状态恢复。

- [根因、构建和复验过程](report.md)
- [结构化执行记录](run.json)
- [对照证据和清理摘要](evidence/cores3-rtc-reset.summary.json)
- [Cardputer-Adv 显示与同路径键盘回归](evidence/cardputer-adv-regression.summary.json)
