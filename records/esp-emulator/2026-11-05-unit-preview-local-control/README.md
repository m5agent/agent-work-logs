# Unit 模型预览与本机 Preview 控制

- 日期：`2026-11-05`
- 结果：`PARTIAL`：源码验证完成；PR、Pages及现有用户Python进程更新待交付。
- 工作类型：`code_change`、`report`。
- 来源：用户要求 Unit 目录可单独查看模型，并询问本机运行代码是否必须手填认证值；无公开 Issue。
- 源码：[m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)，base `082fffafd124800564d11c82b56cc4ecbb2c503d`；提交 [22001fe1cb6bb44eb2737872e4cc578605e57921](https://github.com/m5agent/m5stack-esp-emulator/commit/22001fe1cb6bb44eb2737872e4cc578605e57921)。
- 环境：独立模型浏览器、隔离原生 CoreS3+PIR，以及预览保持打开的 CoreS3 browser-WASM；物理硬件未操作。

## 当前结果

Unit 目录恢复独立可视模型，选择/关闭/重开不会改变主机装配草稿，Add仍显式加入主机。
模型预览不绑定 guest Unit 控制器，不能用预览点击或外观代替实际外设输出。

Preview API 对没有配置认证值的部署增加限定本机入口：监听与连接来源均为loopback，Host为严格本机字面地址与实际端口，
浏览器Origin须精确同源；跨站/矛盾Fetch Metadata拒绝。配置过认证值时current/previous规则不变，远程不获得免认证。
这不是其它旧API的全局CSRF保护或沙箱。

已完成的限定证据为host20、原生无Bearer CoreS3+PIR14、Unit预览打开时的完整CoreS3浏览器65项。
最终Python共1986项（1976通过、10跳过）、Node30、文档50、4个验证器及scope均通过。现有用户服务未修改，本记录不表示该服务已加载新Python。

## 证据与导航

- [report.md](report.md)：实现、拒绝边界和保留失败。
- [run.json](run.json)：分层状态与精确镜像身份。
- [host20](evidence/host-summary.json)：模型生命周期、Add/草稿隔离、4种宽度和实际页面合同。
- [native14](evidence/native-tokenless-summary.json)：自然Origin、8个无Authorization POST、同VM原驱动/帧/ZIP与正常清理。
- [browser65](evidence/browser-preview-summary.json)：预览留开、12次raw-paste/2次默认代码、原完整编辑器与两阶段清理。
- [auth合同](evidence/auth-policy-summary.json)：28项纯上下文/真实HTTP方法；非guest证明。
- [最终检查与包](evidence/final-validation-summary.json)：源码逐文件绑定、首次metadata失败、完整检查、静态包闭集。
- patches/、code/不另附；上述固定源码提交包含实现与测试入口。

## 未覆盖

其它主机/Unit、远程无认证、全设备矩阵、新HTTPS部署、物理性质、性能、现有用户进程迁移及原运行时根因不继承本次结果。
