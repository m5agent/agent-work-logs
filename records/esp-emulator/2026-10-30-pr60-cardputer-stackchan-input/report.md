# ESP Emulator PR #60 Cardputer/StackChan 输入与响应合并报告

## 背景

- 来源：[PR #60](https://github.com/m5agent/m5stack-esp-emulator/pull/60)。
- 作者：`yuyun2000`。
- Base：`3fc436e4aa99176ef3a4f7a2d35d25c973659219`。
- Head：`444632fd04dcedd637bfb61f0971bd18d4e1f7cb`。
- 需求：恢复 Cardputer-ADV 的真实键位输入和显示方向，并让 StackChan
  触摸在舵机事务与 UI 重绘期间保持可响应。

## 快速合并审核

- PR 状态：非 draft，`MERGEABLE`，`CLEAN`。
- PR head CI：platform contracts 与 network namespace policy 均成功。
- 范围：`52` 个文件，`8,897` additions、`89` deletions。
- 文件类型：全部为 patch、源码、测试、JSON/Markdown 证据或锁文件。
- 安全扫描：无私钥、Bearer、凭据赋值、MAC、二进制/NUL、超 1 MiB 文件或
  冲突标记；新增 loopback 地址仅用于本地浏览器测试服务器。
- 没有致命或阻断问题，因此按用户规则直接合并。

## 改动

### Cardputer-ADV

- 将电脑键盘的 Shift/Alt/grave/Fn 及 56 个物理键映射到固件实际键码。
- 从实例局部坐标和 MADCTL 状态判断显示方向，避免部分绘图后丢失方向信息。
- 修正 ADV 玻璃安装方向。
- 新增 patch、方向/安装契约测试和真实浏览器输入/显示 probe。

### StackChan

- 保持原 SCS UART 舵机 API，但由真实 MicroPython 后台线程执行事务。
- Touch、显示、Si12T 和供电 I2C 保留在前台，使用有界队列和局部绘图。
- 不延长输入脉冲，不由宿主状态伪造固件响应。
- 新增 Arduino 参考、轮询间隔、触点与资源清理 probe。

## 合并

- Merge commit：
  `867ce788b3b42e0b9c55429cd9272781ffd15cb0`。
- 合并方式：普通 merge，保留贡献者 7 个提交。
- 远端 head 分支已删除。
- 合并后主分支 CI：
  [40997493078](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40997493078)。

## 验证

### CI

- platform：`1,680` 项，`OK (skipped=10)`。
- QEMU profile、peripheral catalog、runtime coverage 与 project snapshot：
  PASS。
- browser/preview contracts：PASS。
- offline Unit evidence：PASS。
- network namespace policy：PASS。

### 虚拟设备

- Cardputer 最终 V5：`33` 项通过。
- StackChan 最终 V5：`24` 项通过。
- Cardputer 覆盖双 Shift/Fn/grave、56 键、四方向/四角旋转、局部更新。
- StackChan 运动中触点 `104.800/302.020/802.660 ms` 通过；最大轮询间隔
  `165 ms`，不承诺任意短脉冲。
- 原 Arduino BSP 的屏幕/舵机并行、FT/I2C 读回与负控通过。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | 67-patch WASM、CI compileall、生成器与锁文件 |
| flash | PASS（virtual-device） | 固定 Cardputer/StackChan 虚拟设备会话 |
| transport | PASS（virtual-device） | 键盘矩阵、显示方向、SCS UART、I2C/Touch |
| device_response | PASS（virtual-device） | 真实固件输入和 StackChan 触点 probe |
| data_behavior | PASS（virtual-device） | Cardputer 33/33、StackChan 24/24 |
| visual_or_physical | PARTIAL（virtual-device） | 浏览器帧/方向与触点通过；物理显示和机械 NOT RUN |
| delivery | PASS（远端） | merge commit 已推送且远端 CI 两个 job PASS |
| local-main-sync | PARTIAL | 主 worktree 有 6 个原有改动，ff-only 被安全拒绝 |

## 验证边界

物理 Cardputer 键盘、LCD 光学方向、StackChan 机械运动、伺服供电和电气
时序均未执行。V4 的 Stop 后 engine CDP target 未在预算内消失，后续清理
不能覆盖该失败，资源回收仍为 `PARTIAL`。标准 all-admitted Pages 发布门禁
和本轮完整 native QEMU 矩阵均为 `NOT RUN`。

## 风险与回滚

回滚应整体 revert `867ce788b3b42e0b9c55429cd9272781ffd15cb0`，不要改写
PR head 或贡献者提交历史。主工作区现有未提交文件没有被 stash、reset 或覆盖。
