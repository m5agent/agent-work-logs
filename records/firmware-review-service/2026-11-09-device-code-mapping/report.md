# StackChan 和 StickC Plus2 审核路由复验

审核服务在读取模拟器目录前按设备代码查表。补充 `STACKCHAN → stackchan` 和 `STICKC_PLUS2 → stickc-plus2` 后，通过原审核入口分别下载并校验 BIN，完成静态检查，创建两种型号的 QEMU 会话。两次会话均记录到 `flashing`，证明审核器进入了映射后的虚拟设备路径。

复验范围为 virtual-device validation。StickC Plus2 使用原任务版本，StackChan 使用同一项目另一个仍待审的版本。StackChan 原版本已离开待审列表，历史任务停在下载前，原版本复验为 NOT RUN。两项测试都使用本地审核模式。

两次就绪请求均返回 HTTP 408 `ready_timeout`，取证时仍为 `flashing`，串口为 0 字节，画面无可用结果。应用启动、功能交互和物理设备均未得到通过证据。固件和组合镜像哈希、运行模式与状态见[脱敏执行摘要](evidence/virtual-review-summary.json)。

部署时对常驻程序应用两条映射，保留其已有的 SD 复审改动。仓库基线为 `85e6d485644776ef49687a9871050a0fd1c853af`，交付为 `b3d4033fc9de9ea35d345bc6ef9c0eed0732b5dd`。运行 `python3 -m unittest discover -s tests -q`，31 项通过。[补丁](patches/0001-map-review-device-codes.patch)在基线通过 `git apply --check`。如需回滚，撤回两条映射后重启服务。
