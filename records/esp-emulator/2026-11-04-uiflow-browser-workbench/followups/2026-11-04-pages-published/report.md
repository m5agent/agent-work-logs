# 发布结果与范围

PR #165合并为23d38d8dbe91488185dc53eb4cd47dee687df019，树f892649011246b88cb76e3b2ad2973fe76ec99ee。按维护者最新要求，使用现有prepared-preview流程部署已审的同一静态包，保留已知故障。

## 发布与资产

release标签pages-uiflow-workbench-20261104-23d38d8d绑定上述提交。public-site-preview-live.tar.gz为149451828字节，SHA256为09a7c91cb4fab05d886528d81bb43fe701a32bad24f3619340571be22e011f13；实际上传完成后的下载回读与本地相同。部署运行41816252534的prepare/deploy均SUCCESS。

公开HTTPS已返回429908字节的manifest685e134cbaa09bf44edf45218843d387b26cf9e775b75cdf21b8ce3024539e7d。全部2130资产共251196202字节与精确导出逐项一致，含WASM96ea、合法本机runtime manifest fa6及对应源码/许可。站点不打包ROM或固件，service_url为空。

## 实际HTTPS功能

浏览器使用桌面Chromium157/M4硬件ANGLE，每个case独立浏览器/VM，最多两个功能guest并发。Matrix、StickC Plus、CoreS3各运行完整编辑器和键盘/鼠标按键测试，保留原始源码、断言、250ms输入及退出要求；仅传输适配为实际HTTPS。

六例全部通过：222项检查、35个程序、6次未改默认样例执行、10组键鼠输入；正常QMP退出6次、零强制清理或fallback，实际CDP关闭按case为5/5/5/5/6/6（合计32）。编辑器3例的held-iframe围栏已采集，按键3例该围栏未采集，保持NOT CAPTURED。其余16板/34个HTTPS用例NOT RUN，不转授本结果。

可直接在在线页面选择这三款设备，启动默认UIFlow2编程环境，运行默认M5.begin/Hello源码，测试上传、错误恢复、中断与硬复位；按键结果来自同guest原驱动及控制器读回。详细固件/运行时/原脚本与派生脚本SHA、实际输入/输出和清场见有界证据。

## 已知问题与后续

完整资格检查仍FAIL：正式托管环境Matrix600秒未就绪；同MAIN导出本地完整计划在Lite代码运行后的硬复位出现Core1 LoadStorePIFAddrError（PC403864c3、EXCVADDR6002306c），此前16例通过、该例失败、43例未运行。StamPLC/Cardputer/Lite的RUNTIME-07/08/09仍开放。独立诊断通过和本次HTTPS子集通过均不关闭原缺口。

本次交付为携已知问题部署，完整门禁未授PASS。此前V6/R8本地全19结果保持其原身份；本记录没有新增物理、RF、电气或性能证明。无需回退本次已授权部署来等待以上故障定位；后续按缺口登记分别处理。

原始大报告、像素数组和浏览器标识保留在忽略的执行存储中，仅归档有界去标识摘要与原字节/SHA，不称为raw。
