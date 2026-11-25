# NFCCap 原生画面对照

独立复跑使用与首轮完全相同的 0046 WASM、静态站点、官方 v2.5.3 及私有候选源码。复跑在两个阶段打开工作台平面触屏并记录真实画布，分别从来宾读取 64,800 字节 RGB565LE。两张原始帧逐字节匹配首次记录的对应摘要。

- 原版画面显示 cap/cc1101.py 第 301 行 TypeError，原发行版失败再次确认。
- 同一原例程在候选构造方法绑定后，画面显示 NFC card detect、Card detected、UID: DEADBEEF、Type: NTAG_210u 和 Memory: 48 bytes。
- 同会话 UART 确认合成 UID、卡种和容量，芯片寄存器再次读回 0x2a。Vision OCR 将 UID 的首字母读作 V，实际画面和 UART 均确认原标签是 UID。
- DOM Stop 退出 0 并移除 iframe。浏览器上下文关闭前，CDP 观察到六个 Worker 正常回收。

复跑脚本增加原生屏幕和像素采集。执行参数、官方源数据和目录关系见 [首次报告](report.md)，采用 [原生屏幕脚本](code/run-nfccap-131-screen.mjs)。用本地 Swift Vision [OCR 脚本](code/nfccap-131-ocr.swift) 对实际屏幕取证。原件和复跑身份见 [第二次机器证据](evidence/nfccap-131-native.summary.json)。
