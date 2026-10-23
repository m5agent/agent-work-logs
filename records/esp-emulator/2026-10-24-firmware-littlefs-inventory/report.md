# FirmwareManifest LittleFS 资源清单报告

## 背景

现有 manifest/静态审查已经覆盖镜像结构、分区、app descriptor、URL、
凭据特征、高熵块和 SBOM，但不能回答某个 data partition 内实际有哪些文件，
也无法给出敏感资源或许可证文件证据。

## 改动

- 新增 `firmware_filesystems.py`；
- `analyze_firmware()` 在分区解析后识别 data partition；
- LittleFS 通过 `littlefs-python` 以只读上下文挂载；
- 日志只记录路径/大小/哈希，不保存文件正文；
- 敏感路径写为 `<redacted-sensitive-path>` 加路径哈希；
- LICENSE 类文件提取 SPDX 声明；
- manifest `target.filesystems` 保存清单；
- manifest validation 对 unavailable/unsupported/partial/truncated 和敏感路径
  给出结构化 warning；
- schema v1 增加可选 `target.filesystems`，旧 manifest 保持兼容。

## 真实样本

StickS3 UIFlow2 image SHA256：
`c08196024019273ccadee9b4b3da303567f7ab206fa14edd1af283f04f6e98d8`

| 分区 | 类型 | 文件 | 目录 | 数据字节 | 状态 |
| --- | --- | ---: | ---: | ---: | --- |
| sys | LittleFS | 39 | 5 | 632603 | PASS |
| vfs | LittleFS | 17 | 7 | 16306 | PASS |

两个分区均通过 manifest import，validation 为 PASS。

## 测试

```text
platform tests                    225/225 PASS
runtime coverage                  PASS
peripheral catalog                PASS
QEMU profiles                     PASS
LittleFS file hash                PASS
sensitive path redaction          PASS
SPDX extraction                   PASS
manifest integration              PASS
```

## 边界

- LittleFS 不保存 Unix mode，因此权限字段明确写为 `not-recorded`；
- SPDX 存在只证明文件声明，不证明许可证合规；
- SPIFFS/FAT 尚未实现，只返回 unsupported；
- 不读取或保存文件正文到 manifest；
- 不证明恶意固件安全；
- 不覆盖真机安全启动、Flash Encryption 或生产 key。

## 回滚

源码回滚点 `6de2f923735937aac19457ccb37469ae03cfb822`。回滚
`eca4120090ad46b12b64ff74b345c38def80804b` 会移除 LittleFS 清单，但
不影响已有镜像结构、静态 review、SBOM 和 capability 检查。
