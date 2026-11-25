# CoreS3 DualKmeter 标准工作台例程

- 日期 `2026-11-25`
- 结果 `PASS`。锁定 0050 浏览器 WASM 用官方工程生成的原 Python 和真实 I²C 模型通过。普通工作台同一镜像保持预期的无挂接行为。
- 验证层级为浏览器 WASM 虚拟设备验证。Pages、物理模块与热电偶未执行。

[执行与复现](report.md) · [结构化记录](run.json) · [精确构建和同来宾证据](evidence/dualkmeter-workbench.summary.json) · [例程预置 #255](https://github.com/m5agent/m5stack-esp-emulator/issues/255)
