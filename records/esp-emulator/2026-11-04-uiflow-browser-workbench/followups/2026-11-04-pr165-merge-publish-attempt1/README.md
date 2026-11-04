# PR165合并与首次Pages发布尝试检查点

- 日期：2026-11-04
- 结果：PARTIAL；合并/同树绑定/普通main CI通过，发布尝试因source-fetch TLS超时FAIL。
- 类型：report；用户明确授权合并与发布，未保留对话标识。
- 来源：[PR165](https://github.com/m5agent/m5stack-esp-emulator/pull/165)，[发布workflow](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41799916700/attempts/1)。

PR于08:28:44Z合并到main。merge23d38…与已验证c3db的Git树同为f8926490…，
可复用先前限定虚拟设备证据；本检查点没有新guest或物理执行。
08:29:38Z启动publish=true流程；08:31:39Z源下载TLS握手超时，尚未进入QEMU/WASM
编译，guest gate/export/deploy均未运行。不能写成代码或WASM失败，也没有新站点验收。

[普通main CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41799809400)SUCCESS与发布失败分开记录。
[先前公开记录](https://github.com/m5agent/agent-work-logs/commit/89383e5e9f98968e4fdcdf0c66ac1ba28b35aa85)保留原功能/host验证范围。

- [report.md](report.md)：事实、复核方法和后续边界。
- [run.json](run.json)：结构化记录。
- [evidence/summary.json](evidence/summary.json)：精确commit/tree、工作流参数及日志byte/SHA。
- patches/code不另附；未改变源码、输入锁或测试标准。

传输恢复、后续发布结果及线上同路径验收由独立followup记录；当前均无新增通过结论。

## 后续恢复观察

已在相同23d38源码上发起一次failed-job重跑，attempt2仍在进行中；TLS与锁定SHA未改变。
[单次源码下载探测](evidence/source-probe-summary.json)的9个完整下载均为HTTP200且SHA匹配。
本机结果不证明托管网络已恢复；后续发布与线上验收仍须实际完成。
