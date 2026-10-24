# ESP Emulator refreshed four-firmware functional report

## 背景

公开 M5Burner CDN 上同一 firmware/version ID 的 BIN 字节可变化。此前已经对
四个当前制品执行强制刷新、静态分析和 FirmwareManifest 导入，但没有启动
Device Service。该 follow-up 补上同一批 SHA 的虚拟设备执行。

## 执行

```text
devices=atoms3r,papermono
samples_per_device=2
observe_seconds=60
settle_seconds=2
service=/api/v1
runtime=qemu
```

runner 在首轮和 `--resume` 中重新解析公开 metadata、下载当前 BIN 并重算
SHA。每个样本上传 merged image，创建 Device Service session，观察 frame、
serial 和 board-appropriate input，最后以 `purge=0` 停止并保留历史。

## 结果

| Firmware | 结果 | 观察 |
| --- | --- | --- |
| XiaoZhi Voice Assistant For AtomS3R | PASS | 128x128 Wi-Fi 配网 UI；frame 和 serial 均随 probe 改变；有 6 次 nonfatal ES8311 audio write failure |
| OpenAI Voice Assistant For AtomS3R | PARTIAL | 128x128 黑屏；NVS 无 user data，`app_main()` 返回；区分“需要可信首次启动数据”与固件缺陷仍需补测 |
| 阅读卡片 \| EDC Book | PASS | 480x800 启动/续读界面；touch probe 后 frame 从空白变为应用页 |
| CrossPoint-PaperMono-CJK | PARTIAL | 480x800 `SD card error`；serial 连续 4 次 `sdmmc_init_ocr: send_op_cond (1) returned 0x107` |

CrossPoint 不是 firmware FAIL：PaperMono 的 SD controller/model 在设备矩阵中
存在，但 generic Device Service session 没有挂载 initialized SD media。
runner 现将该稳定签名标为 `runtime_fixture_gap`，返回 `PARTIAL`。

## 代码改动

- `detect_runtime_model_gaps()` 增加 PaperMono 重复 SDMMC OCR 失败识别；
- runtime gap 支持 `category=fixture`；
- `classify_result()` 对 fixture gap 返回 `runtime_fixture_gap`；
- 新增“重复失败才归因”的负向测试，避免单条瞬时错误误分类；
- 文档一致性测试绑定四样本 summary、CrossPoint fixture gap、OpenAI 黑屏和
  四张最终帧。

## 验证

```text
platform tests       357/357 PASS
user matrix tests     17/17 PASS
docs contract         19/19 PASS
Node                    2/2 PASS
runtime coverage        PASS
peripheral catalog      PASS
qemu profiles           PASS
project snapshot        PASS
compileall/JSON         PASS
GitHub Actions 40126416761 PASS
```

源码提交：

- `18ac23124802079380c4738d5d66c5d79f86ed04`：fixture-gap 分类与测试；
- `259533cef424ffa0418369e2767a38862dc1b7d4`：四样本 evidence、screenshots
  与文档同步。

## 风险与回滚

无物理设备写入或不可逆操作。回滚可 revert 上述两个提交。Source BIN 不进入
仓库；证据只保存 source/normalized SHA、session、serial digest 和截图。

## 后续

1. 为 PaperMono 增加可挂载、耗材隔离的 initialized FAT/SD media fixture；
2. 提供可信 OpenAI Voice Assistant NVS fixture，或确认无配置启动是否为固件缺陷；
3. 在四样本基础上扩更多设备和 firmware family；
4. 将 storage fixture 纳入 Manifest capability/preflight，避免把缺失前置条件
   报成固件 FAIL。
