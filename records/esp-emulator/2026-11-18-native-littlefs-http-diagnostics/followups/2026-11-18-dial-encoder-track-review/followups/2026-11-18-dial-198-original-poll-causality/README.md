# Dial R1F30 8 ms 复现与 5 ms 采样读回

2026-11-18，原版的原生虚拟设备验证。Device Service 1.98.0 中，未追踪的发布版再次出现 8 ms 漏选，64 个边沿全部送达。另一个带只读采样的诊断二进制复现三次 5 ms 漏选，并用实际 GPIO 寄存器读回重算了原版计数。

诊断二进制的 22 次 8 ms 动作均通过，发布版 8 ms 错误仍待同场采样，快速旋转保持 **PARTIAL**。

[报告与复现](report.md) · [结构化记录](run.json) · [逐动作证据](evidence/dial-r1f30-198-pc-comparison.summary.json) · [此前 1.97 的 8 ms 漏选](../2026-11-18-dial-197-original-cadence/README.md)
