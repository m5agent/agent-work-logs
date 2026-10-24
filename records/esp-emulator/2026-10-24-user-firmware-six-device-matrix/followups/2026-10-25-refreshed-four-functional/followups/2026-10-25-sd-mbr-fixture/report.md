# ESP Emulator SD fixture report

## 背景

第一批 refreshed four-firmware 运行得到 `2 PASS / 2 PARTIAL`。CrossPoint
显示 `SD card error`，serial 连续出现：

```text
sdmmc_init_ocr: send_op_cond (1) returned 0x107
```

该结果只说明 generic Device Service session 没有可用 SD media。PaperMono
设备和 QEMU DWC SDMMC controller 已存在，不能据此把错误归为固件 FAIL。

## 实现

### SD image generator

`platform/tools/sd_image.py` 支持：

- `fat32-mbr`：64-96 MiB，MBR 分区从 sector 2048 开始；
- `fat16-superfloppy`：16-64 MiB，用于 raw block I/O fixture。

FAT32 fixture 包含 primary/backup boot sector、FSInfo、双 FAT、root cluster
和 volume label。生成器不使用宿主 `mkfs`/`hdiutil`，同一参数得到同名
SHA256。

### Device Service

新增 session request：

```json
{
  "storage": {
    "sd_image_artifact_id": "<sha256>"
  }
}
```

校验：

- target device 必须声明 modeled SDCard interface；
- artifact id 必须是已上传的 SHA256 artifact；
- image 非空且为 512-byte 整数倍；
- 只接受 `sd_image_artifact_id`，拒绝任意宿主路径。

执行：

1. 把 source artifact 复制到 session directory；
2. 重新计算 isolated copy SHA；
3. 以 writable `-drive if=sd,format=raw` 挂载；
4. 在 session snapshot、持久记录和 evidence ZIP 中保存 storage summary；
5. service restart 后 stopped session 仍能恢复 storage metadata。

### Matrix

`user_firmware_matrix.py --sd-image` 上传一次 fixture，仅向具有 SD 模型的
PaperMono session 传递 artifact id。Sample result key 增加 fixture SHA，
避免同一 BIN 在无卡和有卡条件下复用旧结果。

## 执行

测试发现 FAT16 superfloppy 能让 SD controller 初始化，但 CrossPoint 仍无法
mount。对公开源码
`MarsTechHAN/crosspoint-reader-mono @ 87a191f` 的检查确认：

```text
if (!Storage.begin()) {
  activityManager.goToFullScreenMessage("SD card error", ...);
}
```

进一步验证表明该固件需要 MBR 分区 FAT32 布局。最终使用纯 Python
`fat32-mbr` fixture：

```text
bytes=67108864
sha256=b720d6f7f932bb22accc8b9133f3016e5c060f5d292523f78b3c636c036a5139
partition_start_sector=2048
FAT32 512-byte clusters
```

CrossPoint 最终帧 SHA256：

```text
076f70454f693443987c5153480fac825939b5cdcb6fa9be604c65fc75943d1e
```

画面为 CrossPoint recent-books 主菜单，不再包含 `SD card error`。

## 最终四样本

| Firmware | 结果 | 说明 |
| --- | --- | --- |
| XiaoZhi AtomS3R | PASS | 配网 UI，frame/input/runtime 通过 |
| OpenAI AtomS3R | PARTIAL | NVS user data 缺失，app_main 返回，黑屏 |
| EDC Book | PASS | 启动/续读 UI，session receipt storage copy |
| CrossPoint PaperMono | PASS | FAT32+MBR SD fixture 后进入主菜单 |

汇总：`3 PASS / 1 PARTIAL / 0 FAIL`。

## 验证

```text
platform tests       363/363 PASS
user matrix tests     18/18 PASS
SD image tests         4/4 PASS
docs contract         19/19 PASS
Node                    2/2 PASS
runtime coverage        PASS
peripheral catalog      PASS
qemu profiles           PASS
project snapshot        PASS
compileall/JSON         PASS
GitHub Actions 40127676353 PASS
```

服务重启后读取 stopped CrossPoint session，storage summary 仍存在；下载
evidence ZIP 后验证其中包含 frame、storage summary 和 manifest。

## 验证边界

- 这是 virtual-device validation，不是物理 SD、PMIC 或 RF 验证。
- CrossPoint 只证明应用启动、SD mount 和主菜单输入；书籍读取及长期状态未跑。
- OpenAI 黑屏仍需用户数据 fixture 或独立根因分析。
- FAT32+MBR 是已验证布局，不代表固件支持所有分区、cluster 或文件系统配置。
- SD image 原文件不进入仓库；只提交生成器、SHA 和冻结截图。

## 回滚

可依次 revert `5ff9d50`、`7647940` 和 `437d417`。无物理设备写入。
