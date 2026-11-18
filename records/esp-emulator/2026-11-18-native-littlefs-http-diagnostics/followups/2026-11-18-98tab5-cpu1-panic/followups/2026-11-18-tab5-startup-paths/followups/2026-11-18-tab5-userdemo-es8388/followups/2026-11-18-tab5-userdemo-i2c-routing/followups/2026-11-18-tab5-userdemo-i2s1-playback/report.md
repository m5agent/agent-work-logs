# Tab5 UserDemo 原版 I²S1 播放对照

## 候选范围

[I²C 路由对照](../../report.md) 显示已发布 GT911 Part 接管 HP I²C0 后，独立 ES8388 与 ES7210 寄存器设备不会收到事务。隔离候选在原板 Part 中为两个地址提供各自的控制寄存器、写入读回与复位状态。原触控和 BMI270 接线保留。候选模块 122,387 字节，固定 Rust 1.88.0，四项 Part 测试通过。候选工具、源码和模块摘要保留在验收记录中。 [ES8388 参考](https://media.digikey.com/pdf/Data%20Sheets/ITW%20Chemtronics/ES8388.pdf) · [ES7210 参考](https://files.waveshare.com/wiki/common/ES7210_DS.pdf)

所有执行使用未经修改的发布版 UserDemo V0.4、同一官方 esp-emu 1.1.0 后端和隔离的常规 Device Service 1.90.0 HTTP 路径。仅测试进程准入候选 Part 摘要。原版冷启动得到多色仪表盘和真正的 native 720×1280 PNG，真实 codec 读写计数也增加。 [源码锚点](https://github.com/m5agent/m5stack-esp-emulator/commit/57d397462e661e608e7c3ae2a878e80527d08e84) · [运行绑定和证据](evidence/userdemo-codec-i2s1-playback.summary.json)

## 动作对照

通过设备服务导入原版固件、创建独立 Tab5 会话并收集 PNG。两组 I²S1 各运行约 45 秒，均先通过 `POST /api/v1/sessions/<id>/input` 点击 Music Test 原生坐标 `(640,417)`。两组实际显示同一张含 PLAY MUSIC 的弹窗。待定位到相同 PNG 后，播放组点击 `(474,270)`，随后界面显示 STOP。空闲组保留该弹窗，未点击播放。实际点击各取得 7 次 GT911 报告及 7 次来宾确认。

| I²S1 观测 | 点击 PLAY MUSIC | 按钮保持空闲 |
| --- | ---: | ---: |
| 同一按钮画面前的非零 16 位样本（启动声） | 91,366 | 91,366 |
| 对照点之后的 PCM 字节 | 3,010,560 | 3,367,680 |
| 对照点之后的非零 16 位样本 | 1,477,609 | 0 |

使用 native `--i2s-wav` 和 `--i2s-instance 1` 捕获数字输出。停止后验证 RIFF、48,000 Hz、双声道、16 位 PCM 和数据边界。默认 I²S0 的双点击对照仅留下 44 个全零保留字节，后端报告没有采到传输。I²S1 同时具有可复查的界面转移和启动声对照，因此可以将新增非零数据归于该动作。WAV 是同一已固定来宾的独立原始输出，停止前业务证据 ZIP 与停止后 WAV 分别核验。原始音频与画面仅保留校验摘要。

停止前取证，随后以 `purge=0` 停机。四次会话均核对 ZIP CRC 和清单，来宾与隔离服务退出，租约归零，原始固件和后端保持原始字节。

## 适用边界

候选仍为隔离诊断，没有合并、生产准入、常驻更新或 Burner 提交。此结果覆盖原版仪表盘、GT911 触控和数字 I²S1 播放。实体扬声器、麦克风、模拟电气特性、CarPlay/UIFlow2 回归和浏览器均未运行。
