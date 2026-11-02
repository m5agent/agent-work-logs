# PR #80 合并报告

## 任务与范围

用户要求合并当前唯一开放的 [PR #80](https://github.com/m5agent/m5stack-esp-emulator/pull/80)。
审核对象为 head `34c176f07812630ddfac3e8879208f35f00a0f1d`，base
`8dd390ff810032b3cbdf7c2d18fda4e97dade8bd`。本次没有新功能修复；
根因分析不适用。PR 将原来只有视觉外壳的 AtomS3U 与 Atom VoiceS3R
接入独立 QEMU 板级、设备 manifest、partial 外设契约、candidate runtime
coverage、Grove 接线入口及设备专用 console 探针。

## 合并门槛与交付

确认 PR 的可合并状态、当前 head 的检查、review 状态及已有同路径执行证据。
head CI runs：
[41403408938](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41403408938)、
[41403398446](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41403398446)，均已成功，合计 4/4 jobs；平台测试 `1,729` 项为 `1,719 PASS + 10 skipped`。
普通 merge commit：`930d7183e68f2e6abdca6803b10b42d3b82626d1`，合并时间 `2026-11-02T07:03:13Z`；
merge CI：[41403793498](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41403793498)，终态 `PASS`。
head 与 merge 的 tree 均为 `744cbccec280e2f18a987eb505d1d9215bf2cb9b`。
本地 `main` 有 6 个已有未提交文件，因此没有执行快进；用户改动保持原样。
此次合并没有新建 patch、固件或部署。

## 虚拟设备证据及归属

本记录沿用 PR 提交前已有的 native QEMU regression runner 执行，
本次任务仅回核已有原始串口、镜像/PCM 产物与 CI，未新启 guest。
以下是 **virtual-device validation** 的限定范围，不代表物理测量。

| 设备 | 已有同 guest 结果 | 未覆盖 |
| --- | --- | --- |
| AtomS3U / `m5atoms3u` | 官方 UIFlow2 v2.5.4；`M5_BEGIN_OK`、`BOARD 138`、`RGB 0x204060`；RMT/GPIO 完成 4 帧、96 symbols、0 errors；按键状态 false→true→false | IR、PDM 麦克风、Grove Unit 数据面、USB CDC |
| Atom VoiceS3R / `m5atomvoices3r` | 官方 UIFlow2 v2.5.4；`M5_BEGIN_OK`、`BOARD 145`、`SPEAKER_RUNNING 1`、`STATUS ok`；官方 `Speaker.begin()/tone(440,900)` 经 I2S1 TX DMA 捕获 53,248 B PCM，其中 52,293 B 非零 | NS4150B 使能、实际发声、IR、MEMS 麦克风、Grove Unit 数据面、USB CDC |

固件、测试镜像、运行时二进制与 PCM 的完整 SHA-256 以及固定源码证据链接
见 [派生摘要](evidence/validation-summary.json)。摘要不包含 raw 日志、内部端点、
主机路径或唯一物理设备标识。已有 AtomS3U 与 Atom VoiceS3R 执行使用不同的
QEMU 二进制哈希，分别保留，未将它们表述为同一 runtime 构建。

回核时两测试镜像 SHA-256 与 12 个串口 marker 均匹配，PCM 的字节数、
非零字节数与 SHA-256 均匹配。当前二进制 SHA-256 为
`4ca3e17d5c9317e7ccbd121a815e02c603790f4a9ce5f94bafe420a3e973f727`，
与两次历史运行不同；历史二进制已被替换，本次未重建或重跑，
因此当前二进制不作为历史执行的运行时证据。

## 复现入口

固定源码：[head `34c176f07812630ddfac3e8879208f35f00a0f1d`](https://github.com/m5agent/m5stack-esp-emulator/tree/34c176f07812630ddfac3e8879208f35f00a0f1d)。
按 PR 中运行时层序构建原生 QEMU，并使用对应官方固件与原探针；
原执行命令属于仓库回归开发路径：

```bash
PYTHONPATH=platform/tools python3 tests/uiflow2/run_device_matrix.py --device atoms3u --flash-transport direct --out-dir /tmp/atoms3u-matrix
PYTHONPATH=platform/tools python3 tests/uiflow2/run_device_matrix.py --device atom-echos3r --flash-transport direct --out-dir /tmp/echos3r-matrix
```

此处记录原回归复现命令，不表示本次再次执行。今后代理触发一般固件功能测试
仍应使用专用 Device Service 的可见会话并保留证据。

## 限制与回滚

两款设备的契约保持 `partial`，runtime coverage 保持 `candidate`，
不宣称设备外设全覆盖，也不继承给其他主机或不同固件 SHA。
本次新 guest 执行、全矩阵、物理硬件、RF、声学、光学、电气均 `NOT RUN`。
任意第三方固件和其余视觉主机/Unit 未验证。
若需要回滚，在远端主线对最终 merge commit 使用标准 revert；本次不执行回滚。

合并后主线 CI 两项均成功，平台 `1,729` 项中 `1,719 PASS + 10 skip`，四个生成器检查全部通过。
