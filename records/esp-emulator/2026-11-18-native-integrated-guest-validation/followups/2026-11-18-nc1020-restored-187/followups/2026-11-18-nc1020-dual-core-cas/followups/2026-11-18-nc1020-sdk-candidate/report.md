# NC1020 原版对照与 SDK 回移候选

## 背景

原版 NC1020 的有界 TCG 追踪捕获了 LCD 总线 LOCK 被设置、CPU0 清除 pending 后因持有者为空而退出的次序。另一个原版停刷现场的队列状态不同。 [此前原版双核追踪](https://github.com/m5agent/agent-work-logs/blob/5a6d032a13e35523cd59034c27372d09c5131287/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-restored-187/followups/2026-11-18-nc1020-dual-core-cas/README.md)

## 候选出处

Espressif 提交的 ISR 退出分支在待处理工作清除后检查 LOCK，选择等待持有者并唤醒它。候选基于 SDK v5.4.1 的隔离副本，对应上游的两处可执行 C 变更。 [ESP-IDF 上游提交](https://github.com/espressif/esp-idf/commit/2521f3887a78559496c0d2599b0f368ddc24e02b)

## 构建与成对执行

基线 SDK 为 ESP-IDF v5.4.1，使用固定发布者源码、SDK 配置和 Xtensa GCC 14.2.0_20241119。隔离 SDK 的源码差异仅在 `spi_bus_lock.c`。应用上游两处 C 变更后完成构建，保留旧头文件引出的 `bg_yield` 未使用警告。原版 BIN 和已发布固件保持原样。

仅在候选复验的 Flash 副本替换 factory 应用分区。独立读回确认其余字节完全相同，包括 ROM/NOR 数据。三次原版和四次候选使用相同 K132 运行时、SoC ROM、时钟设置和 FAT32 存档。七个证据 ZIP 及 21 张采样帧均核对哈希。

| 内容 | 原版 | SDK 回移候选 |
| --- | ---: | ---: |
| 完整显示 | 1/3 | 4/4 |
| 部分显示 | 2/3 | 0/4 |
| 精确存档恢复 | 3/3 | 4/4 |

候选四轮的三次帧采样均逐字节匹配已固定的完整 PNG。原版两轮保留其不同的部分帧和绘制计数。七轮各完成 407 次 SD 单块读取，恢复同一 99,384 字节存档，停机后的 SD 哈希也相同。所有来宾进程结束，临时 Flash 释放，隔离服务停止且租约清零。

## 验收边界

结果覆盖候选在这个已保存状态上的恢复显示。发布者固件未替换，现有原版失败和先前记录继续保留。此样本不估计长期稳定性。实机、浏览器及 Burner 未执行。候选只写入一次性会话副本，回滚方式为释放该副本并继续使用原版 Flash。 [成对执行摘要](evidence/nc1020-sdk-backport-comparison-summary.json)

## 固定源码证据

主分支的对照摘要保留相同输入和各轮证据。 [版本固定的验证记录](https://github.com/m5agent/m5stack-esp-emulator/blob/9df926ec45ffe1c7d9f91f4b98c58d8b23a40769/tests/firmware/cardputer_k132_stock/nc1020-esp-idf-lock-backport-summary.json)
