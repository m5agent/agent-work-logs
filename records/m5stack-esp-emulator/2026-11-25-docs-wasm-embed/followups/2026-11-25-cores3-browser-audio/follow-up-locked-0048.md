# CoreS3 0048 完整构建复测

## 构建和产物

按锁定的上游 QEMU、Emscripten 3.1.50 和 91 个补丁全量构建，重新编译全部 QEMU 对象。生产导出器生成只在显式选项下加入音频控件的预览站点。预览的 2,187 个资源均复核过大小和 SHA-256，包含重新生成的对应源码包。

| 对象 | SHA-256 |
| --- | --- |
| 站点清单 | 06a005130e1334bc2918d529cf6d7d802c545aae3f3801eea063175f692beaec |
| 运行时清单 | e3b65a2887354fada0f49e3b769257e177b5bb800cfbc5946ee3d489653ba432 |
| WASM | be385f43df0b97624f0c3a39f4cff43b16b216a63c9320c06b5f8fd30d7806fc |
| 对应源码包，35,280,660 字节 | 3846be62915724c3693bda797cd52386b1baf1db4641b55c344a227c7bfd52ae |
| 源码锁 | 07afe8bb4894d31121c165dd7b61aa3e9f98400fe859eab081683a7afb604ddc |

实跑站点的源码提交为 8f2cf7230455b6bf8ac46f8b66a983b772fa0d10。将同一改动接到合并后的 #270 后，复核补丁、源码锁和生成站点。原始运行时继续对应实跑时的完整源码。生产 Pages 默认仍保留音频关闭。

## 完整构建上的实际浏览器结果

在同一份导出站点上依次执行。原始 Arduino WAV 通过真实固件上传和 microSD 绑定启动。UIFlow2 使用默认 v2.5.3 编程环境，导入原始 Python 文件，从正常编辑器执行和中断。两例的 AudioContext 均在真实 Start 手势内恢复为 running，并连接实际浏览器输出目标。额外的 AnalyserNode 观察数字信号。测试记录了真实屏幕和各自的正常退出。

| 例程 | 本次同会话原始画面 | 48 kHz 浏览器输出 | 停止清理 |
| --- | --- | --- | --- |
| Arduino WAV | 320×240，11 帧不同，最终 RGB565 为 d0c86fd98bc8e8f46b185065841fa1c54406840115950355f298b8c0a38ae882 | 756,992 个采样，575,037 个非零采样，最高 RMS 0.00549 | QEMU exit 0，AudioContext 关闭，6 个 Worker 全部退出 |
| UIFlow2 Mic | 320×240，录制、播放、完成画面指纹均命中，原编辑器中断应答 | 159,744 个采样，119,996 个非零采样，最高 RMS 0.12377，最大频率档 445.3125 Hz | QEMU exit 0，AudioContext 关闭，6 个 Worker 全部退出 |

两例均无队列丢弃或欠载。麦克风权限调用计数为零。其虚拟 440 Hz 输入在实际 I²S1 RX 和 GDMA 路径中使用。分析档宽为 23.4375 Hz，所报告的档位数值来自数字分析窗口。

早期 WAV 复跑的阈值高于原始固件的数字输出电平。早期 Mic 复跑暴露 signed HEAP8 字节拼接导致的波形失真。两次 FAIL 保留在单独的早期记录，完整构建使用已修正的适配器。WAV 的原始数字音量仍较低。Headless Chromium 数字结果覆盖上述两个文件路径，物理主机 audibility、跨浏览器兼容、生产部署和文档嵌入均未验收。

[完整构建浏览器摘要](evidence/locked-0048-browser-audio.summary.json) · [早期预览结果与对照](report.md) · [同路径复跑步骤](code/replay.md) · [原始 Speaker 资源待验收项](speaker-follow-up.md)
