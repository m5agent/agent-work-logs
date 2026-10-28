# UIFlow2 音频与 Core2 输入收尾报告

## 背景

三设备接口基线轮已经确认 system、网络、协议和多项共享源码缺陷，但仍有：

- StopWatch/StickS3 `playWavFile` 在固定 I2S completion 窗口后阻塞；
- Core2 A/B/C 输入落到无关 GPIO，PWR 回调也不稳定；
- Core2 裁剪 PDM WAV 的测试 oracle 对相位敏感。

本轮在同一 Device Service/visible session 模型内定位并修复这些问题。

## 根因

### ESP32-S3 I2S

虚拟 TX timer 把 DMA completion 和 PCM capture 共用同一个终止条件。超过
`TX_START + 2 s` 或 128 个 descriptor 后 timer 停止推进，而 guest 仍保持
TX 使能并等待驱动 ring 中的 descriptor 完成，最终 `playWavFile` 不返回。

### Core2 A/B/C/PWR

Core2 A/B/C 是 FT5x06 下方触控条，不是通用 GPIO。首次 `0063` 将 A/B/C
映射为同步 pointer 状态，但该分支对每个 key code 都提前 `break`，因此
同一切换块后面的 `Q_KEY_CODE_P` 也永远不可达。PWR 模型没有坏，问题是输入
被触控分支吞掉。

### Core2 Mic oracle

Core2 PDM 输入输出是强裁剪、非对称波形。旧 oracle 用无窗矩形 DFT 搜索峰值，
同一 440 Hz fixture 会随相位选择 395 或 425 Hz 附近的泄漏峰。归一化
autocorrelation 对裁剪不敏感，并可围绕已知 fixture 频率约束 lag。

## 修改

`0062-esp32s3-i2s-continuous-dma-completion.patch`：

```text
TX enabled -> continue descriptor completion
evidence capture -> still bounded by time/4 MiB PCM limit
TX disabled -> stop timer
```

`0063-core2-touch-buttons.patch`：

```text
touch_buttons && key in {A,B,C} -> FT5x06 synchronized pointer -> break
key:P -> AXP2101 power-key event path
```

`verify_mic_recording.py` 改为 expected-frequency-bounded normalized
autocorrelation + parabolic interpolation。平台回归加入强裁剪 440 Hz 波形。

## 执行

最终 runtime：

```text
sha256 03d74d53ff8187c4f0a3b22d34c4e898bdd93b61cfc98432dbbeecd1beb12419
```

最终 Mic/WAV：

| 设备 | record | WAV | 结果 |
| --- | ---: | ---: | --- |
| StopWatch | 440.070 Hz | 440.088 Hz | PASS |
| StickS3 | 440.070 Hz | 440.088 Hz | PASS |
| Core2 | 443.829 Hz | 443.792 Hz | PASS（0.86%） |

Speaker WAV/file：StopWatch 662.146 Hz、StickS3 659.454 Hz、Core2
662.109 Hz。三台 raw 同频 PASS。每台 guest recording state 为 `1 → 0`，
所有 session 都先请求 evidence ZIP，再以 `purge=0` 停止并确认 PID 消失。

Core2 输入：

| 输入 | 路径 | 回调 | remove 后新事件 |
| --- | --- | --- | ---: |
| A/B/C | FT5x06 touch band | `[2]` PASS | 0 |
| P | AXP2101 `0x49` event | `[2]` PASS | 0 |

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | 0062/0063 重放与 QEMU link；定向 C 回归 |
| transport | `PASS` | I2C/FT5x06/AXP2101 与真实 QEMU input |
| device_response | `PASS` | M5Unified callback state 2 |
| data_behavior | `PASS` | Mic/Speaker PCM 与独立频谱/oracle |
| visual_or_physical | `NOT RUN` | 没有物理触控、声学或 PMIC 电气测量 |

平台回归：

```text
Ran 1351 tests in 112.451s
OK (skipped=1)
```

生成器检查：

```text
RUNTIME_COVERAGE_OK
PERIPHERAL_CATALOG_OK
QEMU_PROFILES_OK
PROJECT_SNAPSHOT_OK
```

## 未覆盖项

- ESP-NOW TX/RX/IRQ 仍被 OpenMAC peer routing 缺口阻塞。
- Core2 全部 28 类文档方法矩阵仍为 `REVIEW`。
- 物理触控、扬声器/麦克风声学、PMIC 电气和真机为 `NOT RUN`。
- 六音频会话并发时 StopWatch Mic 在 guest READY 前超时，单会话补跑 PASS。

## 风险与回滚

两个 patch 只改变对应 QEMU runtime 路径。回滚为撤销 `0062`/`0063` 并重新
构建 runtime；不涉及 Flash、凭据或持久设备状态。物理硬件未操作。
