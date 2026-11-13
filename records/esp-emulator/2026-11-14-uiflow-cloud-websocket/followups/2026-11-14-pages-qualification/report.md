# Pages 资格报告

## 背景与范围

身份能力协商和 COI worker 修复影响静态网页。旧网页允许用户连接独立 HTTPS Device Service，
其 native frame 条件请求可返回 304；旧 worker 对 null-body 状态重建 Response 的问题已有同路径
native 浏览器证据。纯 WASM 不发送该 native frame 条件请求，本记录验证静态导出整体回归，
不宣称为纯 WASM guest 修复了同一网络问题。

前次固定源码 a5990e720a8c79310456bf5868141f4cfd50afe8 的本地门禁在 44 例通过后，因网页
与旧服务身份能力协商缺口停于用例边界，剩余 28 例 NOT RUN。它没有完整资格，且不是 28 个
guest 失败。更换到本次源码后重新完整执行，未拼接旧 PASS。

## 固定环境与改动边界

本次源码 `70ef503fc2fb8b2c787fa9065e2952f525c40099`、站点清单 `54fc8d8fe023ef0d86e3bfdea3d3db37599a2f59404c54fdb8920d466bd14a8c`。
冻结 5664 个源码文件、179 个依赖文件和 2179 个导出文件；package lock 和清单哈希见
[准备摘要](evidence/preparation-summary.json)。该文件是准备阶段历史快照，保留当时
PREPARED_NOT_QUALIFIED/PENDING；终态由[资格摘要](evidence/qualification-gates-summary.json)独立记录。

23 款公开设备，无候选 profile、无固件/ROM 打包、默认 service URL 为空。
[42 个 runtime 资产](evidence/runtime-assets-summary.json)完全复用既有浏览器产物，
runtime producer commit 与本次网页源码 commit 分别保留。没有把本轮 native C6 ISR 修复
或 native 云网络能力移植到旧 WASM。

Chrome `157.0.8103.52` 的可执行文件 SHA256 为
`5441ca699b9eff7763f2f10765e2e8409a4b05f38917826b5247f6f6bb3b0c6b`。
执行前后哈希相同，393 次 10 秒间隔采样均匹配，最大采样间隔 10.011 秒；这只能支持抽样
期间的一致性，不能称为逐时刻连续监控。75 份报告中自身版本记录 72 份、缺失 3 份；若只看
完整 72 例则是 70 份记录、2 份 CoreS3 fixed 未记录。缺失字段没有被补填。

## 执行与结果

运行从 `2026-11-13T20:08:19.449Z` 至 `2026-11-13T21:13:01.685Z`。
采用现有 scheduler，phase=all、requireAll、无设备筛选、单 worker、硬件 ANGLE，ready budget
600000 ms；实际命令和固定 runner 见[复现步骤](code/README.md)。只判定终态退出与最终报告。
这是功能回归，不能用时长推导性能结论。

| 层 | 实际结果 | 证据边界 |
| --- | --- | --- |
| 23 UIFlow 编辑器 + 23 按钮 + 键盘/机身触摸 | 48 PASS、2335 检查 | 271 次实际程序、213 项输入、925 行 fixture 串口观察、93 份 RGB565、270 个 CDP target 销毁 |
| fixed | 24 PASS、658 检查 | 72 份同运行快照、64 份 RGB565，按每例最大快照输入数累加为 82（不是跨快照去重后的全局输入数） |
| 完整门禁 | 72/72、2993 检查，0 重试/跳过/NOT RUN | 每个 child exit=0，无信号；所有控制器和报告哈希匹配 |
| 额外 pixel / COI | 5 + 13 host 控制 PASS | 非 guest；COI 含 8 正向、4 预期旧行为负控及 worker 更新 |
| 原版 CoreMatrix stock | 额外 1 guest PASS | 5 启动标记、216 USB 内容字节、8 输入边沿、9 同会话画面判定；前 iframe pthread fence 未采集 |
| 包闭集 | PASS | 2179 文件、186574444 字节；无重复、目录外或额外文件，各项字节等于已验证导出 |
| release / Pages / HTTPS | NOT RUN | 本资格记录不能代表后续真实 HTTPS 子集通过 |

每例分别绑定输入/执行固件 SHA、ROM 名称与 SHA、JS/Worker/WASM、controller、profile、clock
及原 child 报告 SHA。ROM 未随站点打包，其收据与冻结 profile 相符；离线审计没有另行下载 ROM。
固件 SHA 是实际启动/合成镜像身份，不是运行后 mutable Flash 全量读回。

fixed 的屏幕路径保留真实按下/松开串口行、计数与 framebuffer/纹理对应；headless 路径
保留实际 RMT QOM LED 数据和输入计数，明确没有屏幕。均匀 LED 颜色不证明非均匀空间映射或 IMU。
CoreS3 两种 fixture 保留真实 DOM 触摸、负向点击、LVGL callback、PIR 双向响应、暂停/恢复及
重新开启的生命周期证据。清理分别检查 pthread 在 iframe 移除前退出、移除后的 engine/Worker
实际销毁；额外 stock 的缺项单列，不继承这一完整门槛。

最终所有 72 child 正常退出；终态观察中属于此 gate 的 Node guest 进程和 headless Chrome
均为 0。纯浏览器 lane 无 Device Service lease，也没有借用 native 服务结果。

## 历史与观察修正

旧 44/28 中断、旧 hosted FAIL/PARTIAL 原样保留，见[历史摘要](evidence/history-summary.json)。
本轮键盘 runner 在完成前将初始 FAIL 写入 checkpoint，观察者曾把它误当终态；随后按真实
child exit 和 scheduler 判定。没有中断进程、变更源码、重试或改写原报告；该例最终 PASS。
准备记录的 partial 状态和 48 例阶段性摘要也保留，防止后来的 PASS 擦除当时边界。

## 打包、交付及回滚

完整 gate、前置检查和浏览器绑定通过后才创建精确包。包装流程与原 package 收据分别固定，
并再打开归档逐文件核对。产物 SHA 与字节数见[包摘要](evidence/package-summary.json)。
该包尚未发布，未执行 release 或 Pages workflow，也未做远程下载或 HTTPS guest。
拟用新 prerelease tag 且不更新 latest；后续发布须引用本记录的真实完整归档 commit，并另记
远端字节读回与 HTTPS 子集，不能把本地 72 PASS 改称 hosted 全门禁 PASS。

本次资格收集不修改产品源码或服务，故没有产品回滚动作。若后续交付失败，应保留失败记录，
停止推进该产物；再次部署旧资产也必须按独立交付记录验证，不能抹去新旧结果。

## 剩余限制

物理硬件、RF、功耗、光学、电气行为及安全边界未验证。没有提交 Burner。
原云固件 control PING 无 PONG 的超时/重连仍是 native 独立 FAIL；本地 Pages 回归不解决它。
3 份报告缺自身版本、stock 前 iframe fence 未采集、纯 WASM 运行时能力未更新，以及历史
hosted 完整门禁失败均保持明确边界。
