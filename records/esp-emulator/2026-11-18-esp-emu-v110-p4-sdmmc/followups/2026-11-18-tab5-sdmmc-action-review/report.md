# Tab5 保存快照复审的 SDMMC 写入证据

## 问题与改动

Device Service 1.90.0 已支持合规 Tab5 原生 SDMMC 槽位 0。Reviewer 0.21.0
会把保存快照复审的卡镜像引用传给 Device Service。原有写入时间戳和复审准入
针对 SPI，导致 Tab5 的动作写入断言在取样前报告不可用。

Device Service 将既有写入时间戳应用到已准入的原生 Tab5 SDMMC 会话。活着的
自有 P4 进程、会话独占的可写镜像、文件类型和预期容量仍是取样条件。Tab5
API 复位轮换媒体身份。Reviewer 仅在 Tab5 明确发布 `sdmmc` 和
`write_stamp: true` 时启用对应断言。原有 SPI 路径保留。

## 执行与证据

| 用例 | 输入和结果 | 判定 |
| --- | --- | --- |
| 候选服务与合成 SDK 探针 | 保存快照复审实际点按 `(360, 640)`。ST7123 中断和 I²C 触点报告进入来宾，松手后执行 FAT16 写入和读回。采样前两次时间戳相同，采样后增加 4,055,813,158 ns。复审完成，停机获得两个文件的精确 SHA-256 | `PASS` |
| 候选服务与 Arduventure 1.0.0 原版 | 实际触摸已接受。卡镜像与文件时间戳保持原样，停机目录无文件。写入断言报告 `sd_write_not_observed`，复审进入人工复核 | 无写入对照 `PASS`，原版写入 `PARTIAL` |
| Device Service 1.90.0 与候选 Reviewer | 原版保存快照复审获得同一 SDMMC 卡收据与停机 FAT16 清单。旧能力未发布写入时间戳，复审跳过该取样 | 挂载 `PASS`，写入 `NOT RUN` |
| 候选 Device Service API 复位 | 使用同一原版和空白卡，不发送来宾输入。新 P4 进程使旧媒体身份失效，卡 inode、SHA-256 和修改时间保持不变。停机后写入时间戳接口返回 409 | `PASS` |

正例的合成固件为 `87cf38e3a282c24c37ba17dde1d5dfedb341a8a2b252f947a1a00898a95ed5e1`。
原版上传镜像为 `e2f228813b719b81c47a8deaa7576f1b83e61e950c6178c5cf570bfaca7b8616`。
同一 32 MiB FAT16 种子为 `758cd5e18a7bd98241cb2849645bb8cc1d6f1646e9eb6cc8985ca0546211cfa1`。
原生运行时、ROM、eFuse、触摸 Part、C6、传输和终态 ZIP SHA-256 均在
[证据摘要](evidence/tab5-sdmmc-action-review-summary.json)。每个 ZIP 校验了 CRC、
清单中的成员哈希和本次会话的存储收据。各轮停止后均无活动租约。

在精确 Device Service 发布提交与 Reviewer 提交的冻结副本上再次执行合成
正例。复审终态为 `done`，两次输入前取样匹配，后续文件时间戳增加
5,389,998,639 ns，两个停机文件的 SHA-256 与首轮一致。第二轮 ZIP
独立校验七个成员。 [冻结发布包复验回执](evidence/frozen-release-replay-summary.json)

同一冻结发布版再次复审原版 Arduventure。触摸已接受，写入时间戳增量为零，
停机卡镜像等于空白输入。写入报告继续为 `sd_write_not_observed`。
[冻结版原版对照](evidence/frozen-release-stock-control-summary.json)

## 复现与边界

使用固定的 ESP-IDF 5.5.4 构建原生触摸与 SDMMC 探针。以经过准入的 SHA 启动
对应 ST7123 实例，将空白 FAT16 镜像上传到 Reviewer 所用的 Device Service，
提交 `sourceMode=saved_snapshot` 的本地 Retry，并对 `touch_center` 设置
`type=sd_write` 和 `retained_file=/TAP.TXT`。保留触摸前帧、窗口内写入采样、
来宾串口、终态 ZIP 和停机后的 FAT 清单。 [固定源和构建步骤](https://github.com/m5agent/m5stack-esp-emulator/tree/15724035425f9d64cb69d752ebb359e4e2458022/tests/firmware/tab5_sdmmc_action)

写入时间戳说明采样窗口出现了落盘，匹配的来宾触摸及写入事件为合成探针建立
动作归因。停机清单说明文件在最终介质中存在。要证明文件由本次执行创建，
还需核对输入介质的目录。实机、热插拔、浏览器、控制器读计数以及同一个
esp-emu 进程内的来宾自行重启本轮均为 `NOT RUN`。未提交 Burner。

若需回退服务行为，使用早先的 Device Service 1.90.0 与 Reviewer 0.21.0。
此轮的旧 API 对照同时验证了新 Reviewer 在缺失该能力时的保守处理。
原始固件、日志、会话标识和可写卡镜像均留在验证环境。
