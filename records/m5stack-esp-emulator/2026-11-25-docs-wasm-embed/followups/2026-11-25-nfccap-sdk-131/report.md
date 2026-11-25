# NFCCap 的真实 SPI 数据路径

## 身份

| 项目 | 记录 |
| --- | --- |
| 上游 PR 基线 | a61a29409f09f1f4bebae05e15c4bd6dcc4956b6 |
| 候选源码提交 | caab06dc7b517724b5d2b41f6d84a29217407a8d |
| SDK 候选补丁 | d6bf3a13e6010b0829fd8c28faab835d31efc7b7c36b21792cb2b4f9015059d7 |
| 实际导入的候选源码 | 64bcfe4760a507578eac6c708c546a6a725afd014c19a123ea066c8182bcc8d4 |
| 原例程/编辑器 | e0df69f68471a717ba4ec23e67945fe7ed312c4c1bd34e6651c18d147bac1c5b |
| 两阶段采用的原始 Flash | b6255f6af5ad10236380eae09a76b44ca174b5c4de391aef16413bdc590952bd |
| QEMU-WASM | 210db550d50847a3d4f66d86f81c8d1cdb2ac106ebf6bac16cccc60f4da0e211 |
| 静态站点清单 | cec271aefa1a575d8b257ea899a8af91eb8209575202fef99fb919bab37f16ac |
| ST25R3916 C 模型 | f6ac801a1ce8dcb0fd3878b6979b5b8e4aed2746408a665cd56c4c7b0a8423d5 |
| 原始运行报告 | cde945b3b2ae2864e46caadb820ea8eceefc47154858fe580b35001488aee13c |

cap/cc1101.py、unit/nfc.py、driver/nfc.py 和 driver/st25r3916.py 已逐字节匹配官方 2.5.3 与 2.5.5 的源码。候选只改 NFCCap 的方法体，让 SPI 构造得到的同一芯片实例用于 NFCReader 的方法，并调用其真实 begin。NFCUnit 的 I²C 构造接口及两个驱动文件按原样使用。 [官方 2.5.3 源](https://github.com/m5stack/uiflow-micropython/tree/50e440780492aa847378c7d3477ab912f7063bac/m5stack/libs) [官方 2.5.5 源](https://github.com/m5stack/uiflow-micropython/tree/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/m5stack/libs)

## 同会话执行

1. Cardputer-Adv 使用原 v2.5.3 工作台的显式 Cap 路径，时钟除数 1 和 one-insn-per-TB。模型挂接了真实 ST25R3916 SPI，NFC CS6、IRQ4。配对界面没有传送 Sub-GHz 或 LoRa 数据。
2. 候选加载前，用独立构造探针读到 TypeError。再经 UART0 raw-paste 运行未修改的原例程，仍从 cap/cc1101.py:301 返回同样错误。
3. 通过原工作台上传候选的私有 Python 模块。来宾对待导入字节做 SHA-256 检查，从已冻结的 cap.cc1101 绑定真实 machine、_port_table 和 SPI 芯片驱动。模块导入完成后删除临时文件，并把唯一新方法绑定至真实 NFCCap 类。实际读回芯片 ID 寄存器 0x3f 的值 0x2a。
4. 在同一会话中再次通过工作台载入完全相同的原例程。它继续执行扫描循环，并将真实模型返回的合成卡数据传给原应用。中断后只读原应用的变量，得到 NFC_APP_READBACK deadbeef DEADBEEF NTAG_210u 48 和 NFC_APP_VENDOR 42。
5. 两份原程序实际 240×135 RGB565 画面摘要从 6bde4f62…6fd2 变为 f79fc9f2…90db。首次静态页面截图保存了滚动后的编辑器区。独立复跑从真实画布保存两张完整屏幕和逐字节相同的 RGB565 原始数据。 [原生画面对照](screen-validation.md)页面 Stop 退出 0，iframe 移除，六个 Worker 在浏览器上下文关闭前正常回收。

本次执行使用源码级候选模块和同一份启动 Flash。正式冻结 SDK 的重新编译、I²C NFCUnit 的独立来宾复验和物理 NFC 射频测量待独立进行。模型返回的 DEADBEEF 是固定合成卡数据。

## 复现

1. 在独立工作区获取两份固定官方 tag 源码。将 cap/cc1101.py、cap/__init__.py、unit/nfc.py、driver/nfc.py、driver/st25r3916.py 分别以 cap-cc1101.py、cap-init.py、unit-nfc.py、driver-nfc.py、driver-st25r3916.py 存入 release-v253 和 release-v255。准备原例程源文件。不发布 ROM、固件或快照。
2. 按本地目录更新 [生成器](code/prepare-nfc-candidate.py) 的实验目录，并运行它。生成器核对两版的固定哈希、I²C 始终用 i2c 参数，以及单一方法的补丁；随后输出与 [实际导入的候选源码](code/nfccap-131-capsule.py) 字节相同的私有模块。
3. 以精确 0046 静态站点、ROM、官方 v2.5.3 基底及 Node 22/Playwright 运行 [回放脚本](code/run-nfccap-131.mjs)。设置 M5_NFC_131_RUN=1，指定已安装 Chromium 的 M5_WASM_CHROME，传入 candidate 与尚未使用的 browser-0046-nfccap-131-candidate-replay。这个模式自己执行修正前的构造和原程序对照。设置 M5_NFC_131_PREFLIGHT=1 可以只校验静态身份。
4. 如需独立的纯原版会话，使用相同输入以 stock 模式运行另一目录。保存原报告和清理记录。详细 [机器证据](evidence/nfccap-131.summary.json) 保留了本次使用的每个哈希。
