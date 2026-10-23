# ESP Emulator FirmwareManifest FAT12/16/32 文件清单报告

## 背景

FirmwareManifest 已支持 merged/segmented image、静态审查、SBOM 和 LittleFS
文件清单，但 FAT 数据分区此前只返回 `UNSUPPORTED`。ESP-IDF、Arduino 和
第三方固件常用 FAT 保存图片、网页、配置和证书，缺失清单会直接影响固件审查
覆盖率。

目标是在不挂载、不执行镜像的前提下，实现可审计的只读 FAT12/16/32 文件清单，
并确保损坏或未初始化分区不会被误报为 PASS。

## 实现

### Boot sector 和 FAT geometry

- 校验 boot-sector signature、bytes/sector、sectors/cluster、reserved/FAT/
  root/data 区域；
- 根据 BPB 和 cluster count 选择 FAT12/16/32；
- 校验 FAT 表容量足以覆盖声明的 data clusters；
- 支持 FAT32 root cluster 和 28-bit FAT entry。

### 目录与文件

- 支持固定 root directory 和 FAT32 root cluster chain；
- 解析 8.3、NT lowercase bits、LFN sequence 和 checksum；
- 递归目录并限制 depth、file、directory、raw directory entry 数量；
- 对每个文件按 cluster chain 读取并计算 SHA256；
- 校验多簇文件长度，拒绝提前结束、free/bad cluster 和循环链；
- 识别 LICENSE/NOTICE/COPYING 中的 SPDX；
- 对 `.key`、`.env`、credential-like 路径以及敏感目录子树进行脱敏。

### 失败分类

- erased 或 zero-filled FAT partition：`UNFORMATTED`；
- 无有效 boot sector、geometry 不一致或 table 截断：`INVALID`；
- 已解析部分资源但存在损坏目录/文件：`PARTIAL`；
- 完整解析：`PASS`。

`firmware_manifest.py` 把 `UNFORMATTED` 纳入
`filesystem_inventory_incomplete` warning，并统一检查文件或目录 truncation。

## 验证

```text
platform tests                 230/230 PASS
runtime coverage               PASS
peripheral catalog             PASS
QEMU profiles                  PASS
ruff check (changed parser)    PASS
git diff --check               PASS
```

FAT 专项：

```text
fat12 synthetic                PASS
fat16 synthetic                PASS
fat32 synthetic                PASS
LFN and 8.3 fallback           PASS
multi-cluster SHA256           PASS
sensitive path redaction       PASS
SPDX extraction                PASS
cluster loop rejection         PASS
malformed input rejection      PASS
erased partition classification UNFORMATTED
manifest integration           PASS
```

真实公开固件样本：

```text
device                         PaperColor
firmware id                    1897200000000000148
image SHA256                   a3f5...
partition                      storage, FAT12
image size                     16777216
partition size                 6291456
files hashed                   11 PNG
result                         PARTIAL
reason                         System Volume Information has no . / .. entries
```

解析器只保留可由 FAT 目录项和 cluster chain 支撑的 11 个文件。未初始化的
系统目录被拒绝，没有把随机字节解释为合法目录或文件。

## 验证边界

- 这是 static-image validation，不是 QEMU 功能测试；
- 本次 Python 改动没有重跑 QEMU 67-case matrix；
- FAT parser 不挂载镜像，不执行文件，不恢复删除文件，不解析 slack space；
- runtime permissions 和 license compliance 仍为 `NOT RUN`；
- SPIFFS 仍为 `UNSUPPORTED`；
- 真机、secure boot、Flash Encryption 和生产 key 流程未验证。

## 风险与回滚

FAT parser 只读取内存中的镜像切片，不写回输入。资源上限为 512 files、
512 directories、65536 raw directory entries 和 depth 32。

回滚源码提交 `97d9a80e1a1abe6a9870e79d2bc2ca81583e6f7d` 会恢复 FAT
`UNSUPPORTED` 行为，并移除专项 tests/evidence；不会影响 LittleFS、QEMU、
网络或 Device Service 已保存 session。
