# ESP Emulator PR #14 合并与 Core2 启动复验

- 日期：`2026-10-27`
- 结果：`PASS`（issue 的公开最小启动路径）
- 工作类型：`issue`
- 问题来源：GitHub issues #2/#3，PR #14
- 源码版本：`m5stack-esp-emulator @ 47af9e76f89912028db06d9dee0b0bcc5425c852`
- PR head：`d0bdd33fc34945ddf424401ed45dc4feccb6e11a`
- 环境：macOS arm64、Python 3.12.14、从合并版源码重新 clone/构建的 Xtensa QEMU、可见 Device Service `/api/v1` session

## 结论

PR #14 在 Linux CI 首轮因 test-only C harness 的 signed/unsigned 条件分支被
`-Werror` 拒绝；contributor 以 `d0bdd33f` 修复后，platform 与 network jobs
全绿，PR 已合并为 `47af9e76`。

从合并版 `main` 独立冷构建 runtime
`bcd439bc57bae37834b784933585c697e3e5d9e7226955159fc7cd2272931dbc` 后：

- direct display、Widgets、LVGL 与 offline network 四个可见启动 session 全部
  `PASS`；
- 实际 LVGL frame 可读，不再出现全宽撕裂；foreground bbox
  `[12,27,217,40]`，14 rows，最长连续 foreground run 16；
- `WLAN.active(True)` 在 `181 ms` 返回，`isconnected()` 为 `False`，不可达
  NTP send 在 `1 ms` 产生 bounded `OSError(118)`，随后绘制 `loading...`；
- 两个连续显式 Wi-Fi session 均完成 scan/association、DHCP DORA、受控 HTTP
  和双向 pcap payload；每个 capture 35 packets、2 TCP flows；
- session 均 ZIP-before-stop、保留历史，Flash 释放且 QEMU PID 退出。

结论只覆盖 issue #2/#3 的公开最小启动路径和合并后的虚拟设备。原始私有完整
应用归档、旧 UIFlow1 LVGL7 `RUNTIME-03` 和物理硬件不继承该 PASS。

## 关键证据

- 合并 commit：`47af9e76f89912028db06d9dee0b0bcc5425c852`
- runtime SHA256：`bcd439bc57bae37834b784933585c697e3e5d9e7226955159fc7cd2272931dbc`
- source receipt SHA256：`bc9b3986b7622740bfe8a892abb0ae81e30fee75c4b7ef21220a5dbae380fdcd`
- 17 patches / 109 source files，`bootstrap-unit-runtime.py --check` PASS
- startup runner：4/4 PASS
- radio runner：2/2 PASS
- PR CI：`platform-contracts` PASS、`network-namespace-policy` PASS

结构化 session、firmware、frame、pcap 和 SHA 见
[evidence/summary.json](evidence/summary.json)。

## 文件

- [report.md](report.md)：PR 审阅、构建、执行和边界
- [run.json](run.json)：机器可读记录
- `evidence/summary.json`：合并后独立复验摘要
- `evidence/frames/`：display、Widgets、LVGL、offline-network 最终 PNG
- `patches/`：不适用；补丁以 PR #14 和合并 commit 为权威入口
- `code/`：不适用；正式 runner 已随源码 commit 合并

## 未覆盖项

- 原始 issue #2/#3 的私有完整应用归档未取得，完整业务初始化 `NOT RUN`。
- 完整 67-case peripheral matrix 未在本独立复验中重跑；PR 声明为
  66 PASS / 1 FAIL。
- 旧 UIFlow1 LVGL7 `RUNTIME-03` 未关闭。
- RF、功耗、电气、机械、光学和物理硬件均为 `NOT RUN`。
