# ESP Emulator FirmwareManifest policy fail-closed

- 日期：`2026-10-26`
- 结果：`PASS`（static manifest policy）
- 工作类型：`code_change`
- 源码版本：
  [m5stack-esp-emulator @ c00fd2e](https://github.com/m5agent/m5stack-esp-emulator/commit/c00fd2eeed4d180931e9390ed80f3e140359ae74)
- Base commit：`6ecaef5ddc4323f3c3919edf4ad25670a64c8c8c`
- 环境：macOS arm64；Python 3.13；无 firmware/QEMU runtime 启动

## 结论

三个手写/篡改 FirmwareManifest 的 fail-open 路径已经关闭：

1. 根 `capabilities` 过去可以整体省略，兼容性检查仍可能 `PASS`；
2. signed Secure Boot image blocks 仍在时，可以把 aggregate image status
   改成 `not-found` 绕过旧 preflight；
3. `efuse_summary.secure_boot/flash_encryption` 可以写入任意启用字符串，
   旧结构校验和 preflight 都不会拒绝。

现在 schema、内部结构校验和 `validate_capabilities()` 三层都要求
`capabilities.required/optional`；image status 必须与 signed blocks/trust
evidence 一致；eFuse 字段使用严格枚举；key digest mismatch 和 image
secure-version below eFuse 直接拒绝。

## 关键证据

- platform tests：`537/537 PASS`
- `test_firmware_manifest.py`：`32/32 PASS`
- 新 manifest policy fixture：全部 checks PASS
- Secure Boot v2 image rerun：`26/26 PASS`
- schema JSON、runtime coverage、peripheral catalog、QEMU profile、project
  snapshot、compileall、diff check：PASS
- manifest policy evidence SHA-256：
  `b7935b7920e93fe859f1b83bb5cf2d74e58a0c079194d31220792a43f0c036d0`
- Secure Boot v2 rebind evidence SHA-256：
  `5cedb3cd9a7c7857389798b0cc0e2bb8e1e6f2c0d3ab800cae559ec11a3b0aed`
- 产品 CI：[40250487931](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40250487931)
  的 `platform-contracts` 与 `network-namespace-policy` 均 PASS
- 产品提交：`c00fd2eeed4d180931e9390ed80f3e140359ae74`

## 文件

- `report.md`：三项绕过、修复、验证和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：工具哈希、fixture 结果和边界。

## 未覆盖项

- 没有读取 live eFuse、执行 bootloader trust chain 或 anti-rollback；
- 没有执行 Flash Encryption runtime、生产 key 或真机安全配置；
- 没有把 manifest static review 当作任意固件运行态兼容证明；
- 没有新增 QEMU/固件矩阵；本轮是 static manifest policy regression。
