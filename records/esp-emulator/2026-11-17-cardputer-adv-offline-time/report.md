# 同一来宾的实际配网与授时

隔离 Device Service 使用 Cardputer ADV 的原生 Wi-Fi，给独立会话提供封闭 Unix Ethernet 对端。审核显式选择该夹具，ACL 对应用专门放行。四个画面和串口门槛确认原始固件完成了界面流程，来宾从实际虚拟网络接收 DHCP、固定 DNS 和 SNTP。

原始二进制的 SHA 保持一致，正常 saved-snapshot 路径在冻结运行时中观察了约 60 秒和 13 个样本。来宾报告时间与响应内容对应。服务回执和 pcap 汇总对响应载荷验证相同 SHA。独立负对照保留 DHCP 和 DNS，并扣留 SNTP 响应，来宾无同步标记。独立 ACL 拒绝用例与原有 StickS3 SoftAP 复位回归通过。

公开卫星应用 HTTP 属于未验证的声明。最终审核结果维持部分验证，证据包已停止会话并核对零租约。记录无原始 BIN、凭据或捕获文件。正负对照的原始源码复现入口保留在项目 `tests/network/native_sta_peers/original_skycompass/`。
