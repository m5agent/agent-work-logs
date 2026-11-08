# StickS3 官方 v2.5.5 preview TLS 时间校验

## 来源与范围

[UIFlow #120](https://github.com/m5stack/uiflow-micropython/issues/120) 报告 v2.5.3 在正确时钟下出现证书过期错误。维护者 10 月 30 日回应计划在 v2.5.5 修复。本轮对官方公开元数据标记为 `UIFlow2 v2.5.5 preview` 的镜像执行限定复核，原 issue 仍开放。

主代理制定输入和验收标准，dsh 0.2.2-rc.1 的 DeepSeek 模型实际创建 Device Service `/api/v1` 会话并执行固件。所有结果标记为 `virtual-device validation`。

## 镜像与实现身份

base 为 8,384,512 字节，SHA256 为 `fd85648dfa1fd9656448aa45e86ee63be537a4534e959e422c0be4d45b3466c7`。现场重新下载公开 CDN 产物，哈希与缓存一致。原生应用分区 SHA256 为 `2c4aec55288901846e5b63da096f8975492db6677c2d0478c7aedd4572cc595f`。base 按声明的 8 MiB Flash 以 `0xff` 补齐后，四次执行的应用分区及 VFS 外字节逐字节一致。

匹配的运行时与 ROM 身份见[既有固定源码证据](https://github.com/m5agent/m5stack-esp-emulator/blob/dd2eb35d2e6a909992268089ddc37e27970d4a92/docs/evidence/2026-11-05-latest-firmware-issues/root-peripheral-summary.json)。

运行时 SHA256 为 `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e`。源码固定为 `dd2eb35d2e6a909992268089ddc37e27970d4a92`。受测 TLS 库沿用镜像内实现，探针及临时测试证书写入 VFS。原始 `caller-pinned-candidate` 组合标签保留，`library_lane=stock-frozen` 表示 TLS 库来源。

## 实际结果

证书有效期为 2020-01-01 至 2035-01-01。三个输入分别生成独立证书，摘要记录各自哈希。

| RTC 输入 | SSLContext 与模块 wrap_socket | peer 数据面 | 独立判定 |
| --- | --- | --- | --- |
| 2026-10-27 | 两次真实握手及 HTTP 200，保持 CA、主机名和客户端证书验证 | 两次请求的客户端证书 SHA 与该轮 fixture 一致 | PASS |
| 2010-10-27 | 两次明确拒绝证书尚未生效 | 零认证 HTTP 请求 | 预期拒绝 PASS |
| 2040-10-27 | 两次明确拒绝证书已过期 | 零认证 HTTP 请求 | 预期拒绝 PASS |

正控原报告为 5 PASS，其中包含两个独立数据面调用与三个关联配置检查。两次负控原报告均保留 `FAIL`，各有 2 ERROR、3 STATE_PASS，命令退出码均为 1。上表根据具体错误与 peer 拒绝另行评价负控行为。

## 首次观测失败与纠正

首轮选择 native UART bootstrap，原始结果缺少 Python 串口 ready、RTC 和 API 行，最终因 ready marker 超时失败。peer 实际收到两次正确证书的 TLS/HTTP 请求，证明探针的数据面已经运行。原失败记录完整保留。

随后改用 checked-in runner 的 dupterm bootstrap，把 Python 输出桥接到 UART。TLS 验证逻辑、官方应用和运行时保持同一实现。纠正后的三个输入获得完整时钟、串口和 peer 观测。

最初曾怀疑 LittleFS 2.0 到 2.1 的宿主版本变化，历史同版本成功证据构成反证。该变化未被认定为本次串口问题的原因，也没有据此修改源码。

## 复现入口

使用固定源码及匹配运行时建立独立 Device Service，并准备公开 base。对 2026、2010、2040 分别执行以下命令，使用各自尚未存在的输出目录。

```sh
python3 tests/uiflow2/api_sweep/run_protocols.py --execute \
  --api "$DEVICE_SERVICE_ORIGIN" --token-file "$CONTROL_TOKEN_FILE" \
  --group tls --device sticks3 \
  --base-image sticks3=platform/.cache/firmware/sticks3/uiflow2.bin \
  --expected-base-sha256 sticks3=fd85648dfa1fd9656448aa45e86ee63be537a4534e959e422c0be4d45b3466c7 \
  --uart-repl-bootstrap dupterm --tls-clock-year "$RTC_YEAR" \
  --out-dir "$FRESH_OUTPUT_DIR" --timeout 240
```

负控退出码 1 为原报告的预期表现，需根据实际错误类别和 peer 数据独立评价。

## 证据与边界

[脱敏摘要](evidence/tls-validity-summary.json) 给出每轮固件、探针、证书、串口、frame、peer 和 ZIP 哈希，并保留原始结果与独立判定。ZIP 必需成员及存在的可选成员逐一重算大小和 SHA。三组完整观测在下载 ZIP 后请求停止，历史保留，运行时退出。首轮先因 ready 超时自动失败，随后下载证据并保留其失败状态。

独立验收见[检查摘要](evidence/independent-audit-summary.json)。ZIP 完成时序由同步原代码顺序、文件时间和服务请求顺序交叉支持，本轮没有单独抓取客户端下载完成时刻。实际 PID、启动身份及二进制哈希在 booting/running 阶段独立核对，停止前最后一刻没有另行重算二进制。运行时最终均已退出。

原 v2.5.3 本轮为 `NOT RUN`。AWS IoT 账号、MQTT 消息投递、NTP 获取、错误主机名/无关 CA 负控、物理 Wi-Fi/RF 与其它板卡均为 `NOT RUN`。当前结论适用于上述受控 TLS 时间校验路径。公开摘要已去除端点、机器路径、进程与会话标识以及临时私钥，完整原始证据保留在私有存储。
