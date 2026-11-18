# CardputerDict ADV 原版发音的宿主转发修正

- 日期为 `2026-11-19`，原生 virtual-device validation，结果 `SIM_VERIFIED`。
- 固定同一原版、初始 Flash、SD 种子、Device Service 和 Reviewer 0.29.2，仅将宿主转发解释器固定为 Python 3.13.15。
- 校时和 TLS 双向字节验证通过，缓存 MP3 为 10,605 字节，三份归档与 API 回执中的 PCM 均为同一 84,992 字节。
- 此前 Python 3.9 的部分结果及收集器错误原样保留。

[报告](report.md) · [运行清单](run.json) · [有界证据](evidence/adv-relay-python313.summary.json) · [上一轮排空和部分结果](../../README.md)
