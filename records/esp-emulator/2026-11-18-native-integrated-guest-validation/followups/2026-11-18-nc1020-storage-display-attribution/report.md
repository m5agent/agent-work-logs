# 原版 NC1020 的存档回读和显示诊断

## 两次原版冷启动

同一 Cardputer K132 原版合并 BIN 在 `b92d7b5630687cb7d7142346a39839ef61bd0116` 的原生 Device Service 和同一 Xtensa QEMU 下，以正常定时执行两次冷启动。两次导入完整的 206 个 ROM bank 与 512 KiB NOR。基础 bootloader、factory app 与应用 SDK 保持原样。两份实际读回的 8 MiB Flash 逐字节相同，SHA-256 为 `4d345b3c54bce553a28c7ee0f72e40e8784b072a0dbd236e2f805593f64e2b93`。

来宾分别在约 25.6 和 29.6 秒进入应用循环。第一次 G0 前后均与作者图案像素一致。第二次 G0 前后仅匹配 61.59%，观察窗口内没有首次非零绘制标记，证据 ZIP 中仍有 351 个心跳标记。两次都接受 0.85 秒 G0 按住并在各自证据路径保存实际 99,384 字节状态文件。独立回读同会话 FAT 文件和媒体，停机后已释放 Flash，活动租约为零。显示验收为 `PARTIAL`。

## 两个新服务阶段的存档

第一阶段导入原版来宾真实填充的 Flash，附不含替代 ROM/NOR 的媒介。来宾报告 `romdata pre-filled`、`NOR in flash ready` 和 `LoadNC2k() returned`，跳过冷导入。G0 后写入采样前进，停止后的 FAT 含 `/nc1020.state`，实际文件 99,384 字节并得到 SHA-256。

把该停止会话导出的 SD 逐字节交给第二个新服务阶段，使用同一填充后的 Flash 启动。来宾报告恢复状态。复核两次保留 SD 原始 FAT，状态文件大小和 SHA-256 一致。两个阶段最终各释放 Flash，活动租约均为零。使用的 ROM、NOR 与 factory 内容摘要不变。在两个直接捕获的 240×135 帧中，非黑像素分别为 120 与 4,063，作者图案匹配均为零。跨服务存档为 `PASS`，显示为 `PARTIAL`。 [同会话 Flash、SD 与帧证据](evidence/nc1020-storage-display-summary.redacted.json)

## SPI/LCD 归因边界

独立的同版本 ESP-IDF v5.4.1 LCD-only 工件中，同核提交与回收三个试验均为 960/960。跨核的两次未完成记录分别提交并回调 299、603 次，任务只回收 298、602 次，另一次达到 960/960。独立停住的探针保留一个已经入队的完成项，显示任务等待 SPI 总线锁，信号量不可用，且未记录锁所有者，两核均在 idle。该观察与旧 SDK 的交接问题一致。

原版 BIN 保留交接受影响的驱动条件。上游 ESP-IDF 5.4 分支提交 `8ee2dce0d6758d0dd8c782587ef5d8715c8c26e3` 修正 SPI 总线锁的获取与释放逻辑。这是原版显示问题的归因线索，原版发生局部绘制时的同会话等待状态为 `NOT RUN`。另一个原版加入 GPSPI 跟踪的试验观察到 DCS 写窗口和行负载，仍为 `PARTIAL`。跟踪产生的时序变化使它独立于正常定时对照。 [Espressif SPI 总线锁修正](https://github.com/espressif/esp-idf/commit/8ee2dce0d6758d0dd8c782587ef5d8715c8c26e3)

替换原版 SDK、浏览器、实体设备、常驻服务更新和 Burner 提交均为 `NOT RUN`。


源码主线为 `9d27879b55bcc6abc2c0e77163853867f19f1a6b`。更新范围为文档、项目快照和有界复验证据。51 项文档检查、项目快照及变更范围通过。 [模拟器主线](https://github.com/m5agent/m5stack-esp-emulator/commit/9d27879b55bcc6abc2c0e77163853867f19f1a6b)
