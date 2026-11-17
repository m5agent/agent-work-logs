# 虚拟数字音频、附件审核与 PaperS3 触摸复验

## Cardputer 与 Cardputer ADV 原生数字音频

此前两个原生板型能使用启动时的麦克风夹具。此次把运行中替换输入和分页读取 I2S DMA 输出接入 Device Service。两个板型都使用原生 QEMU SHA-256 `68d98b8491b09eeb91fc3c99ee2dd7d2752ac1b6b548bf0c93981f4c225fb05d` 和各自的 UIFlow2 来宾探针。固件与样本校验值见 [运行清单](run.json) 和 [双板证据](evidence/cardputer-native-pcm-summary.redacted.json)。

ADV 前两次测试在来宾夹具等待测试按键时超时，报 `missing audio test key`，尚未开始采样。本轮通过的双板复测采用串口阶段标记和固定等待窗完成夹具替换。

将符合 16 kHz、单声道、s16le 的 WAV 发布为工件，等来宾输出各阶段标记后，分别通过 `audio.inject` 替换预置音调和全零 PCM。API 给出 `next_i2s_rx_start`，来宾结束并重新开始 RX，再输出每阶段采集的 3,200 样本。两个板型的音调都为 523.217 Hz、RMS 30,208.053；全零输入夹具下的来宾读值为 RMS 134.71，尾部 RMS 8.0。全零是输入夹具属性，来宾样本含残余信号。

集成版本首次复测中，Cardputer 的全窗口 RMS 596.676 超过原先探索阈值 200。首 400 个样本（25 ms）的 RMS 为 1,687.521，后七个等长块均为 8.0，两种音调仍通过。下一次双板复测完整保留 3,200 样本，观测全窗口 RMS 相对于音调 RMS 的比例以及从样本 400 起的稳态 RMS。两板全窗口均为 134.71，稳态 RMS 均为 8.0，分别满足低于音调 RMS 十分之一和稳态低于 12 的条件。只调整测量校验，模拟器源码和虚拟设备模型一致。

来宾调用真实播放接口生成约 660 Hz 的参考信号。两个板型的原生 DMA PCM 读回前 65,536 字节，按调用方声明的 48 kHz 单声道 s16le 计算，主频均为 660.657 Hz，窗口 SHA-256 与证据 ZIP 的相同字节范围一致。两份运行证据保留同会话摘要，清理后活动租约为零。范围是数字数据路径。物理麦克风、扬声器声学和浏览器音频未验证。

两个已停止会话在工作进程重启后，允许 `audio.read` 时均返回 HTTP 200，整段输出 SHA-256 与停止前一致，ZIP 含音频。禁用 `audio.read` 时两板均返回 HTTP 403，ZIP 不含音频。`audio.inject` 的拒绝独立验证。对应 Device Service 1.76.0，音频源码为 `c9088f83c68ca2db87fa910c5f0c0544198788fe`，集成版本 `731817add38c34e6d2a58f8dcde646cd7ded3f46`。音频执行源码与单测在这两个提交之间逐路径一致。完整平台套件运行 2,393 项，跳过 10 项，其余通过。51 项文档、4 项音频、16 项 ACL 检查及 API 合约校验也通过。 [保留读回和 ACL 对照](evidence/cardputer-retained-pcm-acl-summary.redacted.json) · [音频源码提交](https://github.com/m5agent/m5stack-esp-emulator/commit/c9088f83c68ca2db87fa910c5f0c0544198788fe)

## CoreS3 Port A U024 保存快照审核

审核源码 `4315174c8231b7ac5dd27fc41083fbf20c112106` 接收 U024 夹具请求。审核核对附件配置、会话、型号与固件绑定，然后分别从 QOM 取 I²C 计数，从同一 ZIP 的实际来宾 UART 取驱动 X/Y/按键读值。任一绑定或独立读值缺失时，该验收维持 `PARTIAL`。

相同 CoreS3 UIFlow2 来宾固件在两个独立 dry-run 中各运行至少 60 秒。总线每次记录 49 次事务、72 个读取字节和 24 个写入字节。两个注入值 37/201/1 和 52/177/0 均与来宾读取一致，审核详情和报告也一致。错误会话绑定与缺少来宾读值的负向控件分别返回 `unit_evidence_identity_mismatch`、`unit_guest_readback_not_observed`。审核 192 项单元测试和 OpenAPI 0.6.0 YAML 解析通过。两次运行释放 Flash 与租约。未提交 Burner，未验证实机和机械量。 [双用例证据](evidence/cores3-u024-review-summary.redacted.json)

## PaperS3 原版浏览器触摸

被测固件为官方 PaperS3 Factory V0.5，使用原有 Chromium QEMU WASM、`papers3-wasm-wallclock-et047tc1` 和虚拟时钟除数 1。首次启动在触摸前出现 WASM 越界，触摸尚未执行。重试后收集 145 个面板样本，一段扫描计数保持不变至少 1,085.395 ms。随后 12 次触摸中有一次在暂停主机帧轮询且面板有 1,150 条新增扫描线的情况下正确消费接触，图标改变 607 像素。正常轮询下也存在面板零扫描、接触期无 GT911 读写并在松开后清除的案例。 [首次完整对照](evidence/papers3-first-comparison-summary.redacted.json)

第二次对照固定在虚拟触摸点 (113,347) 发出 300 ms 按压，以按下确认与释放入队之间的时间作为保守下限。6 次下限均超过 300 ms。3 次面板零新增线，另外 3 次新增 711–784 条线。正常轮询收到 9 次主机帧请求，暂停时为 0 次。全部 6 次触摸期无 GT911 事务，释放后出现清除、空状态 `0x80`、再次清除，图标变化为 0/6。两个平坦时段的失败同时没有主机帧请求。三个扫描失败窗口都保留了 RTC 日期时间突发读取和 BMI270 读寄存器，证实窗口内来宾仍有应用级 I²C 工作。 [匹配对照证据](evidence/papers3-flat-panel-summary.redacted.json)

待定位的是晚清除前的来宾驱动服务间隔。固定版本的 GT911 驱动在距上次服务至少 128 个来宾毫秒时先清掉滞留报告，再重试。晚清除顺序与此相符，证据尚不足以归因为特定前台调用，也尚未确定电子纸提交队列是否参与。两次完整浏览器运行退出后零 Worker、零 iframe、零 Device Service 调用。物理触摸时序、实机光学效果和完整来宾函数顺序为 `NOT RUN`。 [Factory 主循环](https://github.com/m5stack/M5PaperS3-UserDemo/blob/5e275ad4b70abb85f7193fda137844730e64c4db/main/main.cpp#L58) · [GT911 清除逻辑](https://github.com/m5stack/M5GFX/blob/c6f92dc03226cdc04d67c705a2020f62ad21ad01/src/lgfx/v1/touch/Touch_GT911.cpp#L169) · [EPD 生产者队列](https://github.com/m5stack/M5GFX/blob/c6f92dc03226cdc04d67c705a2020f62ad21ad01/src/lgfx/v1/platforms/esp32/Panel_EPD.cpp#L553)

## 交付边界

三项证据来自不同执行路径。原生音频与附件审核的源码可在各项目回滚各自提交。PaperS3 本次仅做对照测量，沿用已有固件和 WASM。原始音频、串口、匿名化前的运行标识、捕获包和临时运行信息均保留在测试环境。
