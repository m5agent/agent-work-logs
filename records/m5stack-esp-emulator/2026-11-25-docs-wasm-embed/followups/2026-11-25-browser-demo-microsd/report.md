# 浏览器工作台按文档例程挂接 microSD

[#253](https://github.com/m5agent/m5stack-esp-emulator/issues/253) 记录 CoreS3 SDcard、Picture、WAV 及 Cardputer-Adv SDcard 的原例程依赖外置素材。旧工作台只传设备和 Flash。虽然底层虚拟 SPI 卡能打开卡镜像，通用浏览器启动没有交付这份镜像。

导出器通过 `--qemu-sd-media <fixture-directory>` 校验卡镜像和例程清单。导出将已审查的素材压缩后按原始摘要寻址，同一内容可以声明给多个固件。工作台按设备和输入固件 SHA-256 选中卡镜像，分别校验 gzip 和解压后的字节。QEMU Worker 以会话独立副本挂接实际 SPI microSD。停止后该副本跟随 Worker 释放，静态 gzip 种子可复用。

## 复现

按 CoreS3 Arduino [SDcard](https://docs.m5stack.com/en/arduino/m5cores3/sdcard)、[Picture](https://docs.m5stack.com/en/arduino/m5cores3/pic) 和 Cardputer 系列 [SDcard](https://docs.m5stack.com/en/arduino/m5cardputer/sdcard) 取得原程序，核对单独记录的固件来源、板型、版本和合并镜像摘要。ADV 采用文档最低库版本和实际 8 MiB Flash 配置。

使用仓库 `platform/tools/sd_image.py --format fat32-mbr --out <image>` 生成 64 MiB FAT32-MBR 种子，分区起点 LBA 2048。向 CoreS3 卡写入 320×240、40 像素方格的红白和蓝黄 PNG，按例程分别保存为 `TestPicture01.png`、`TestPicture02.png`、`cores3_test_picture01.png` 和 `cores3_test_picture02.png`。共享素材也包含 16 kHz 单声道 12 秒 `sample-12s.wav`。ADV 卡另有读取和改名用的种子文件。确切执行素材、原固件和 gzip 摘要见结构化证据。

创建 `manifest.json`，填入 `schema_version: 1` 和 `examples`。每条记录使用 `device`、`firmware_sha256`、`image`、`bytes`、`sha256`。锁定运行时通过 `platform/tools/build_public_site.py --qemu-runtime <runtime> --littlefs-runtime <composer> --qemu-sd-media <fixture-directory>` 导出。再次执行相同导出并省略素材参数，可得到无卡对照。隔离浏览器选择对应设备、本地原始合并固件和浏览器执行，点击启动。实际 LCD 和程序结果到达后点击停止，记录 Worker 回收及会话身份。

本文记录浏览器虚拟设备验证。正式托管与真机未执行。

## 工作台与 SPI 取证

第一次完整工作台矩阵使用同一锁定 WASM `618f471307a11e90301372b5f704afa46df1224be19feda292ba663fb6c31a62`。CoreS3 SDcard 在原固件 LCD 报告卡检测及写入成功，随后与 Picture 一样显示两张完整的 320×240 来宾画面，RGB565 全帧与种子源像素一致。两个 64 MiB 初始卡分别压缩为 85,913 和 86,129 字节，四个固件声明合并使用这两份静态资源。

Cardputer-Adv 同一工作台页面停止并再次启动。两个浏览器来宾均报告删除、改名、读取 28 字节、写入 1,048,576 字节及容量。两个独立会话都恢复初始种子，第二次只复用不可变 gzip。未提供映射时，原 CoreS3 镜像启动并显示缺卡，没有请求素材。单字节损坏的压缩响应在创建来宾前被拒绝，首次报告将错误写成固件校验。后续构建将提示修正为 microSD 素材错误。

独立诊断只在本地导出副本中打开已有 `M5SW_SPI_SD_TRACE`，QEMU WASM 与原固件相同。真实工作台启动后观察到 44 次 CMD17、11 次 CMD24 和 11 次写入接受响应 `0x05`。写入的数据区包含原例程 `WriteTest.txt` 的完整预期文本，同一来宾显示两张源图片并正常退出。主矩阵保留未启用字节跟踪的标准工作台。

修正错误提示后的导出重新验证了两款设备的三个原例程、无卡及压缩响应损坏对照。损坏响应显示「无法读取或校验示例 microSD 素材。」且未创建来宾 Worker。相同最终导出也运行 CoreS3 原版 WAV。来宾显示实际文件 384,044 字节，解析出 16 kHz、单声道、16 位，读到第一个 16 KiB 数据段。观察 36 秒未见后续完成提示，声音未采集。音频由 [#248](https://github.com/m5agent/m5stack-esp-emulator/issues/248) 跟踪。此次 WAV 会话正常回收了六个 Worker。
