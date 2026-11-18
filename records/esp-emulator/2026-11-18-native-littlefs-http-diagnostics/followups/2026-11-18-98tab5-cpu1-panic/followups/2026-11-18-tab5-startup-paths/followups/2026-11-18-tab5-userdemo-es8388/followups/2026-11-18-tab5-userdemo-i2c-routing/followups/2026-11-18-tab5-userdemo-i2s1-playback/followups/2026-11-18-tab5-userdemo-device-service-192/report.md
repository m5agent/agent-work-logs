# Tab5 UserDemo V0.4 的 Device Service 播放取证

[前一次虚拟设备诊断](../../report.md)验证了原版 UserDemo 的 GT911 操作和 I²S1 数字输出。本次在普通 Device Service 的上传、会话、触控、停机和证据 ZIP 路径复现播放，并以同一原版固件空闲对照区分动作后的信号。

## 精确冻结包复验

最终复验使用 Device Service 1.92.0，源码 `1c2eb72d3b7e517e2ceb487c408708a5b800a8c8`，OpenAPI SHA-256 `87f44a1b3180ccc9cc6e8d77e39e260f4734890a848b4fc9840908fe20181ccd`。两组均启动官方 esp-emu 1.1.0，使用 GT911/ILI9881C 和未修改的 UserDemo V0.4。录音随创建会话显式开启，两组租约均为 120 秒。[精确 OpenAPI](https://github.com/m5agent/m5stack-esp-emulator/blob/1c2eb72d3b7e517e2ceb487c408708a5b800a8c8/docs/device-service.openapi.yaml) · [复现配置与接口](https://github.com/m5agent/m5stack-esp-emulator/blob/1c2eb72d3b7e517e2ceb487c408708a5b800a8c8/docs/device-service-api.md#tab5-userdemo-i2s1-speaker-output)

两组均以原生坐标 `(640,417)` 点击 Music Test，在对话框出现后取样本偏移。播放组继续点击 `(474,270)`。两组进入 Music Test 的触控和实际播放触控均收到 7 条已确认的 GT911 报告。约 45 秒内两组均无软件复位。

| 停机后的同会话证据 | 播放 | 空闲 |
| --- | ---: | ---: |
| 完整非黑帧 | 17 | 17 |
| 动作标记之后的 PCM 字节 | 2,749,440 | 3,001,920 |
| 动作标记之后的非零 s16le 样本 | 1,346,574 | 0 |

运行中读取返回 `409 audio_capture_pending`。使用 `purge=0` 停机后，普通 `GET /api/v1/sessions/{id}/audio.pcm` 分页读取 48 kHz 双声道 s16le PCM，范围字节与同一会话证据 ZIP 一致。独立复核验证两份 ZIP 的 CRC、清单、各文件摘要、固件身份和帧摘要。停机保留历史、释放可变 Flash，活动租约归零，来宾和独立服务均退出。[冻结包与早期暂存复验](evidence/final-http.summary.json)

此前 A2 在录音准入完善前独立复现同一 HTTP 数据路径，播放组有 1,100,356 个动作后非零样本，空闲组为零。随后 A3 和首版冻结包均使用显式录音通过 A/B；后续冻结包复验先覆盖对非 Tab5 会话的兼容性修订，再覆盖生成项目快照后的最终源码。[A2 独立核验](evidence/candidate-http-a2.summary.json)

## 录音准入和旧固件回归

设备服务对配置中准入的原版 UserDemo Flash 哈希加载 codec Part。默认会话仍可进入仪表盘，未启动 WAV 捕获，PCM 请求返回 `409 audio_unsupported`，证据 ZIP 不含 PCM。仅当创建时提交 `speaker_capture: true` 才启动 I²S1 捕获，最长 180 秒且不可续期。真实 HTTP 准入测试在首版冻结前的 `4c8142ae` 源码验证了 180 秒边界、续期拒绝后的期限保持、错误字段类型、超长租约和其他固件的拒绝，三类拒绝请求均未获取会话或租约。[录音资源保护](evidence/speaker-policy.summary.json)

Rust 1.88.0 默认构建与原 GT911 Part 的 WASM 逐字节一致，codec 变体连续三次构建摘要一致。资源保护完善前的隔离比较中，原版 CarPlay 使用旧 GT911 Part，完整出帧并响应触控。以同一旧 Part 强制 GT911 的原版 UIFlow2 复现既有 DSI 无帧结果，70 秒内 35 次取帧不可用。两组均未开启录音，PCM 读取都返回 `409 audio_unsupported`。[Part 构建](evidence/part-build.summary.json) · [旧固件回归](evidence/legacy-route-comparison.summary.json)

归档时已在主分支回读该源码。最终平台测试通过，共 2,445 项，其中 8 项跳过。

## 验证范围

本记录覆盖实际原生触控、来宾显示和虚拟 I²S1 数字信号，以及 Device Service 的显式准入、停机后 PCM 和证据 ZIP。实体扬声器、麦克风输入、浏览器、录音中的复位、Reviewer 保存快照与 Burner 提交均为 NOT RUN。
