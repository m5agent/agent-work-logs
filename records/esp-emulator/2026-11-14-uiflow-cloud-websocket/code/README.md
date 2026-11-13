# 离线复现与公开摘要

本目录脚本不联网，也不执行固件。它从私有 Device Service `evidence.zip` 中读取 PCAP、串口和 manifest，再调用固定源码版本的 `uiflow_cloud_status.py` 观察器，输出可公开的白名单摘要。绝不把原始 ZIP、BIN、截图或配对码放进记录。

## 依赖与版本

- Python 3.12 或更新版本；只使用标准库。
- `esp-emulator` 中含观察模块的固定 checkout。固定观察器提交为 `a5990e720a8c79310456bf5868141f4cfd50afe8`；将此值填入 `OBSERVER_COMMIT`。main 或部署是否完成另由交付证据证明。
- guest 原版 BIN SHA-256 为 `5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded`；本记录的两次参考运行使用相同原生运行时哈希。
- 观察器是有界 UIFlow 证据观察工具，不是通用 TCP 分析器。脚本使用固定版本的内部解析接口，因此 checkout 与记录中的观察模块哈希必须一致。

## 从私有 ZIP 生成摘要

由操作者设置 `CHECKOUT` 为固定源码 checkout、`PRIVATE_EVIDENCE` 为私有证据目录、`OBSERVER_COMMIT` 为最终公开观察器提交。变量值不要写入公开报告。

```sh
python3 code/summarize_private_evidence.py \
  --tools-dir "$CHECKOUT/platform/tools" \
  --zip "$PRIVATE_EVIDENCE/evidence.zip" \
  --case default-baseline \
  --source-commit ffa621cdcf8422005b7fdf66afdee1be7c5fbba7 \
  --observer-source-commit "$OBSERVER_COMMIT" \
  --runtime-identity "$PRIVATE_EVIDENCE/runtime-identity.json" \
  --terminal-state "$PRIVATE_EVIDENCE/terminal-state.json" \
  --output evidence/default-baseline-redacted-summary.json
```

授权身份运行使用 `--case authorized-identity`。后续候选使用 `candidate-default`、`candidate-authorized` 或 `follow-up`，写入新的摘要文件，不能覆盖参考失败证据。`--source-commit` 是操作者提供的 guest 执行源码身份，不会从 ZIP 自动证明；`observer_module_sha256` 则由脚本对实际加载的观察器文件计算。

脚本约束：ZIP 不超过 64 MiB、PCAP 不超过 8 MiB、串口不超过 8 MiB、单份 metadata 不超过 1 MiB、输出不超过 64 KiB。只读取指定成员而不解压整个 ZIP。异常只输出固定 unavailable 状态，不输出输入路径或异常原文。`--runtime-identity` 仅提取运行时 SHA；`--terminal-state` 仅提取 stopped 与 Flash 释放布尔值。

## 重做执行对照

1. 使用同一合法获取的原版 BIN，先核对原始 SHA；固定 guest 源码、运行时和板型。
2. 在专用虚拟设备会话中运行默认身份，保存同会话串口及 PCAP。
3. 使用操作者自己有权使用的云端设备身份运行独立对照。保持 BIN、运行时、网络路径一致；不要把真实身份放进源码或报告。
4. 观察窗口应跨过首个控制 PING 之后的 120 秒。只测前几十秒会遗漏本报告发现的第二类故障。
5. 先获取同会话证据 ZIP，再停止会话并保存独立终态记录。随后用本脚本生成摘要。
6. 分别核对 MQTT 非空 code 回复、完整 WS 握手、业务消息、文本与控制心跳、FIN 方向和串口超时标记。配对码获取不代表账号绑定，握手不代表远程 REPL 成功。

两次主机 12 秒对照属于独立诊断；第二次补验了 Accept，一次结果不能覆盖另一次。本目录不附带需要私有身份和在线端点的探针，避免把在线请求与离线摘要生成混合。其发送语义与结果保留在主机摘要中，但没有公开原始网络抓包；不要把这部分描述成可由公开原字节独立重放的 guest 验证。

## 审查摘要

[summary.schema.json](summary.schema.json)描述本脚本输出。序列号、MAC、IP、云端 URL、请求参数、会话标识、配对码、主机路径和任意 peer 文本均不输出。所有证据摘要应严格 UTF-8、可解析 JSON，并通过身份值与敏感字段扫描。被删去的原始资料只能凭哈希在私有归档中追溯。
