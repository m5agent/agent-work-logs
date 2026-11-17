# 审核存储复用与分步配网

原生 Device Service 已通过 FAT32 导出复用和 LittleFS/SPIFFS 的实际挂载。
原版 Stock Ticker 可通过同一会话的两步输入进入热点页，应用网络数据面仍为 NOT RUN。

- [复验与边界](report.md)
- [执行记录](run.json)
- [SD 导出](evidence/sd-export.json)
- [SPIFFS](evidence/spiffs-http.json)
- [LittleFS](evidence/littlefs-http.json)
- [保存快照里的 SPIFFS](evidence/saved-spiffs-replay.json)
- [原版分步配网](evidence/stock-ticker-setup.json)
