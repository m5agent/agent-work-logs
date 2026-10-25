# ESP Emulator 镜像能力观察与 capability mismatch 报告

## 背景

FirmwareManifest 已支持 required/optional 声明和 sdkconfig detected
capability。但很多公开 BIN 或 WebBurner 包不带 sdkconfig，manifest 只能
记录操作者声明，无法提示“镜像里出现某能力，但声明没有写”或“required
能力受设备支持，但镜像中没有相应 token”的审查风险。

直接把这些 token 当成强制能力会制造 false positive：链接库可能残留字符串，
字符串也可能未被执行。因此本轮目标是增加低置信度观察层，始终与 hard
compatibility gate 分离。

## 实现

### 数据模型

manifest 新增：

```text
capabilities.observed[]
  capability
  source=image-signature
  confidence=low
  signatures[]

capabilities.observation
  status=SCANNED|TRUNCATED
  source=normalized-flash
  bytes_total
  bytes_scanned
  truncated
```

白名单覆盖 WiFi、BLE、Classic Bluetooth、IEEE 802.15.4、PSRAM、camera、
display、touch、audio 和 SD。扫描只读取规范化完整 Flash 的前 64 MiB，
不会输出任意字符串。

### Warning 语义

- `required_capability_not_observed`：required 能力受设备支持，但相应镜像
  token 没出现；
- `observed_capability_not_declared`：镜像出现能力 token，但 required/
  optional 都没有声明；
- `observed_capability_unavailable`：镜像出现能力 token，但目标 profile
  没有该能力；
- 以上都只是 review warning；
- 设备不支持 required 能力仍产生 error
  `unsupported_capability`，不会因 observation 降级。

### Schema 与兼容性

`observed`/`observation` 是可选的新增字段，既有 v1 manifest 无需重写。
structure validator 同时限制条数、token 长度、重复项、source/confidence
和 scan coverage 一致性。

## 真实样本验证

使用公开 StickS3 Weather BIN：

```text
source bytes      8,323,072
source sha256     8b7b47c8d601e1821817f8d0e6b55568829913e50333dbcc15de6ffdbad1997c
normalized sha256 d291e77f782399e37fd5b464f9b206a00654b2c10556d730d1c45667156c603f
device            sticks3
scan              8 MiB / 8 MiB, SCANNED
observed          wifi, display
required wifi     PASS
optional display  PASS
required camera   REJECTED / unsupported_capability
```

两个 import 的 normalized artifact hash 相同，说明 capability observation
没有改变输入字节或规范化语义。

## 验证

```text
platform contracts               413/413 PASS
documentation contracts          22/22 PASS
manifest tests                   24/24 PASS
runtime coverage                 PASS
peripheral catalog               PASS
QEMU profiles                    PASS
project snapshot                 PASS
compileall                       PASS
selected Ruff E9/F               PASS
OpenAPI/manifest schema JSON     PASS
git diff --check                 PASS
GitHub Actions 40147212974       PASS
GitHub Actions 40147293390       PASS
```

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compile and schema JSON |
| static_image | `PASS` | real public BIN normalized and scanned |
| capability_contract | `PASS` | declared/observed mismatch warnings and hard required rejection |
| runtime | `NOT RUN` | no boot/network/UI execution added by this milestone |
| physical | `NOT RUN` | no hardware, RF or secure-boot measurement |

## 未覆盖与风险

- linked-library token 可造成 false positive；
- stripped/compressed strings 可造成 false negative；
- observation 不证明函数被调用，也不证明外设初始成功；
- `CLEAN`/warning 不是安全或法律结论；
- WebBurner UI 本轮复用同一 manifest importer，没有新增浏览器交互；
- 物理硬件、secure boot/eFuse 和运行时权限仍为 `NOT RUN`。

## 回滚

回滚 `c4d4f6a` 后回滚 `9ad3771d87acff6147714492caa84d0c288eb293` 可移除
文档证据和 observation 字段。新字段为可选，旧 manifest 和验证工具无需
数据迁移；回滚不影响虚拟设备、凭据或物理硬件状态。
