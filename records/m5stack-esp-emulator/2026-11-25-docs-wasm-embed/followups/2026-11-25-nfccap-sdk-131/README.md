# Cardputer-Adv NFCCap 构造修正

- 日期 2026-11-25
- 问题 [上游 #131](https://github.com/m5stack/uiflow-micropython/issues/131)
- 结果 原版 FAIL，候选 SDK 代码在浏览器虚拟设备验证 PASS

同一个 UIFlow2 v2.5.3 来宾在原版构造探针和文档原例程中均报 unexpected keyword argument 'chip'。随后只替换原 NFCCap 的初始化方法，真实虚拟 SPI 读到器件寄存器 0x3f=0x2a，完全相同的原例程读到模型的合成卡 DEADBEEF，并报告 NTAG_210u、48 字节。复跑导出了原生画面，清楚显示合成 UID、卡种和容量。页面 Stop 退出 0，六个 Worker 全部回收。正式固件重新构建和物理 NFC 均待独立验收。

- [报告和精确复现](report.md)
- [运行记录](run.json)
- [脱敏证据](evidence/nfccap-131.summary.json)
- [原生画面对照](screen-validation.md)
- [SDK 最小补丁](patches/0001-nfccap-spi-init.patch)
