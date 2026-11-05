# PR170交付与限定验收

## 已确认交付

[PR #170](https://github.com/m5agent/m5stack-esp-emulator/pull/170)由源码 `22001fe1cb6bb44eb2737872e4cc578605e57921` 合并为 `84b4f4932a402b77c9688aff7b51a1932ff12be6`，二者tree均为 `3b4b073ee1fe9f2ade55ec64141adf2799e1e7d6`。四项CI及[合并后main CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41964268536)成功。
正式发行包147,128,260字节，发布后全量下载SHA为 `e56d7e9faeeea1ff4cd651b51fc8ab366208b94502362f2d576ba0a5e75f695b`，与首次包一致。
[Pages运行](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41964338671)成功，实际HTTPS manifest为 `23ee838732c99369d2b0b852b4430c46eee48236ed768a88d9374a5969cc8b2c`；全部2134资产/251,980,691字节在86.276秒内完成HTTPS读回，零mismatch。

## 现有服务与保留失败

经授权更新现有本机Python进程，保留原状态和worker配置，handoff时无活动会话；无认证值的Preview GET实际返回200。HTTP返回的HTML/JS/CSS字节与合并源码精确一致。真实浏览器只读13项通过：统一工作台标题、独立PIR模型canvas、Add按钮与认证帮助文案正确；实际无Authorization的Preview GET返回200。API写入、guest创建、WASM/Worker/iframe均为0，活动会话/lease为0，浏览器已关闭。公开摘要从私人页面观察派生脱敏，原件只留3,762字节/SHA，不提交截图。
首次启动因现有终端工具不支持所请求的日志选项而失败，采用兼容的终端配置恢复；该宿主启动失败保留，不描述为产品或guest失败。
此次没有在实际用户服务创建guest。此前隔离原生CoreS3+PIR的14项virtual-device validation，才是无手填认证值与实际运行、PIR数据/帧、同VM程序及清理的证明。

## HTTPS限定验收

实际生产HTTPS的CoreS3完整65/65通过：原12次raw-paste、2次未修改默认代码、UTF-8/多行/错误恢复、文件导入、中断后同VM运行、真实红帧和硬重置0→1恢复全部保留。PIR独立可视模型在运行前后保持同一个DOM root，主机附着Unit为0、picker为空，不能解读为PIR外设运行验收。

站点manifest为上述23ee，runtime manifest `fa6b56048ec91d100cb4f2a15088ce77e313bd2e6e8ba083229826b258297c51`；WASM `96ea9f91956aa80926182ed174ea426f3f4c84e96ca58754fa249063fdda5ca1`，Flash `52f38f562f6e3749357a2ed4834efd72d16870046ea052f2f31691743cb5384d`。精确策略为div1、无icount/clock override、oneInsnPerTb=true。

正常QMP退出0，forced与engine fallback均0；iframe移除前与context关闭前两次实际CDP均observed6/live0，浏览器正常关闭。原大报告只保留5,174,368字节/SHA，提交13,825字节bounded摘要。原生、实际本机页面和浏览器guest结果分开；单次ready观察不作为性能比较。

## 边界

独立Unit预览只有视觉模型，不绑定guest外设；Add仍单独改变装配草稿。本次不增加其它型号或Unit验收，不建立RF、电气、物理、性能或全19板声明。
首次记录的两个native观察器FAIL及inventory元数据FAIL不被交付成功覆盖。该后续只补合并、包、部署与限定在线结果，不重新解释旧运行时根因。
