# 原生存储复用与分步配网

## 存储

Device Service 先复制源文件。可写 FAT32 在 active guest 时拒绝清单和导出，停机后生成只读内容寻址 artifact。原生 SDK 同 guest 对照覆盖初代 Cardputer、Cardputer-ADV、PaperS3 的预置文件、目录、写入和重挂载。初代 Cardputer 的第二个会话直接消费导出 ID 并读回写入。服务重启后导出同一 ID，源卡保持同一 SHA。此前误把访问日期字段用于过滤目录项的结果保留在 SD 证据中。

内部数据分区夹具基于已准入镜像的标签、类型、边界、几何及 SHA。主机只覆盖会话私有 Flash 并记录 PREPARED，随后由 guest 驱动证实目录和文件行为。UIFlow2 LittleFS 在初代 Cardputer 和 StickS3 上读预置文件、写入、复位并读回。ESP-IDF SPIFFS 在初代 Cardputer、StickS3 和 Dial 上完成预置、读写和重挂载，初代同会话复位持久化。四项错误参数在分配前拒绝。保留原 artifact、padded Flash、目标原分区、fixture 与有效 Flash SHA，实测区间外字节一致。

LittleFS 首次客户端错误把会话受理状态 202 当成 201，随后一次探针字符串转义未通过 guest 语法，另一轮误把原始 artifact 的 SHA 当成准入后补齐 Flash 的 SHA。最终运行校正三项，保留停止的会话、ZIP CRC 与复位串口标记。

另在两套隔离服务执行保存快照复审。调用方上传经校验的 ESP-IDF SPIFFS 夹具，再将同一 ID 交给审核。guest 串口证明预置读取与重挂载，ZIP receipt 与 session 相同。探针未绘制界面，所以固件审核判定是 E_NO_FRAME。

## 原版 Stock Ticker

使用未改变的保存快照与隔离 Wi-Fi。审核等到首页，侧键 B 长按 6200 毫秒，确认菜单，再发正面 A 点击进入热点页。实际 GPIO 边沿、三处有效画面、持续 60 秒观察和 guest Beacon 来自同一会话。Ethernet pcap 为零包，AP 关联与 portal 保留 NOT RUN。审核将输入步骤记为通过，网络保持 E_NETWORK_PARTIAL。早期侧键 A 与精确五秒 B 的失败单独保留。

## 复现和边界

使用执行记录中的原生运行时及对应 ROM 启动独立 Device Service。SPIFFS 编译输入见模拟器候选的 tests/firmware/spiffs_partition，准备脚本可重建基底和夹具。LittleFS 专用文件见 code 目录，按原 UIFlow2 底包的实际 VFS 几何打包，预置 /fixture/seed.txt 为探针读回的内容。将合并固件与分区文件分别上传，创建带 storage.filesystem 的会话。复位前后观察独立串口标记，先取证再保留停止的会话。SD 导出用停止后 storage/sd/export 返回的不可变 ID 开新会话。

两个隔离复审均关闭提交，Burner 提交数为 0。物理硬件、WASM 和常驻部署为 NOT RUN。
