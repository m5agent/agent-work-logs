# 发布资格失败与独立控制检查点

日期2026-11-04；结果FAIL（发布资格）。本次只整理既有终态，没有新guest或源码修改。

| 路径 | 结果与边界 |
| --- | --- |
| formal41799916700 attempt2 | sourcebuild/静态host控制通过；Matrix首case600s未app-ready，4UIchecks/0program，59例NOT RUN |
| 本机CfT152/M4控制 | 一个原Matrix完整case58checks、11program/reset通过；不是58cases，不授cloud或全19 |
| fresh MAIN23d桌面完整60 | 17completed=16PASS+Lite1FAIL，43NOT RUN；Lite48项后硬reset出现Core1 PIF，尽管oneInsn |

本机CfT有正常QMP/two-stage5CDP；hosted失败只有最终5CDP关闭、正常QMP未建立，不能混用。
新Lite失败自身正常QMP0/零fallback、6CDP-before-context，held-iframe未捕获；并行AtomS3R63项
已正常drain/two-stage6CDP。此前R8PASS不被抹去，也不能转授这次失败的export/run。

新站点发布、release promotion、prepared-preview、HTTPS40/DOM均NOT RUN，existing publication
保持不变。原因仍OPEN；没有把相同runtime bytes写成不同producer的manifest相同。

- [report.md](report.md)：阶段、身份和清理边界。
- [run.json](run.json)：结构化状态。
- [evidence/summary.json](evidence/summary.json)：精确FW/runtime/source及raw byte/SHA。
- 无patch/code；大52KiB formal/CfT checkpoint只按hash引用，不重复归档。
