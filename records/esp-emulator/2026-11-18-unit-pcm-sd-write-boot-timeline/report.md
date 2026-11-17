# U197 PCM、SD 写入采样和应用加载时间线

## Dial U197 原版驱动到数字输出

Device Service 源码 `4ee0e106386f064fcb95f901e6141b8cde6198f3` 增加 Dial 原生 AudioPlayer WAV 附件。会话创建时按顺序挂接不可变的 16 kHz 单声道 s16le WAV，单个 Unit 最多 16 条。能提供 PCM 的 QEMU 才会上报对应能力。数字读取使用同会话的 `audio.pcm?source=unit`，证据 ZIP 的输出为 `audio/unit-output.pcm`。读取受 `audio.read` 控制。

用同一 vinylM5Dial 1.0 R1F30 原版与 QEMU SHA-256 `7e63fc223c6946ef8b2f44b1510d904aea6cc7c36c21324bb631490a3f325b24` 执行 Port B 正向和循环。原版 UART 自播及两次旋钮动作对应 1 → 4 → 2，独立读回主频 440.079、706.055、523.949 Hz，恢复播放为 524.009 Hz。暂停和停止的观察窗内输出字节数保持稳定。另一个两轨运行到达曲尾后，输出按 1 → 2 → 1 切换。两个会话的七个 HTTP 字节窗均能用原 ZIP 的原始 PCM 片段回核。集成服务再跑同一原版与运行时，四个读回主频为 440.040、705.882、524.009、524.009 Hz，逐窗与新 ZIP 的字节哈希一致。损坏 WAV 在挂接前被拒绝，旧运行时在分配租约前返回 HTTP 409 与 `runtime_model_gap`。

独立的原生模型证据直接读回 166,298 字节数字样本，按三个曲目和停止后重启位置逐字节比对夹具。暂停后的恢复延续原位置，停止后再次播放从曲目起点输出。曲尾回绕另有逐字节对照。未配置音频时验证了原有 UART 路径。为验证 16 MiB 上限，专门将捕获预置到离上限差 128 字节，实测最后 128 字节与曲目实际前缀一致，文件抵达上限后保持稳定。该容量实验的预置区是测试数据。

验证范围为虚拟 N9301 的数字样本。MP3 解码、物理 SD、声学输出与浏览器为 `NOT RUN`。所有实际会话均停止、释放 Flash、活动租约为零。 [服务和原生模型证据](evidence/dial-u197-pcm-summary.redacted.json)

## PaperDIY SD 写入采样

`storage/sd/write-stamp` 对可写 SPI SD 镜像返回纳秒级修改采样，并绑定会话、归一化 Flash、源 SD 与媒体身份。比较同一挂接中的前后采样，能观察输入窗口内是否落盘。Cardputer 系列以外，此次验证 PaperDIY 原生热插拔路径。

单个来宾进程在卡未插入时挂载超时。插卡后实际读取种子并写入文件，SPI 计数增加 6 次 CMD24，采样前进。拔卡后请求被拒绝，重新插回同一镜像产生新的媒体身份，来宾重新挂载并读回旧文件。只读回读阶段有 CMD17、零新的 CMD24，采样保持稳定。最终停止后回读实际 64 MiB SD，FAT 数据中的 `/PROOF.BIN` 为 32 字节。媒体身份也绑定 worker 实例，worker 更换有独立单测。同一固件、QEMU、ROM 与源 SD 的旧服务对照也实际写入 6 次 CMD24，最后 SD 和文件摘要一致，但两次同卡在位的采样请求仍返回 HTTP 409 `sd_write_stamp_unsupported`。写入采样的验收针对落盘变化，文件内容由来宾及停机存储证据独立确认。 [PaperDIY 热插拔与写入凭据](evidence/paperdiy-sd-write-stamp-summary.redacted.json)

## Tab5 旧启动记录的应用加载时间线

新增的应用加载时间线从保留 UART 的 bootloader 装载行提取全部匹配计数，并保存最后 16 条。98TAB5 的保留原版证据为 32 条，保留后 16 条，CarPlay 为 1 条。对两个已停止的历史会话执行只读 API 回放，新 `/crash` 结果与同会话新 ZIP 的诊断一致，串口摘要与旧 ZIP 完全相同。

M5TabOS 的旧原版 ZIP 由同一解析器得到 7 条。它的 HTTP 回放为 `NOT RUN`。三个输入都重新回读 ZIP 串口，已有 crash 字段保留。该时间线给出 bootloader 报告的应用位置，原版就绪、稳定性和复位原因没有在本轮重新执行。隔离审计启动零来宾，最终无活动租约。 [历史日志的逐项回放摘要](evidence/tab5-app-load-retained-summary.redacted.json)


## 源码与校验

模拟器主线为 `d99d4d00340b8ef3265a8b9d31252996e1f41d8c`，Device Service API 为 1.80.0。完整平台运行 2,408 项，跳过 10 项，其余通过。51 项文档以及版本清单、项目快照、运行覆盖、外设目录、QEMU 配置、构建配方和变更范围校验通过。各路径可独立撤销对应模型或服务提交。未提交 Burner。 [模拟器主线](https://github.com/m5agent/m5stack-esp-emulator/commit/d99d4d00340b8ef3265a8b9d31252996e1f41d8c)
