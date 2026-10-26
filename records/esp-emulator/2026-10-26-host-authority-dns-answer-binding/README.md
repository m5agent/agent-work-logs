# ESP Emulator Host authority and exact DNS answer binding

- 日期：`2026-10-26`
- 结果：`PASS`（Linux virtual-network policy + Core2 tool-hash rebind）
- 工作类型：`code_change`
- 源码版本：
  [m5stack-esp-emulator @ 6ecaef5](https://github.com/m5agent/m5stack-esp-emulator/commit/6ecaef5ddc4323f3c3919edf4ad25670a64c8c8c)
- Base commit：`e6c40e13d4cc3a3aea81ca5f28ff542f7fa44438`
- 环境：macOS arm64；Python 3.13；Linux arm64 Docker namespace；
  Core2 QEMU + Device Service

## 结论

HTTP Host allowlist 过去用最后一个冒号截断 authority。最小反例证明
`allowed.lab.test:not-a-port`、`allowed.lab.test:443,evil` 等非法 Host
仍返回 200。现在只接受单一 Host header、可选数字端口和 origin-form
request target；userinfo、逗号/多重冒号、端口越界、重复 Host 和
absolute-form 目标都返回 403。

Controlled DNS 的 exact A/AAAA 与 CNAME terminal answer 现在也必须由
allowed endpoint 覆盖；IPv4-mapped IPv6 DNS record 在解析前拒绝。
`allowed_hosts` 与 policy/sandbox 扫描同步采用严格 ASCII DNS label
校验。

Linux arm64 namespace 中同一 StickS3 guest 完成 WiFi、DHCP、controlled
DNS allow/NXDOMAIN、TLS 200/403、pcap、namespace cleanup 和 QEMU reap。
代码变化更新 service/policy tool hash 后，Core2 同一 firmware/ELF 的两批
独立零错峰 `8×120s` 均 `8/8 PASS`，合计 `16/16`。

## 关键证据

- platform tests：`534/534 PASS`
- network policy/sandbox/egress：`73/73 PASS`
- QEMU profile tests：`20/20 PASS`
- Linux namespace TLS/DNS/DHCP/pcap lifecycle：`PASS`
- Core2 A/B：`8/8 + 8/8 = 16/16 PASS`
- Core2 evidence SHA-256：
  `a4da8bc0613b72b179343895b1c01f0fe99cfe1b71bc0171e51ba0cf122e63ef`
  和
  `6442574c0d13d799e4e191fb0c8782a9d0d45ff640f1aa25966fb1f46f2f10b2`
- 产品提交：`6ecaef5ddc4323f3c3919edf4ad25670a64c8c8c`
- Device Service contract：`1.34.0`
- 产品 CI：[40249694316](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40249694316)
  的 `platform-contracts` 与 `network-namespace-policy` 均 PASS

## 文件

- `report.md`：反例、修复、执行、验证边界和回滚；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：tool hash、Core2 批次、哈希和边界。

## 未覆盖项

- 物理跨主机 worker、生产多机调度和无 reachable seed 的任意 NAT；
- worker 未拥有的外部 side effect 与 guest/controller 内部状态 fence；
- 任意公网 DNS、DNSSEC 或外部 resolver rebinding；
- CNAME guest lifecycle 本轮未重跑，只重跑 resolver 契约和 Linux TLS/DNS；
- 物理 PSRAM/cache、bit-exact controller、RF、功耗、声学和真机均
  `NOT RUN`。
