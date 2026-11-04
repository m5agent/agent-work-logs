# 正式云端与新本地资格检查的独立结果

主源码23d38d8dbe91488185dc53eb4cd47dee687df019，树f892649011246b88cb76e3b2ad2973fe76ec99ee。
本记录只摘录已终态的原报告。父60流程的FAIL保留，未运行项不补成通过。

## 三条路径

正式attempt2实际已完成sourcebuild与export/ABI/Canvas host控制，随后Matrix首个UIFlow case
600000ms没有ready。4个UI检查通过、0program；1FAIL/59NOT RUN。这里是实际guest失败，
与attempt1下载TLS失败不同。正常QMP/disposal未建立，held-iframe围栏未采到，最后5CDP均关闭。

本机同版本CfT152/M4跑原8f9脚本，一次完整Matrix58checks/11program/reset和正常5CDP两阶段
通过；hosted152/PV在packaging/signature/host上不同。相同五runtime资产包括96ea WASM，
仍保留合法localfa6与formal9c两个runtime manifest；不能伪装同一个producer，或据本机PASS定因。

新的MAIN23d/prod-prefix immutable export使用manifest685e134cbaa09bf44edf45218843d387b26cf9e775b75cdf21b8ce3024539e7d、
合法fa6 runtime/96ea资产。完整计划60，终态17completed、16PASS、Lite1FAIL、43NOT RUN。
Lite首次boot和10program已执行，48个已完成check均true；硬reset新启动时Core1
LoadStorePIFAddrError，PC403864c3、EXCVADDR6002306c。精确oneInsn/divisor1、无icount，
不能继续把oneInsn说成已保证reset稳定。原FW5c06…和脚本8f9…保持，不降断言。
Lite正常QMP0/零fallback、6CDP关闭，held-iframe未采；AtomS3R peer63PASS正常drain并双阶段6CDP关闭。

## 后续范围

停止该新export的发布资格推进；没有release promotion/deploy/HTTPS40或DOM执行。
现有公开站点未被本轮替换。原因仍OPEN；源码、时钟、输入、固件及断言未在此检查点改动。
后续诊断与任何新尝试必须单独留证，不能覆盖这些FAIL，也不能借旧R8或单CfT控制授予全60。
本记录为既有实际执行报告的有界派生摘要；未新增guest、构建或修复。
