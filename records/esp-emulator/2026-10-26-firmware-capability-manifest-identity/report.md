# Firmware capability fail-closed and manifest identity report

## 背景

用户在继续推进 P0 固件审查时，重点包括标准 FirmwareManifest、
WebBurner 导入、安全配置和 capability mismatch。审计当前实现发现：

- unknown required capability 只记录 warning，不能阻止 manifest 被视为
  compatible；
- manifest identity 仍包含输出 artifact 文件名，导致相同 WebBurner 内容从
  不同目录名导入时产生不同 `manifest_id`；
- Device Service 与 importer 各自维护 manifest ID 计算逻辑，存在再次漂移的
  风险。

## 根因与修复

### Unknown required capability

`validate_capabilities()` 现在把未知 required capability 放入 `errors`，
因此 manifest validation 为 `REJECTED`。Device Service 将该 manifest 映射为
`409 unsupported_firmware_capability`，不会创建 firmware/session。unknown
optional capability 仍只产生 `unknown_optional_capability` warning。

### Manifest identity

新增统一的 `manifest_identity_payload()`：canonical identity 去除
`created_at`、`manifest_id` 和 `artifact.file`。`artifact.sha256`、
segments、target、security、capabilities、resources 和 validation 仍参与
identity。CLI/importer 与 Device Service 都调用同一 helper。

相同 WebBurner 内容放在两个不同目录名下时，规范化 artifact SHA 相同且
`manifest_id` 相同；输出文件名的差异不再改变内容身份。

## 执行与证据

公开 StickS3 Weather firmware：

- source SHA256：
  `8b7b47c8d601e1821817f8d0e6b55568829913e50333dbcc15de6ffdbad1997c`
- normalized flash SHA256：
  `d291e77f782399e37fd5b464f9b206a00654b2c10556d730d1c45667156c603f`

结果：

| 输入 / 声明 | 结果 |
| --- | --- |
| merged，required `wifi` | `PASS`, exit `0` |
| merged，required unknown | `REJECTED`, exit `1`, 唯一 error `unknown_required_capability` |
| merged，optional unknown | `PASS`, warning `unknown_optional_capability` |
| WebBurner，required `wifi` | `PASS`, source format `web-manifest` |
| WebBurner 第二目录名，相同内容 | 相同 artifact SHA 与 `manifest_id` |
| WebBurner，required unknown | `REJECTED`, exit `1` |

`firmware_manifest.py` 工具 hash 变化后，旧 Secure Boot evidence 不能继续
绑定当前工具。当前代码已重跑静态 Secure Boot fixture，`26/26` checks
PASS；authenticity、trust root 和 anti-rollback 仍为 `not-verified`。

`device_service.py` hash 变化同时影响 Core2 八实例 evidence。使用当前源码
重建同 SHA `c3eaa35b…` unified firmware，并重跑两批独立零错峰 `8×120s`：

- A：`8/8 PASS`
- B：`8/8 PASS`
- 合计：`16/16`
- 最大真实并发：`8`
- 每批 evidence 均绑定当前 `device_service`
  `abbffe80a46c6480a157921acd88356d15e64be0b1b3f6060382527a235fb715`

首次重跑没有设置 `M5_CORE2_RADIO_QEMU`，8 个会话在创建阶段返回 503，
`maximum_concurrent_sessions=0`。该 infrastructure control 没有计入有效
批次；设置文档要求的环境变量后使用原命令重跑。

## 验证

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
npm run test:units
python3 tests/firmware/unknown_required_capability/run_test.py
python3 tests/firmware/secure_boot_image/run_test.py --out-dir <new-temp-dir>
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
python3 -m compileall -q platform/tools platform/tests \
  tests/firmware/unknown_required_capability tests/firmware/secure_boot_image
ruff check --select E9,F platform/tools platform/tests \
  tests/firmware/unknown_required_capability tests/firmware/secure_boot_image
git diff --check
```

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build/static | `PASS` | compileall、Ruff、Node units、manifest/Secure Boot fixtures |
| platform contracts | `PASS` | `525/525` |
| virtual-device Core2 | `PASS` | 两批 `8×120s`，合计 `16/16` |
| firmware call-path capability | `NOT RUN` | 声明与静态 observation 不证明 runtime use |
| full UIFlow2 matrix | `NOT RUN` | 本轮未重跑 67 cases |
| physical hardware | `NOT RUN` | 无真机、RF、功耗、光学或电气测量 |

## 风险与回滚

没有烧录、擦除、生产配置或持久设备状态修改。回滚 product commit
`904d4ec7c6fb9516942625c86d619ebba5ae90a3` 会恢复旧的 warning/identity
行为，但也会重新引入 required capability 不 fail-closed 和 WebBurner
manifest ID 漂移；旧 evidence 不应被删除或改写。
