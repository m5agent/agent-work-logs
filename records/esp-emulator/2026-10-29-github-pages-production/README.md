# ESP Emulator：正式 GitHub Pages 上线

- 日期：`2026-10-29`
- 结果：`PASS`
- 工作类型：`code_change`
- 问题来源：用户要求合并本地修复、WASM 工作和正式 GitHub Pages 托管
- 源码版本：[`m5agent/m5stack-esp-emulator`](https://github.com/m5agent/m5stack-esp-emulator)
  @ [`8e47c6ba`](https://github.com/m5agent/m5stack-esp-emulator/commit/8e47c6ba83c042398d767a8d56ff47c16b927181)
- 记录落库版本：[`e5a94bbb`](https://github.com/m5agent/m5stack-esp-emulator/commit/e5a94bbba93bfa1785a72a0140a9f4de9be53bbf)
- 正式站点：<https://m5agent.github.io/m5stack-esp-emulator/>

## 结论

原仓库正式启用 GitHub Actions Pages，并在 main 上完成固定源码
C/QEMU、LittleFS 和静态资源构建，Actions 内真实 CoreS3 guest 验收，
Pages 部署以及部署后的公开 HTTPS 独立复验。

本地 TIMG WDTFEED 修复已由 main 提交
[`a07f49b7`](https://github.com/m5agent/m5stack-esp-emulator/commit/a07f49b7a8b5e680a24faf08541c7329e7ced760)
和
[`8e47c6ba`](https://github.com/m5agent/m5stack-esp-emulator/commit/8e47c6ba83c042398d767a8d56ff47c16b927181)
收口；CoreS3 C/QEMU WASM 工作台由
[PR #16](https://github.com/m5agent/m5stack-esp-emulator/pull/16) 合并。

## 关键结果

- Pages [构建 job](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40719197233/job/122925130720)
  `13m53s` PASS，[部署 job](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40719197233/job/122933361298)
  `14s` PASS；
- 正式 URL HTTP 200，manifest 声明 `1922` 个资产，`service_url` 为空，
  `firmware_bundled=false`；
- 公开 HTTPS 真实 CoreS3 C/QEMU 独立验收 `21/21` PASS；
- 覆盖共享内存、真实 RGB 帧、触摸正反例、PIR 双向状态、QMP
  暂停/继续、四档布局、停止/重开、Worker/iframe 清理和零 JavaScript
  错误；
- 页面未访问 `/api/v1` 或本机模拟器接口；
- C/QEMU WASM
  `716f3b6a8750335613da2897be0933d1497965962d0dc1b3f2754ebf76316c89`；
- 最终 Flash
  `78961297e751ec9c743b4cdf89cc2c137e7e2c801dda3ead9df2ea45d59fbd3f`；
- ROM
  `b5c7090cc22efce51c1323cef31ca96fcd673a5b1d1b1017e219d393f2659913`。

## 文件

- `report.md`：部署、复验、边界与回滚
- `run.json`：机器可读结果
- `evidence/public-qemu-browser-summary.json`：脱敏公开验收摘要
- `evidence/public-site-1440.png`：正式站点 1440px 截图
- `patches/`：不适用；源码已在主仓合并
- `code/`：不适用；复验入口位于主仓

## 未覆盖项

- `cores3-wasm-vm-div8` 的默认墙钟调度、长期稳定性与 Flash 持久化；
- 网络、音频、其它设备/Unit 和任意固件兼容性；
- 物理硬件、RF、声学、光学和电气验证。
