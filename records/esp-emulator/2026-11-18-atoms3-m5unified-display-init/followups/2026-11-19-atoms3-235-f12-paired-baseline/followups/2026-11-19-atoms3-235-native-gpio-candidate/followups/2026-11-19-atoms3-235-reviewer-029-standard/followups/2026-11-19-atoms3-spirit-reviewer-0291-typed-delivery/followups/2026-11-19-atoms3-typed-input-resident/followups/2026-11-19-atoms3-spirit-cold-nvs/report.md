# 原版 Spirit Level 校准状态的冷启动验收

使用被冻结的 Device Service 1.99.3 源码 `2a7f979c0c7e67420d8b790a3cfdb692702abf05`、签名 Xtensa QEMU `04abc3ba8cb115919e7faebd55425c802f4f6e40b10bc3cc422c51700add728e` 和固定 AtomS3 ROM。输入是同一份 609,856 字节的 Spirit Level v1.0.0 完整原版。三个访客均为独立 `m5atoms3-st7735` 冷启动。此处续接原版按键递交验证，检查正常停止后读取与重新导入 Flash 能否恢复应用状态。 [签名运行时和常驻版本](../../README.md)

调用 `POST /api/v1/firmware/import` 导入原版或前一轮的停止快照，随后新建独立会话。校准与清零访客通过 `DELETE /api/v1/sessions/{id}?purge=0&retain_flash=1` 正常停止，然后以认证请求读取 `GET /api/v1/sessions/{id}/flash?format=bin`。两次实际停止后读出的 8 MiB 均与相应会话停止前 ZIP 和在线 Flash 字节一致。保留历史并释放 Flash 后，重新读取返回 HTTP 409 `flash_not_available`。认证读取路径已执行，匿名负面对照未执行。

| 独立冷启动输入 | 平放 X 轴显示 | 同一 +0.75g 以后的 X 轴显示 | 后续动作与输出 |
| --- | --- | --- | --- |
| 原版镜像 | +0.0° | +36.9° | 请求 700 ms。GPIO41 低高边沿后显示 `ZERO SET` 并稳定为 −0.0° |
| 已校准停止快照 | −36.9° | −0.0° | 请求 2350 ms。GPIO41 低高边沿后显示 `ZERO RESET` 并恢复 +36.9° |
| 已清零停止快照 | +0.0° | +36.9° | 无输入，控制帧与原版逐字节一致 |

三组画面均为来宾生成的 BUBBLE。通过模型 MPU6886 的实际寄存器读取得到平放和 +0.75g 两组输入。每组保留无按压控制。重新导入后先观察显示，再执行按键。两次按键沿实际控制器通路送达。所用时长来自各自的虚拟计时回执。

离线比较两份停止快照与三个同会话 ZIP。每个 ZIP 通过 CRC 及八项清单文件长度和 SHA-256 验证。完整 OTA0 位于 `0x10000`，长度 `0x330000`，逐字节等于原版规范化分区。区间 `0x9000–0xdfff` 为 NVS。校准与清零快照的 82 个不同字节全部位于此区间。读取活跃条目并复算 NVS 页头、记录头和 blob 数据 CRC 后，`level` 的 `off` 读出首项约 +36.869896°，其余五项为零。清零后六项为零，第三次启动退出前仍全零。 [NVS 存储格式](https://docs.espressif.com/projects/esp-idf/en/v5.3.2/esp32s3/api-reference/storage/nvs_flash.html) · [脱敏证据摘要](evidence/atoms3-spirit-cold-nvs.summary.json)

三个原生访客和专用服务均已退出，停止历史保留，Flash 已释放，活动租约为零。此结果覆盖明确保存的虚拟 Flash 经正常停止后冷启动。物理断电、异常退出、实际硬件、浏览器及新的 Reviewer 或生产运行均未执行。未验证其他按压时长，Burner 未提交。公开档案保留完整摘要、大小和证据哈希，省略原始 Flash、ZIP、运行位置和独有标识。
