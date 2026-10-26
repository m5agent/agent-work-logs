# Core2 legacy LVGL flush wait and SPI transaction-done diagnostic

- 日期：`2026-10-26`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 源码版本：
  [m5stack-esp-emulator @ f206175](https://github.com/m5agent/m5stack-esp-emulator/commit/f2061759897955e6017d4aa2a41bd5ba962c35b6)
- Base commit：`7f9f248544fea950fc1b13050f604634ed02637e`
- 环境：macOS arm64；Python 3.13.15；Core2 QEMU retained tree

## 结论

`UIFlow_Core2 v1.15.4` 的 WDT-off late state 已从“未命名 flag/object”
收敛到 LVGL 7 double-buffer flush wait。BIN-bound 分析把 CPU1
`0x40100049` 所在路径绑定到 `lv_refr_vdb_flush`：`lv_disp_buf_t` 的两个
buffer 都有效，`flushing=1`，display driver 的 `wait_cb` 为 null。display
`flush_cb=0x40174758` 在虚拟时间约 44–48 秒执行一次，但 completion
`0x40174884` 与 `lv_disp_flush_ready` 没有出现，frame 仍为 302-byte 黑帧。

`0042` 补上 `SPI_SLAVE.TRANS_DONE/TRANS_INTEN` 状态、IRQ level 和有界对象
word dump。模型可观察到 `trans_done=1/trans_inten=1/level=1`，但 50 秒
WDT-off 窗口仍未执行 completion callback。normal WDT 在 60 秒窗口内继续由
TG0 stage-1 于约 `15.9157 s` 首次 reset，TG1 在 reset 前保持 feed。

因此本轮把一个未知等待点变成了可重放的 LVGL/SPI completion 链诊断，但
`RUNTIME-03` 仍为 `OPEN`。这不是产品修复，也没有取得非空应用帧。

## 关键证据

- 固件 source SHA-256：
  `18d77e28adfacf7e719a167bd0c3450b78357d13cb1d2f2a8b7bccc2248a909a`
- normalized Flash SHA-256：
  `152127c808b9212e3a5b55dd9e0a2d24e71b902e225452b67db381c76caba1cc`
- QEMU binary SHA-256：
  `59ee022723974aa4ff7d2305f4e46ac049d3eb59632f292d5de8600bf9ede052`
- `0042` patch SHA-256：
  `bc520f7983ea1061d065201d4960b633daf4c0c189258fc96ef397c3c9104c5a`
- 平台测试：`544/544 PASS`
- Core2 文档契约：`12/12 PASS`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall、selected Ruff 与 diff check：PASS
- `0042` retained-tree reverse apply check：PASS
- 产品 CI：
  [40254086653](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40254086653)
  `platform-contracts` 与 `network-namespace-policy` 均 PASS

## 文件

- `report.md`：调查路径、模型改动、验证边界和回滚；
- `run.json`：机器可读提交、检查项和剩余状态；
- `evidence/verification.summary.json`：命令、哈希、运行时观察、CI 和
  `NOT RUN` 范围。

## 未覆盖项

- 没有 matching `UIFlow_Core2 v1.15.4` ELF/MAP；
- SPI completion 没有在 guest interrupt matrix/ISR/queue 路径中闭环；
- normal-WDT legacy 启动仍为 `FAIL`，没有 setup/REPL 或非空应用帧；
- 没有运行完整 67-case UIFlow2 外设矩阵；
- 没有物理 PSRAM/cache timing、RF、功耗、电气或真机验证。
