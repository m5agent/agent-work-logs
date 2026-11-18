# 无网卡 Linux 原版 CardputerDict 可信 HTTPS 复审

- 日期 2026-11-18
- 结果 PASS
- 类型 infra_baseline
- 固件 CardputerDict 0.6.4 原版
- 环境 Linux ARM64 Virtualization / 无网卡 Virtio VSOCK / Device Service 1.99 / Reviewer 0.27
- 源码 esp-emulator 218106fa，运行时 a729e24b，Reviewer f0101b6

## 执行结果

原版经实际 SNTP、真实 TLS、SD 词库和 I2S PCM 完成 hello 发音。SD 上的 10,605
字节 MP3 与使用原版内置 CA 校验的宿主预检逐字节一致。复审 ZIP 和停机 API
均读到同一份 84,992 字节 PCM，峰值 7051。宿主和 Linux 对端的双向 TLS
字节数与 SHA-256 对上。

独立阻断对照保留受控 DNS 和实时校时。原版向 443 发包后没有 HTTPS 回复、
缓存或 PCM。两个通道的无效凭证均在实际连接上游前被拒绝。两台 QEMU 来宾、
Flash、租约、VSOCK 监听和临时 Linux 网络资源均已释放。

## 文件

- [方法和边界](report.md)
- [机器可读运行索引](run.json)
- [结构化收据](evidence/cardputerdict-trusted-https.summary.json)
- [原版证书](https://github.com/RadioDisney/CardputerDict/blob/4b69cef2c59ef443eea191aa8e1b6bbef6178595/include/pronunciation_ca.h)

实体设备、RF、常驻 Linux 路由和外部端点长期可用性未验证。未提交 Burner。
