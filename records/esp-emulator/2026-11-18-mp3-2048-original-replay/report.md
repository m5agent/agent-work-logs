# Cardputer ADV MP3 与 Core2 2048 原版隔离复审

在两套隔离保存快照中复验原版功能。Device Service 1.82.0 源码 `c8a40dee575b944195ed52c7f8dfb8a16a51a8cf`，Reviewer 0.14.0 源码 `ea64e80e3d88e2761b5627545376a1de400cf34f`，原生 Xtensa QEMU SHA256 `7e63fc223c6946ef8b2f44b1510d904aea6cc7c36c21324bb631490a3f325b24`。软件版本和固件字节受校验值约束，两次验证均为 dry-run。

## Cardputer ADV MP3 Player v1.0.0

按保存快照运行同一原版 BIN 和 FAT32 测试镜像，完成 60.011 秒同会话观察。Reviewer 在 48 kHz 单声道 PCM 中测得两个连续窗口为 522.792 Hz 和 522.582 Hz，两段均在 524 Hz 的 8 Hz 容差内。终态 ZIP 的两段数据可按偏移逐字节核对，完整数字 PCM 独立分析得到七个匹配窗口。 [MP3 复审摘要](evidence/mp3-isolated-review.summary.json)

## Core2 2048 Game 1.0

保存快照的原版 app-only 执行得到 `SIM_VERIFIED`。八次拖动覆盖四个方向各两次，帧中的压缩、合并和一次合法 2/4 新砖块均通过独立校验。八张动作帧的摘要与保留证据一致，末帧与终态 ZIP 中的帧一致，ZIP 的虚拟 Flash 中原版 app 字节与来源摘要相符。Reviewer 内置棋盘语义断言为 `NOT RUN`。首次整理独立校验结果时脚本缺少 JSON 导入，随后直接读取同次运行保留的证据完成校验，无额外来宾运行。 [2048 复审摘要](evidence/2048-isolated-review.summary.json)

两次虚拟设备会话均已停止，释放 Flash，活动租约为零。模拟器准确提交的 GitHub CI 两项作业通过，Reviewer 测试 222 项通过。Pages 读取现有发布对应的静态站点和运行时清单，仍属于既有 `70ef503fc2fb8b2c787fa9065e2952f525c40099` 产物。实机、物理声学、浏览器来宾、Pages 新部署和 Burner 提交均未执行。 [准确提交 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44188018262) · [Pages 只读证据](evidence/remote-ci-and-pages-readback.summary.json)
