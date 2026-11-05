# 唯一 main 收口：验证与保全终态

## 目标及授权变化

前一轮盘点确认26个本地分支、25条工作树、远端仅main、12个tag和1个stash。用户随后要求完成剩余工作、合并必要改动并清理无关分支，又明确最终仅保留一个main分支。新的明确要求替代此前在线保留attic引用的安排；历史通过独立离线Git备份保全，不能把这一变化追溯成此前已有授权。

## 根因及最小改动

三个主题各有一个与main完全补丁等价的提交；PR166两个docs提交累计diff与main squash完全相同，四个dated evidence文件逐字保留，无须重复合并。

`pages-system-browser` 的直接脚本Chrome兼容补充仍独有。canonical发布gate已归一化环境，但直接运行 `test_public_qemu_guest.mjs` 仍只读取旧变量，因此不能以gate存在为由称旧提交完全合入。真实merge `ef60f88168b60bc8da685cd007f6658ce0bc0361` 的父提交为base `84b4f4932a402b77c9688aff7b51a1932ff12be6` 与兼容提交 `0569b2391e599012d566c61be76cc38c23afb387`；范围仅两个测试文件、4行增加/1行删除。没有Web、运行时或固件改动。

## 同路径虚拟设备验证

实际执行当前tracked直接runner，令优先Chrome变量指向已配置Chrome，而旧fallback变量指向故意不存在的路径；两代guest均成功启动并完成49/49检查。CoreS3 stock-reference profile为div1、oneInsnPerTb=true、无icount或clock override。WASM为 `96ea9f91956aa80926182ed174ea426f3f4c84e96ca58754fa249063fdda5ca1`，固件为 `78961297e751ec9c743b4cdf89cc2c137e7e2c801dda3ead9df2ea45d59fbd3f`；其余源代码、ROM、站点和runtime manifest身份均由有界摘要绑定。

观察包括LVGL ready、实际可信pointer输入、点击结果及帧像素、负例触摸、PIR QOM与guest两次转换、QMP pause/resume、四种宽度、共享参考重新打开和第二代输入。两次正常guest退出码均0，强制pthread处理和engine fallback均0；实际CDP在第一代与第二代累计分别observed6/live0、observed12/live0，且在iframe移除前和移除后均成立。浏览器/静态server在finally关闭，未请求Device Service或本地模拟器。

原报告164,077字节，SHA256 `67a1842496fb1963590dd3eb3846c09d856e8950cc250a09bd038f31ca295eff`，不提交。11,157字节有界摘要逐字提交，SHA256 `cc27733d9dfce6e0dd98c49049da8357312fc539c133d7a2fbdb699f1accc815`。

## 相关检查

public-site专测10/10、Node语法、全平台unittest 1986项/148.200秒/OK（skipped10）、30个Node contract脚本、runtime coverage/peripheral catalog/QEMU profiles/project snapshot四项检查、diff与PR scope均通过。PR scope记录4个新blob/70,339字节、源码证据新增0字节；工作记录证据在独立仓库保存。

首次Node contract启动因缺少现有Playwright链接失败，随后使用已有锁定依赖通过，未安装依赖。该观察器/环境失败保留，不改写为guest失败，也不被后续PASS抹去。

## 历史保全及服务边界

清理前保存私有完整Git bundle，126,719,820字节，SHA256 `32bae6cc4cdb78b4d3b902a0b590ed859736da8ae513dd2a9b1c2b992a85980f`。独立bare恢复、fsck和cat-file验证49个引用对象全部可读，包含26个原本地分支及1个新增整合分支。公开摘要不复制本机路径、私有引用标识或备份本体。

用户明确允许结束其它不重要服务；实际操作先确认两个旧服务均为0活动会话、0lease，再SIGINT并观察正常退出。停止前首次检查因listener输出PID解析错误失败，发生在任何动作之前；修正解析并重新检查后才执行。其它受保护listener未观察到进程。本阶段要求保留的本地资产均未修改，服务结果不替代独立浏览器功能验证。

## 尚未交付的部分

23个旧分支绑定工作树已切换为各自原始HEAD的detached状态，文件/status均相同，原未跟踪日志哈希及跨工作树依赖链接保持不变；没有删除目录。源码PR尚未创建或合并，最终分支引用删除及目录退役尚未执行，因此本次整体状态PARTIAL：验证、保全与detach步骤PASS，delivery及最终ref/directory步骤NOT RUN。最终本地/远端仅main、资产及tag/stash保全、实际目录退役清单和main远端SHA将在独立follow-up追加。

## 限制与恢复

本结果仅为记录中精确CoreS3镜像/运行时/Chrome直接入口的virtual-device validation。没有物理硬件、其它板型、性能比较、长期运行或新Pages部署结论。Git引用与本机资产管理是独立管理面，不转授固件功能PASS。若后续删除需恢复，可从经过验证的私有bundle/bare备份按原引用SHA恢复；不应依赖reflog或假设已删除tip仍有命名引用。
