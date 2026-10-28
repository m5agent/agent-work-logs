# QRCode.setText 与 TLS epoch 三设备候选固件报告

## 背景

三设备接口复测保留了两个已有源码补丁但尚未在 StopWatch、StickS3、Core2
重建候选固件的问题：

- `0014-widgets-qrcode-text`：`Widgets.QRCode.setText` 更新字符串后仍重绘旧 QR；
- `0010-mbedtls-epoch`：1970 epoch UIFlow 端口重复添加 1970→2000 偏移，导致
  2026 RTC 被 mbedTLS 解释为 2056，owned 2020–2035 证书被判过期。

## 构建

三台板先由匹配 source build、bootloader 和 partition table 组成 preimage，
再分别增量编译/重链接一个 translation unit：

| 设备 | preimage | QR 候选 | TLS 候选 |
| --- | --- | --- | --- |
| StopWatch | `790184d2…b5d0` | `a8e69c2e…ebfe` | `edcd9a39…e6a6` |
| StickS3 | QR `20b78359…3b95`; TLS `373092e7…77a6` | `a036205d…970b` | `2e838605…f6aa` |
| Core2 | `f3d37e56…e4e` | `42669acc…f932` | `204def8c…e2c6` |

每个 receipt 都断言：

- `outside_application_unchanged=true`
- `original_source_unchanged=true`
- `original_library_unchanged=true`
- `kind=incremental-candidate-firmware`, `cold_build=false`

StickS3 TLS 不使用 stale `hciuart` UART object；改用了包含当前 native UART
REPL 的 `unified` build。`run_guest.py` / `run_protocols.py` 新增 native
bootstrap，避免对已由固件占用的 UART0 再执行 `os.dupterm`。

`0010` manifest 的 source binding 从旧 release commit `3a86d8f6…` 重绑到
当前 `db526ecc…`。差异位于 `m5things` 启动路径，不改变 epoch patch hunk；
preimage、candidate 和 patch SHA 均重新核对。

## QR 验证

同一个 Widgets 程序先绘制 `UIFLOW2-API`，再调用 `setText('UPDATED-API')`。
最终画面必须由独立 QR decoder 解出 `UPDATED-API`。

| 设备 | preimage | 候选 |
| --- | --- | --- |
| StopWatch | `ORACLE_MISMATCH` | `FRAME_PASS` |
| StickS3 | `ORACLE_MISMATCH` | `FRAME_PASS` |
| Core2 | `ORACLE_MISMATCH` | `FRAME_PASS` |

状态方法本身返回不能证明文字更新，因此保留 `PENDING_FRAME` 并由画面 oracle
给出最终结果。

## TLS 验证

临时证书有效期 `2020-01-01`–`2035-01-01`，RTC 正确设为 2026。preimage
三台都在 handshake 返回：

```text
ValueError('\nThe certificate validity has expired\n')
```

候选三台都通过五个原始 `CERT_REQUIRED`/mTLS 项：

- `ssl.SSLContext.wrap_socket`
- `ssl.SSLContext`
- `ssl.SSLContext.load_verify_locations`
- `ssl.SSLContext.load_cert_chain`
- `ssl.wrap_socket`

每台有两条独立 `/tls-authenticated` GET；owned peer 记录 TLSv1.2、客户端证书
SHA256 和响应 body SHA256。候选 firmware/evidence 哈希记录在
`evidence/results.json`。

## 回归与清理

```text
PYTHONPATH=platform/tools:.work/py python3 -m unittest discover -s platform/tests -p 'test_*.py'
Ran 1346 tests in 113.756s
OK (skipped=1)

runtime_coverage / peripheral_catalog / qemu_profiles / project_snapshot: PASS
actionable contracts: 29/29 PASS
git diff --check: PASS
```

全部 session 先取 evidence，再以 `purge=0` 停止；runtime PID 消失，独立测试
service 停止，未留下 QEMU 进程。

## 边界与回滚

本记录只证明 hash-pinned virtual candidates。物理硬件、RF、公网 PKI、生产
证书存储和 Secure Element 未验证。回滚为撤销对应候选 build/patch，不修改
平台默认 reference 或原厂 CDN 固件。
