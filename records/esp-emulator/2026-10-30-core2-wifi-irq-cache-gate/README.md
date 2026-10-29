# M5Stack ESP Emulator Core2 WiFi IRQ cache gate

- 日期：`2026-10-30`
- 结果：`PARTIAL`（virtual-device validation）
- 工作类型：`code_change`
- 问题来源：`RUNTIME-03` legacy Core2 cache-disabled panic
- 源码版本：`m5stack-esp-emulator @ 4b99fa0a16de5232337ebd0c01a7dc232d5ead60`
- 交付：PR #52 已合并为 `0563a0a01772403d563463398a3607462e0ffe87`
- 环境：macOS arm64、Device Service `/api/v1`、QEMU virtual Core2

## 结论

WiFi MAC level 在 Flash cache handoff 期间被注入 cached ISR，是
`Cache disabled but cached memory region accessed` 的直接触发路径。
`0092` 将 per-CPU instruction-cache-ready 状态从 DPORT 送到 INTMATRIX；
cache disabled 时仅暂存 WiFi MAC source，cache restore 后重放 retained
level。cross-core、timer 和 cache-illegal source 不受门控。

默认 per-vCPU budget、normal WDT、`icount shift=2` 下，同一 legacy
firmware 不再出现该 panic，串口到达 BOARD/APIKEY/boot markers，并渲染
原厂 API Key 页面。随后仍进入 `TG0WDT_SYS_RESET`，因此这是 cache/WiFi
IRQ 子问题修复，不是 `RUNTIME-03` 关闭。

## 关键证据

- Pre-fix QEMU：
  `54d31e90e2eff273b17f11388015e9bf16a1cf6877fbf7681c207eb73b68286f`
- Post-fix QEMU：
  `a4cfa2b8c3aa7e62b11423fa456c57ec01da7c7e43086a90bdded0eec6241249`
- Original firmware：
  `4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- Effective Flash：
  `b30f3014b75f762f50be3284010502e047b3bd0494b0f0b72a673c2756baffd7`
- Post-fix frame：
  `320x240`、`75,559` nonblack pixels、`512` colors
- Frame SHA256：
  `737df08a0c5d21fe23a46e38f79b7a580508f8dfa7c63c9bc552be19a3106c96`
- Core2 UIFlow2 device group：`6/6 PASS`
- Platform full suite：`1,599` run，`1,598 PASS + 1 skip`

## 文件

- `report.md`：根因、实现、执行证据、边界和回滚
- `run.json`：机器可读记录
- `evidence/verification-summary.json`：脱敏检查摘要
- `evidence/frame-api-key-summary.png`：API key 已遮盖的虚拟设备帧
- `patches/`：不适用；patch 已作为源码文件交付
- `code/`：不适用；测试位于源码仓库

## 未覆盖项

- normal-WDT stable startup、setup/REPL 和完整用户应用
- WiFi association/DHCP completion
- physical hardware、RF、电气、物理 cache/PSRAM timing
