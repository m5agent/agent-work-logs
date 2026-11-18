# PaperColor 原版 USB MSC 块读取执行报告

## 目标与环境

历史验证覆盖 PaperColor 原版的 USB 描述符、配置和 `GET_MAX_LUN`。本次沿用原版 `PaperColor_Factory_Code` 的 16 MiB 完整镜像，在 Device Service 1.99.0 的普通 `runtime=qemu` 会话验证批量命令、数据和命令状态。服务源码基线 `09db00eb793972a679f87234a6797eff70334d47`，所执行的冻结版本 `981fdcdf09253b75be960772147258b677775d8c` 与该基线的相关工具和 API 文件一致。原始镜像、FAT 分区、原生运行时和 ROM 的 SHA-256 均单独核对，见 [结构化记录](run.json)。

普通服务启动实际的 `m5papercolor` 来宾。宿主网络后端关闭，USB 仍经过 PaperColor 所接的原生 S3 DWC2 模型。控制阶段收到地址与配置读回、LUN 0 回执，模型报告 `mode=buffer-dma`。没有改动应用或 USB 控制器模型。

## 复现

1. 在独立状态目录和隔离端口启动 Device Service。以 `papercolor` 设备、`merged` 镜像类型上传完整原版 BIN，校验 SHA-256 后创建 `runtime=qemu` 会话。关闭来宾网络后端，确保实际可执行文件和 ROM 与记录一致。
2. 在首个冷启动周期，沿用 `tests/firmware/papercolor_usb_otg/run_test.py` 的 USB 复位与枚举操作，从描述符确认 bulk OUT `0x01` 和 bulk IN `0x81`，每包 64 字节，再由 `GET_MAX_LUN` 确认 LUN 0。`/sessions/{session_id}/qom` 在 `/machine/soc/usb-otg` 写入 `host-packet`，读取 `host-response` 和 `host-state`。
3. 通过 bulk OUT 发送签名 `USBC` 的 31 字节 CBW，方向 IN，LUN 0。依次发送 `INQUIRY`（期望 36 字节）、`READ CAPACITY(10)`（期望 8 字节）和 `READ(10)`（一次读取一个块）。每次从 bulk IN 收数据，再接收 13 字节 CSW。验证 `USBS` 签名、回显 tag、状态和剩余字节。每个 case 使用新会话，再做只停在容量回执的控制组。
4. 独立从原始 USB 收发表重组数据，在原版镜像分区表定位 `storage`，比对请求 LBA 的全部 4,096 个字节。读取同次串口和证据 ZIP，再保留会话历史、释放会话 Flash 和租约。

## 实测结果

| 会话 | 协议结果 | 原版来宾迹象 |
| --- | --- | --- |
| LBA 0，NAK 轮询间隔 20 毫秒 | `PARTIAL`。64 个数据包与原版 FAT 引导扇区一致。CSW 阶段 7 次 NAK，随后 `DETACHED`。 | 出现 `xTaskPriorityDisinherit tasks.c:5156`，随后 `Rebooting...`。 |
| 省略 `READ(10)` 的控制组 | `INQUIRY` 和 `READ CAPACITY(10)` 成功，未发送读块命令。 | 同一断言，前 9 个 PC 相同，完整堆栈不同，随后 `Rebooting...`。 |
| LBA 1，NAK 轮询间隔 2 毫秒 | `PASS`。4,096 字节与首份 FAT 表一致，CSW 成功。 | 完成于首次冷启动周期。 |
| LBA 0，NAK 轮询间隔 2 毫秒 | `PASS`。4,096 字节与原版引导扇区一致，CSW 成功。 | 完成于首次冷启动周期。 |

已取得的两种块内容不同。LBA 1 的 FAT 表内容在原版下一份 FAT 副本中相同。首轮已经传完 LBA 0，失败发生在命令状态阶段；控制组表明读取块数据并非复现该断言的必需条件。两个快速轮询会话成功时的设备启动耗时也不同，因此此次证据未单独确定轮询间隔、任务调度或断言的根因。两个成功结果只覆盖首启动周期的真实读块路径。

全部 ZIP 的 CRC 和镜像身份校验通过。USB 事务、串口和 ZIP 的摘要可在 [取证记录](evidence/bulk-read-summary.json)核对。原始日志、临时端点、设备地址和租约标识留在私有取证区。没有发出 MSC 写入命令。browser-WASM、物理 USB 和稳定性验收仍未执行。无需回滚源码或常驻服务。
