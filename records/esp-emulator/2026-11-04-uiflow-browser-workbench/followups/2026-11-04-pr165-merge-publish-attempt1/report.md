# 合并与发布检查点报告

用户已明确授权PR165合并和Pages发布；下载恢复按该发布目标继续处理。
源码合并成功；发布尚未成功。此记录只固定一次状态，不对修复或新站点作预授结论。

## 实际事实

- PR165 merged：2026-11-04T08:28:44Z；merge commit23d38d8dbe91488185dc53eb4cd47dee687df019。
- merge与已测试c3db057d2ee99c022a4116ae72d661c4d39888c6的树均为f892649011246b88cb76e3b2ad2973fe76ec99ee。
- ordinary main CI SUCCESS；它不等于Pages guest/deployment验收。
- 08:29:38Z workflow_dispatch到main，publish=true、base_path=/m5stack-esp-emulator/、service_url为空。
- 首次观察为IN_PROGRESS；随后流程终态failure。独立08:33:56Z快照确认该状态和相同head。
- 失败为SDKsetup之后、QEMU/WASM编译之前的source-download urllib TLS握手超时。
  没有新的WASM编译结果，guest/gate/export/deploy被跳过。现有代码或WASM不因此判FAIL。

公开失败log只保留20,421字节/SHA23767ea6c54786ce29d7469504639bb4a825fd51e0df18bd2a56ba192749345f引用，
未复制原日志、内部端点、机器路径或任何会话/设备标识。

## 验证与复核

新动作仅为一次只读GitHub合并/commit-tree/workflow查询，未起browser/guest/构建或轮询。
相同树只允许复用先前声明的精确固件/运行时功能证据；不代表新Pages已部署或新线上路径通过。
结构化字段及公共链接见summary。可只读复核：

~~~sh
gh pr view 165 --repo m5agent/m5stack-esp-emulator --json mergedAt,mergeCommit
gh run view 41799916700 --repo m5agent/m5stack-esp-emulator --json status,conclusion,headSha
~~~

## 后续与风险

继续按原输入/checksum/准入约束诊断下载传输并准备恢复；首轮失败记录不被后续尝试覆盖。
发布成功、产物身份和线上same-path验收必须在后续独立记录中证实。
未做物理测试；原模型、性能和固件范围边界继续有效。没有不可逆设备操作；无代码回滚动作。

## 后续恢复观察

已在相同23d38源码上发起一次failed-job重跑，attempt2仍在进行中；TLS与锁定SHA未改变。
[单次源码下载探测](evidence/source-probe-summary.json)的9个完整下载均为HTTP200且SHA匹配。
本机结果不证明托管网络已恢复；后续发布与线上验收仍须实际完成。
