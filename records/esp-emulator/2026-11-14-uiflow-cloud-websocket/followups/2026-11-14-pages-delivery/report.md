# Pages 交付报告

## 背景与固定范围

本次将取得完整本地资格的精确静态包交付到公开 Pages，再验证远端字节和实际 HTTPS guest。
站点源码 `70ef503fc2fb8b2c787fa9065e2952f525c40099`、清单 `54fc8d8fe023ef0d86e3bfdea3d3db37599a2f59404c54fdb8920d466bd14a8c`，
包 SHA256 `8c25e92e124fc0d323afd51b13c8ce05719e54167c1cbc5d1a3507eab28b9b98`。
此前本地 72/72、2993 项完整资格已[独立归档](https://github.com/m5agent/agent-work-logs/tree/6f06108d3b68b35f679e3c37aebeac60972434fe/records/esp-emulator/2026-11-14-uiflow-cloud-websocket/followups/2026-11-14-pages-qualification)，这里不把它改称线上完整门禁。

沿用同一导出与 42 个既有运行资产，没有重建 WASM 或变更 guest oracle、timeout、输入路径。
变化限于已验证静态网页的交付；native C6 GPIO 与云网络修复不因此进入 WASM。
最终文档提交为 `12c01eab89c41794ecea4b5b4d3eadf63999feab`，不能替代实际站点源码身份。

## Release 下载与部署

实际 [release](https://github.com/m5agent/m5stack-esp-emulator/releases/tag/pages-20261114-70ef503f)
及 tag 指向上述源码。API 读回 isPrerelease=true、isDraft=false、isLatest=false。
下载包为 186574444 字节，SHA 与资格包一致；重新打开归档逐项验证 2179 文件，无额外、遗漏或重复，
0 下载重试。归档相同不单独证明线上已更新，因此继续独立验证 workflow、deployment 与 HTTPS。

[prepared workflow 43511659965](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43511659965)
于 `2026-11-13T21:33:39Z` 完成 success。head SHA 对应站点源码，实际输入 release tag 与下载产物一致，
prepare/deploy 两 job 均成功。关联 deployment `7776988548` 状态 success、日志关联相同 run，
环境为[公开 Pages](https://m5agent.github.io/m5stack-esp-emulator/)。这证明实际发布流程，
不证明 hosted 全设备功能门禁重新通过。

## HTTPS 2179 文件字节核对

实际读回于 `2026-11-13T21:34:36.564343+00:00` 至 `2026-11-13T21:37:31.994459+00:00` 执行。
完整清单 2179/2179（含 42 runtime）共 304564570 字节全部与资格导出匹配，无首次错误、无重试。
前后 manifest 均为上述 SHA、439371 字节。原始约 1 MiB 报告留在私有证据区，公开仅保留其
SHA/大小、有界结果和独立闭集复核；不复制整个大报告。

## 实际 HTTPS 两例

执行时间 `2026-11-13T21:39:33.975106+00:00` 至 `2026-11-13T21:42:41.095295+00:00`。
相同固定源码 runner 通过远程静态宿主加载两个不同 CoreS3 fixture，原始报告均为
`remote-static-host`，实际 site、输入固件、执行固件、profile/clock、ROM、JS/Worker/WASM 与预期身份吻合。

| 示例 | 实际检查 | 固件输入/执行 SHA256 | 范围 |
| --- | --- | --- | --- |
| stock-reference | 49/49 PASS | `78961297e751ec9c743b4cdf89cc2c137e7e2c801dda3ead9df2ea45d59fbd3f` | 项目原参考示例，冷启动及重开 |
| wallclock-candidate | 34/34 PASS | `e9500994f4c0e1708ec35f5a46146225ac330d210a2427e1fc537c33635d9554` | 独立候选 fixture，冷启动及重开 |

共 83 项检查、0 JavaScript error。实际 trusted DOM pointerdown/up 包含负控位置与目标位置，
650 ms 请求持按，经客体 LVGL click 和 PIR 双向串口响应验证；pause/resume 及重开各有真实输出。
10 份 RGB565 的像素长度与哈希重算一致，输入/输出/清理逐项见[两例摘要](evidence/https-cases-summary.json)。
每个 fixture 都有 cold/reopen，合计 4 guest 生命周期；分别验证 pthread 在 iframe 移除前归零、
移除后的 CDP target 销毁以及 normal owner 退出，不把容器移除本身当作 Worker 清理。
终态观察中本次 guest Node 与 headless Chrome 均为 0，没有由观察者强杀进程。

浏览器为 Chrome `157.0.8103.52`，exe SHA
`5441ca699b9eff7763f2f10765e2e8409a4b05f38917826b5247f6f6bb3b0c6b`。
执行前后身份相同，20 次 10 秒间隔采样一致，最大间隔约 10.011 秒；采样不是连续监控。
两份 child 未记录自身 version，原值保留 `NOT_RECORDED`，由实际包装流程身份单独绑定。
没有拿本地 72 例的浏览器历史填充当前缺失字段。

独立审计重新核对原 snapshot/serial/RGB565/输入/退出、报告闭集和 HTTPS 资产，结果 PASS。
另对已有 stock desktop Clicks:1 与 candidate 390 宽布局截图实际视觉复核：guest/模型显示可读匹配，
检查的画面未见错误横幅。视觉仅覆盖这些截图；其余输入和 Worker 结论来自独立原始数据审计。

## 文档收尾、限制与恢复

文档提交 [`12c01eab89c41794ecea4b5b4d3eadf63999feab`](https://github.com/m5agent/m5stack-esp-emulator/commit/12c01eab89c41794ecea4b5b4d3eadf63999feab)
已推 main，父提交为实际站点源码。逐文件验证仅 10 个 docs 文件变化，产品代码、runtime、服务与
原测试未改。初次文档合同运行 51 项、1 项失败，原因为两个新证据页面未登记 freshness 台账；
原失败日志保留。补齐两行台账、更新 Pages reviewed 日期并再生成 snapshot 后，原测试 51/51 PASS，
snapshot 复核也 PASS；此前 runtime coverage、peripheral catalog、QEMU profiles 和 snapshot
四个 validator 首轮已通过。diff/scope、UTF-8/隐私与同行复核 PASS。

[文档摘要](evidence/docs-closeout-summary.json)分别记录失败与修正，不把本次文档验证称为新的 guest
执行。最终 [main CI 43515767914](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43515767914)
于 `2026-11-13T22:04:47Z` 完成 success，head SHA 为上述文档提交；platform-contracts 和
network-namespace-policy 两个 job 均成功。本记录因此在声明的交付范围内 PASS，实际站点/guest
仍绑定 70ef，文档 CI 不被描述成重新运行 guest。

历史 hosted 完整 gate FAIL/PARTIAL 没有重跑。线上两个固定 fixture 不能证明全部 23 设备、
任意上传固件或云端配对/WebREPL。旧 WASM 不继承 native 模型与网络修复；native control PONG
缺失仍独立 FAIL。本地额外 CoreMatrix stock 的前 iframe pthread 未采集也不由当前 CoreS3 两例补齐。
没有物理/RF/功耗验证，没有提交 Burner。此次没有执行回滚；后续如需恢复，应保留现有失败/成功记录并独立验收恢复结果。
