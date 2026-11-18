# Tab5 双核 PMU 暂停与 WFI 对照报告

此前原版 UserDemo 复验观察到 CPU0 等待 CPU1 暂停状态位。为区分状态位读回和 CPU1 实际执行行为，本轮用两个独立的合成应用，在普通 Device Service 会话分别执行忙循环和 WFI 对照。服务固定到 `57d397462e661e608e7c3ae2a878e80527d08e84`，原生 esp-emu 1.1.0 P4 运行时、ROM、eFuse、C6 工件及两个合并固件的 SHA-256 均记录于回执。[原版启动对照](../../README.md) · [本轮数据](evidence/busy-vs-wfi.summary.json)

## 执行结果

| 对照 | 暂停前 | 写入 PMU 暂停码 `0x86` | 写入解除码 `0xff` |
| --- | --- | --- | --- |
| CPU1 忙循环，1 个会话 | 心跳有进展 | bit 1 由 0 变为 1，心跳增量为 0 | bit 1 回到 0，心跳增量为 51,432 |
| CPU1 WFI，2 个冷启动会话 | 无中断时不自行返回，第一枚中断触发一次返回 | 保持 2,500 虚拟微秒。bit 1 保持 0，第二枚中断期间无额外返回、中断处理或心跳 | 第二枚中断得到处理，WFI 累计返回 2 次，随后产生 4,000 次心跳 |

WFI 夹具的反汇编包含实际 `wfi` 指令，且 CPU1 只打开测试中断。两个冷启动记录的串口标记一致。停止后保留会话证据，所属服务及来宾进程退出，活动租约为零。[串口标记与证据包哈希](evidence/busy-vs-wfi.summary.json)

## SDK 对照和结论

ESP-IDF v5.4.2 的 ESP32-P4 HAL 写入暂停码后等待对应状态位。v5.5.4 在发出暂停请求后取消这项等待，源码说明目标核心已在 WFI 时状态位可能保持为 0。固定原生后端在本轮两种状态下均实际暂停并恢复 CPU1。状态位单独为 0 无法判定 UserDemo 的 CPU1 是否已被有效暂停，也不足以归因其启动故障。[v5.4.2 HAL](https://github.com/espressif/esp-idf/blob/v5.4.2/components/hal/esp32p4/include/hal/cpu_utility_ll.h#L29-L38) · [v5.5.4 HAL](https://github.com/espressif/esp-idf/blob/v5.5.4/components/hal/esp32p4/include/hal/cpu_utility_ll.h#L31-L43)

## 复现和范围

用回执固定的 ESP-IDF v5.5.4 构建 `esp32p4`、早于 rev 3、16 MiB Flash 的两个镜像。固定原生 Tab5 P4/C6 配置，通过标准 HTTP API 上传、导入并创建普通会话。忙循环夹具把任务固定在 CPU1，CPU0 读取暂停请求前后心跳和状态。WFI 夹具把任务固定在 CPU1，屏蔽除一条跨核心中断外的其他中断。先在无暂停请求时触发第一枚中断并等待一次返回。下一次 WFI 时，由 CPU0 经 SDK 发出暂停、延迟 1,500 虚拟微秒、触发第二枚中断、延迟 1,000 虚拟微秒，再解除暂停。核对回执中的 `TAB5_STALL_*` 标记、会话摘要和 ZIP。两种状态由不同测试镜像产生。

本轮没有重跑原版 UserDemo、实体硬件或其他芯片修订，也未验证 C6 网络。未提交 Burner。未修改源代码或原有验证记录。
