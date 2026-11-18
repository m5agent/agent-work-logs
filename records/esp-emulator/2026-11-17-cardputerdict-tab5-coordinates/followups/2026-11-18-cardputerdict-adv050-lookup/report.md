# CardputerDict ADV 0.5.0 原版查词

目标是复核固定原版 ADV 0.5.0 的 FAT32 字典查词。原始 BIN 为 2,141,568 字节，模拟 Flash 仅按擦除值 0xff 填充至 8 MiB。三轮均使用 Device Service `929dbf749e4a8ecd6c469fce8aea44120febd03f`、同一原生 Xtensa 运行时和 Cardputer ADV，分别独占虚拟会话。先确认 240×135 非黑画面，再执行五次 Backspace、依次输入 `zorbax`、等待候选画面，按 Enter 后采集结果。虚拟输入由 Device Service 接受。

| 词库状态 | SPI CMD17 总数 | Enter 后画面 | 该对照 |
| --- | ---: | --- | --- |
| 完整词库 | 128 | `zorbax` 与 `MINT CACHE 7319` | PASS |
| 缺正文 | 79 | 未显示指定词条及释义 | PASS |
| 无卡 | 0 | 未显示指定词条及释义 | PASS |

带卡两轮均回读 64 MiB SPI SD 存储摘要。CMD17 是各会话全段日志的读命令计数。缺正文和无卡的最终 PNG 字节相同，二者的读命令和介质回执仍有区别。0.5.0 没有出现此前 0.6.4 的挂载提示，查词结论依据实际 SPI 记录、画面和对照。独立回读检查三个证据 ZIP、全部成员摘要、串口、SPI 日志和最终 PNG，并对三个结果再次运行 OCR。三轮均停止、释放 Flash，活动租约归零。 [三路原生证据](evidence/native-lookup.summary.json)

## 保存快照审核

- **Reviewer 0.17 基线。** 同一原版和完整卡在独立离线保存快照中完成 60.013 秒观察。Enter 对应的取帧和候选画面与直接原生验证逐字节相同，复查 OCR 找到词条及释义。保留 ZIP 的 SPI 日志有 136 次 CMD17。取帧来自同会话的动作附件，ZIP 中另存会话最终画面。该查词路径通过，整单仍为 `SIM_PARTIAL` / `E_INTERACTION_CLAIM_PARTIAL`。更早的启动预检使用了错误机型参数，在目标查词执行前失败。 [0.17 回执](evidence/reviewer017-offline-baseline.summary.json)
- **Reviewer 0.18 区域断言。** 对 `key_ret` 的 240×135 画面，读取从 (0, 41) 起、宽 240 高 38 的区域。以固定的 RGB 像素摘要对比动作前、首次动作后和最终样本。三个会话中动作前均不同于目标值，两份动作后样本均稳定。校验了三个 ZIP 的全部成员并独立重算九个区域摘要。 [0.18 原版回执](evidence/reviewer018-frame-region.summary.json)

| 0.18 离线保存快照 | SPI CMD17 总数 | 稳定区域结果 | 整单 |
| --- | ---: | --- | --- |
| 完整词库 | 136 | PASS，匹配目标释义区域 | `SIM_PARTIAL` / `E_INTERACTION_CLAIM_PARTIAL` |
| 缺正文 | 110 | FAIL，与目标区域不同 | `SIM_PARTIAL` / `E_SIM_FRAME_REGION_MISMATCH` |
| 无卡 | 0 | FAIL，与目标区域不同 | `SIM_PARTIAL` / `E_SIM_FRAME_REGION_MISMATCH` |

三轮均通过启动观察和解码，释放 Flash 并退出独立服务。网络和其他交互结论仍由各自证据判定，本轮未执行网络发音功能。通过隔离 HTTP 读取三条已完成的审核记录，在 Chromium 中确认同一目标画面分别显示“通过”“未通过”“未通过”。浏览器此处仅用于核对 Reviewer 页面。 [页面回读](evidence/reviewer018-ui.summary.json)

Reviewer 候选 `ce92d559873602963e036e8d804a322cf2428823` 的 250 项测试全部通过，采用 Python 3.9 启动器。模拟器证据提交 `72aa245ae0abfbf0b72af4edffa8df56fa8ab93a` 从 `929dbf749e4a8ecd6c469fce8aea44120febd03f` 以来只改变文档与证据，GitHub CI 两项均通过。 [模拟器源码证据](https://github.com/m5agent/m5stack-esp-emulator/blob/72aa245ae0abfbf0b72af4edffa8df56fa8ab93a/docs/evidence/2026-11-17-cardputerdict-stock/adv-0.5.0-summary.json) · [GitHub CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44204118299)

## 复现条件

把自编、未压缩的 StarDict 2.4.2 三词夹具放到 FAT32 根目录的 `dictionaries` 文件夹，使用 `ecdict.ifo`、`ecdict.idx` 和 `ecdict.dict`。直接核对两个 FAT32 镜像的目录和文件内容，.ifo 与 .idx 逐字节相同，完整卡的 .dict 在索引指定偏移存有自编释义，缺正文卡省去 .dict。完整词库的 `zorbax` 释义为 `MINT CACHE 7319. An invented test word.`。以原版 SHA-256 确认输入，通过独立原生 Device Service 会话重复上述输入，分别保留同会话 SPI、画面和存储摘要。 [夹具格式与三个自编词条](../../report.md)

## 验证范围

上述应用行为来自原生虚拟设备。验证对象是指定画面区域和真实的 SPI 请求。命令次数是全会话统计。未执行物理设备、浏览器 WASM 来宾或 Burner 提交。
