# Reviewer 0.28.0 的常驻切换与 Python 3.9 回读

## 首次切换与回退

候选 `e7e32f19d03f88394dfadb4e9f73fb1a83ea39c0` 通过了隔离 Linux 的 ADV 发音允许、策略拒绝以及初代 Cardputer 对照。首次 macOS 常驻切换遇到 Python 3.9.6 在导入时计算 `str | None` 类型标注，应用启动失败。切换程序执行保护性回退，Reviewer 0.27.0 `f0101b6bb0926a69ef2f8477ae81e991338391f5` 恢复就绪，回读 129 条记录及抽样 ZIP。 [首次候选的同原版功能对照](../../report.md)

## 修订与验证

`37d7675dced42b2b932c51d1ca21bbb8ccfdf7e1` 启用延迟求值的类型标注，范围为发音模块的导入兼容性。原运行环境 Python 3.9.6 运行全部 301 项测试，两套隔离服务完成实际 HTTP 200 就绪回读。初版执行、回退、兼容性预检、功能复验和常驻二次切换分别保留记录。

修订版在隔离的无网卡 Linux ARM64 VZ 重跑同一原版三条审核路径。ADV 允许及初代 Cardputer 允许均达到 `SIM_VERIFIED`，两条各得到同一 84,992 字节 PCM。ADV 拒绝保留预期的策略拦截和零 PCM。三条均核对两份 ZIP、PCAP 与资源清理。

## 二次切换和独立读回

Reviewer 0.28.0 使用 `37d7675dced42b2b932c51d1ca21bbb8ccfdf7e1`，以同一 macOS Device 后端返回 HTTP 200 就绪。129 条记录的数据库、实际 UI/API 与抽样 ZIP 一致。两套 Device Service 保持 `9837c3f84df4383eb74881a1f44fcd3f460daefa`，均提供相同的 OpenAPI 1.99.0 文件。生产来宾与 Linux 常驻路线为 `NOT RUN`，Burner 未提交。

[脱敏回读摘要](evidence/resident-readback.summary.json)
