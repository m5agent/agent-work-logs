# ESP Emulator SPIFFS 只读清单与文档对账报告

## 背景

FirmwareManifest 已支持 LittleFS 和 FAT12/16/32 文件清单，但 SPIFFS data
partition 此前返回 `UNSUPPORTED`。ESP-IDF 固件仍常用 SPIFFS 保存启动脚本、
网页、配置、证书和许可证文本，缺少可审计清单会降低通用固件审查覆盖率。

目标是在主进程内实现 read-only parser，覆盖明确的 ESP-IDF 布局；不挂载宿主
文件系统、不执行镜像，并让 unsupported/malformed 输入得到确定分类。

## 实现

### SPIFFS 解析

- 支持 page size `256/512`、block size `4096/65536`、object-name length
  `32/64` 和 metadata length `4/0` 的 8 个 little-endian、默认未对齐
  object-index 配置；
- 根据 page 所在 block 计算 LUT entry，并校验 LUT 与 page-header object ID；
- 校验 object-index/data page flags、span、页号范围和数据页顺序；
- 将 span 0 与后续 index page 的数据页引用串接，计算文件 SHA256；
- 记录 `index_page_count`、`data_page_count`、`selected_config` 和所有
  `config_attempts`；
- 对所有候选配置按 complete objects、valid data pages、index pages 和
  objects 评分，避免多个 block size 同时匹配时误选；
- 从 LICENSE/NOTICE/COPYING 提取 SPDX；
- 对 key、credential、secret 等敏感路径只保留脱敏标记、路径哈希和内容哈希；
- erased partition 返回 `UNFORMATTED`，无有效布局返回 `INVALID`。

### 测试与证据

自包含 fixture 参数化覆盖全部 8 个声明配置。每个配置的主文件都超过一个
object-index page 的容量，从而强制测试 span 0 + span 1 的拼接和多 data
page 哈希。负例覆盖随机字节、LUT mismatch 和全 `0xFF` 分区。

ESP-IDF v5.5.4 `spiffsgen.py` canonical fixture：

```text
page/block/name/meta       256 / 4096 / 32 / 4
image size                 16384
image SHA256               6951389cf0f200e011b5d4603a1e29405697b54e95f9291e7248a30c6d6b819c
file count                 3
directory count            2
declared license           MIT
sensitive path count       1
```

多索引 fixture：

```text
image size                 131072
file size                  60000
index pages                3
data pages                 240
file SHA256 match          true
```

### 文档与代码地图对账

本轮同步了当前状态、工作流台账、Backlog、验证台账、代码地图、
FirmwareManifest 契约、QEMU 设备矩阵和统一运行时文档：

- 移除 SPIFFS `UNSUPPORTED` 的旧状态；
- 明确 8 个配置、LUT、多索引和负例的验证边界；
- 把 Core2 `HCI-3b` 的最新 API-boundary 审计补到当前事实页；
- 保持网络远程 worker/re-attach/IPv6、Core2 native backend 和真机验证为
  开放项，不把 partial 写成完成；
- 文档一致性测试检查 evidence 文件、SPIFFS 状态、配置数、LUT、许可证、
  敏感路径和相对链接。

## 验证

```text
local platform tests       267/267 PASS, skipped=0
GitHub Actions             267 tests, skipped=2, conclusion success
runtime coverage           PASS
peripheral catalog         PASS
QEMU profiles              PASS
Node SHA256/upload         2/2 PASS
Python compileall          PASS
git diff --check           PASS
```

GitHub Actions：

- run：`40042218401`；
- head：`7d274bcf3b8f7759f4d0d721bd6b234f6a67a928`；
- CI 的两个 skip 是 Linux runner 缺少本地 LittleFS 测试运行时，不是 SPIFFS
  或文档测试跳过。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall、Repository CI |
| transport | `NOT RUN` | 本轮是 static-image parser，不涉及运行时链路 |
| device_response | `NOT RUN` | 未运行 QEMU/固件会话 |
| data_behavior | `PASS` | 8 配置多索引 fixture、canonical/malformed/manifest SHA256 |
| visual_or_physical | `NOT RUN` | 无真机或视觉任务 |

## 验证边界

- static-image PASS 不证明镜像安全、许可证合规或 runtime permissions；
- big-endian 与 aligned object-index table 布局没有声明支持；
- 不恢复删除对象，不检查未分配页中的历史数据；
- 本次无 QEMU 功能矩阵，因为改动只在静态固件审查 Python 与文档；
- 物理硬件、RF、secure boot、Flash Encryption 和生产 key 均未验证。

## 风险与回滚

parser 只读取内存切片，不写回输入镜像；文件、目录和 SPDX 前缀均有资源上限。
回滚源码提交 `7d274bcf3b8f7759f4d0d721bd6b234f6a67a928` 会移除 SPIFFS
inventory、测试和当前状态同步，不影响 LittleFS/FAT 解析或已保存的 Device
Service session。
