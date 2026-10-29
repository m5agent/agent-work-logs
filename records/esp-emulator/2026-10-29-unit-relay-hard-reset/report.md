# ESP Emulator Relay/Relay2 hard-reset boundary 报告

## 背景

- 来源：`UNIT-HOST-36`
- 现象：legacy GPIO hard reset 清除寄存器，但不通知 output listener；Relay/Relay2
  的 `previous_output` 和 transition counter 保留 reset 前状态。
- 目标：让 GPIO 与 Unit 的 reset 顺序可重放，并证明 reset 后的高低变化在新
  execution interval 内正确计数。

## 结论

- 状态：`PASS`（virtual-device validation）
- 根因：复位后 derived state 没有失效；旧 listener 基线跨 reset 泄漏。
- 改动：新增 `0087-unit-hard-reset-output-boundary.patch`；共享 GPIO reset
  建立 route/level 后调用 reset observers，再执行正常 line notification。
  Relay/Relay2 从 post-reset pad 重定 previous 状态并清零 transition。
- 兼容：Unit bootstrap 使用 `qemu-unit-runtime/0003`–`0006` forward ports，
  历史 Core2 诊断 patch 原字节保持不变。

## 证据

### 代码或配置

```text
GPIO reset:
  clear registers / establish reset routes
  notify reset observers
  publish effective line change through normal listeners
  update transition IRQ

Relay reset observer:
  previous = post-reset pad
  transition counters = 0
```

### 执行

- 环境：macOS Apple Silicon；AtomS3R UIFlow2；Device Service `/api/v1`
- 固件：`ab4dd742a342f85037c3c0cb2c67c037bf5eef7cf429bee131d2227d4a404e3d`
- pre-fix QEMU：`9aca9a8db5143ad133510795cd228ed8ac23c388ea197267d7b2b4750e58eb82`
- fixed QEMU：`e318b2b748d6e982cd2e592a1b991ec930a8e9501cf02a0c19925022a656b373`
- 执行方式：同一 guest 先拉高，调用 `POST /api/v1/sessions/{id}/reset`，随后
  分别驱动 gpio-1/gpio-2；停止前请求 evidence，并以 `purge=0` 停止。
- GitHub CI：PR 两个 run 与 merge commit main run 均为
  platform-contracts + network-namespace-policy PASS。
- PR #36 已合并，merge commit 为
  `16580f97228908c3d0f11dcbec71f7f9a530a747`。

pre-fix：

- 单 Relay reset 后 counter 仍为 `2`，warm low 后变 `3`。
- Relay2 reset 后 level `0/0`，counter 仍 `1/1`。

fixed：

- 单 Relay reset observer 立即给出 counter `0`。
- Relay2 reset 后 `0/0`；gpio-1 高后 `1/0`，gpio-2 高后 `1/1`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | 38-patch source receipt；完整 `xtensa-softmmu` 冷构建 |
| transport | PASS | 真实 Device Service HTTP、QMP reset、串口 marker |
| device_response | PASS | QOM Relay/Relay2 level/counter 与 guest 驱动一致 |
| data_behavior | PASS | pre-fix stale counter；fixed reset zero + independent post-reset transitions |
| visual_or_physical | NOT RUN | 无触点/线圈/负载/电气或真机测量 |

## 验证边界

只验证 AtomS3R 同固件的单 Relay 和 Relay2 数字 GPIO 路径。其它 host/model、
FlashLight reset、Preview reset、机械保持状态和 controller 级 reset 不继承。

## 风险与回滚

改动限于 opt-in reset observers；未注册的 peripheral 继续使用原 GPIO reset
路径。回滚源码 commit `22828390` 或反向应用 `0087` 可恢复旧行为；旧行为会
重新暴露跨 reset transition 泄漏。
