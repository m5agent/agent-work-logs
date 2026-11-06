# 存储保留与 clone 审计报告

本记录针对工程目录的大体积与 clone 大小混淆，分别实测网络 clone、审查 ignored
存储的保留价值，并对可再生成物与关键磁盘字节采用不同保留方法。本轮主机存储审计与清理 `PASS`：
三项小批次及10个旧scope、14个已完成service scope均已完成。
所有数字只覆盖本轮，不重复累计此前清理。

## 普通完整 clone 的实测

对公开仓库进行一次普通 `git clone --progress`，未使用 depth/filter，也未初始化
submodule。审计 HEAD 固定为 `ea6a553b…`，精确身份和完整观察见
[clone 摘要](evidence/clone-summary.json)。默认 12 个 tags 已核对，接收 pack
124,055,040 B（118.308105 MiB），checkout 连同 Git 数据落盘 389,599,232 B
（371.550781 MiB）；本次耗时 7.169 s 只是一条样本，不是速度保证。

pack 是 Git payload，不含 TLS/HTTP 等传输开销；磁盘值是文件系统 allocated bytes，
不是源码逻辑字节。当前 tracked 文件 5,117 个，`docs/evidence` 为 5,189,708 B
（约 4.95 MiB）。较大的已跟踪内容主要是模型几何/美术资产与固定 WASM，不能当作
无价值证据删掉。忽略规则与实际 HEAD membership 都检查过；仅写入 gitignore 并不
能排除已跟踪文件。没有额外 runtime/cache 自动下载，也没有当前 submodule/LFS 隐式载荷。

原 checkout 的本地 Git objects 还服务其它 refs、reflog 和已登记 worktree。
“不可从这个 HEAD 历史到达”不等于可删除，本轮未执行 prune、ref 删除或历史重写。
审计仅创建、测量并移除了自有临时 clone，原 checkout 跟踪文件和 Git 引用保持原状，未改写对象历史。

通用复现入口：先给下列变量指定自有空目录与摘要中的审计 SHA；远端变化应另记一次
观察，不套用本次数值。

```sh
git clone --progress https://github.com/m5agent/m5stack-esp-emulator.git "$OWNED_CHECKOUT"
git -C "$OWNED_CHECKOUT" rev-parse HEAD
git -C "$OWNED_CHECKOUT" rev-parse --is-shallow-repository
git -C "$OWNED_CHECKOUT" count-objects -vH
du -sk "$OWNED_CHECKOUT"
```

## 已完成存储处理

| 范围 | 操作与验证 | 本轮净计入 |
| --- | --- | --- |
| qstr.i.last | 34 个单链接生成中间文件；Make/CMake 的预处理生成规则可重建。1,450 个关键文件 SHA、19 个源仓库 HEAD/status/跟踪 diff 前后不变 | 3,440,599,040 B |
| boot.vfat 副本 | 完整字节等于保留 base 的 offset 8 MiB、length 512 MiB 分区；base/XZ/QCOW2 身份不变 | 536,870,912 B |
| work raw image | 8 GiB 逻辑镜像无损冷存；完整实际恢复的 SHA、大小、权限/owner/group/nsmtime/flags/xattrs 及 QEMU raw compare 通过，再释放展开副本 | 4,529,401,856 B，已扣 archive 和当前小报告 |
| 三项小计 | 每个被释放 inode 只计一次；不含下述大批次及此前清理 | **8,506,871,808 B，约 7.922642 GiB** |

qstr 是 C/C++ 预处理输出，用于后续 qstr/module/root-pointer 等生成，不是运行输入。
保留最终 ELF/bin/config/source；以后按原构建配方重新生成即可。本轮没有触碰其它
`.last`、当前 runtime、原固件或已有未提交修改，也没有新建固件构建/guest 验证。

work image 原 allocated 为 6,968,049,664 B，冷 archive allocated 为 2,438,598,656 B；
再扣 49,152 B 当前报告/恢复指引，得到表中的净收益。源 raw 与实际恢复的完整 SHA
相同，archive 自身也有独立 SHA；数值与保护对象的完整身份集中于
[已完成摘要](evidence/completed-storage-summary.json)。稳定 base、XZ 和 QCOW2
的全部内容/元数据保持不变，backing chain 未变。删除前重新检查 open/mount 与源身份。
五个 direct probe 默认需要该 work image，必须先恢复；不能把冷存描述成随时可直接运行。

`df` 受 APFS 共享 extents/snapshots 和并行工程活动影响，分别保留观察，不能替代逐
inode allocated 或扣除 archive 成本后的计数。原始证据并非全部无价值：原 ZIP、
输入/输出、首轮失败、帧、source/toolchain provenance 和需要的 Flash 字节继续保留。

## 保留的失败与冷归档门禁

APFS 大 raw image 压缩试验中，复制命令退出成功，但 UF_COMPRESSED 未设置，副本
反而多占 469,024,768 B。原 stable image 未替换，agent 自有副本已清除，该临时空间
恢复不计净收益。只读 raw compare/backing metadata 通过，只能说明普通副本字节
一致；压缩 raw 的 guest 兼容性没有建立，启动/写入测试 `NOT RUN`。

较大冷归档的首次恢复因 scratch 继承 group 与原始 group 不同，被严格比较挡住，
当时未删除任何原文件。补加 `--same-owner` 后，独立格式试验的 owner/group、nsmtime、
ACL/xattrs、ResourceFork/FinderInfo、硬链接等通过，原 PAX xattr 值另行检查。
没有放宽 group 比较。跨包真实 relink 后两个 scope 的全量复验及 parent-symlink
负控、嵌套 scope 与 hot 邻居排除也各有独立试验。这些预演不代替实际 10/14 批次终态。

两批均已终态完成：24个scope共56,634条regular路径完成实际解压与逐项核验，按包释放原展开文件。两批净回收33.419331GiB，完整原字节、归档/manifest/proof哈希及成本分列于[批次摘要](evidence/archive-batches-summary.json)。不把原始文件释放bytes直接当作净收益。

第二批首包在源数据已验证冷存后写RESTORE占位遇到变量命名错误，保留小失败记录；复核根身份、空目录、归档/manifest哈希与热态邻居后完成占位和journal，随后才执行其它13包。归档始终有效，没有数据丢失，也没有扩大清理范围。

## 隐私、恢复与边界

原始 service 归档可能含内部网络、会话和请求数据，仅本地保存（archive `0600`、
私有目录 `0700`），不附公开下载链接。公开内容仅为派生 summary、hash、counts 与通用
复现步骤，不含宿主绝对路径、端点、账户/设备唯一标识或原始私有数据。脱敏摘要不标为 raw。

通用恢复顺序：先核对 archive SHA，选择自有空 scratch，实际完整解压；检查原文件
SHA、metadata、路径成员和链接拓扑，拒绝覆盖新数据或 active/mounted image。

```sh
zstd -d -c "$PRIVATE_ARCHIVE" | tar -xpf - --same-owner --mac-metadata --acls --xattrs --fflags -C "$EMPTY_RESTORE_DIR"
shasum -a 256 "$EMPTY_RESTORE_DIR/$IMAGE_BASENAME"
```

此处环境为 macOS 原生 tar；按私有原始 manifest 核对后才恢复原位置。包内 ZIP 必须
保留原字节，不重新打包；跨包硬链接按全局索引安全重连，再复验全部 scope。
AppleDouble 是封装元数据，不是新的原始证据文件；操作系统 provenance-only 变化
需独立审计，原值必须仍在 archive 中。恢复先验证 owner/group 和权限条件。

项目[历史证据规则](https://github.com/m5agent/m5stack-esp-emulator/blob/ea6a553b702c636b10692665c475341b178cb662/docs/evidence-retention.md)
允许普通 checkout 不依赖本地大材料；显式历史审计前仍须还原完整材料及对应历史
checkout。冷存改变可用方式，不改变原 PASS/FAIL，也不改写固定 commit 的证据索引。
原有 M5Stick 声明输入缺失边界不由本轮归档造成，不能宣称所有原始输入均可用。

回滚：qstr 按保留配方重建；boot 副本从固定 base 分区重新提取并核对 SHA；work image
从完整冷 archive 恢复，不 rebase/覆盖稳定镜像或 QCOW2。产品源码不变，故无代码
revert。物理硬件、browser-WASM、guest 启动/写入、服务功能及长期保存介质可靠性
本轮均 `NOT RUN`。各包实际终态已记录；使用发布脚本推送，并以两端固定commit回读完成交付。

## 最终收口

24个目录全部按包完成真实完整解压、逐文件SHA与元数据检查后，才释放展开副本。新增冷归档、索引、证明与占位均计入净收益。连同生成缓存和旧工作磁盘，本轮按组件账净回收41.341972GiB；项目目录独立du从147.808456降至106.466908GiB。两者微小差异含目录元数据和并发小文件。源main仍ea6a553b且clean，refs与30个工作树不变。用户明确选择保留进行中任务，约27.4GiB目录和现有服务未动。详见[最终空间核验](evidence/final-space-summary.json)和[两批实际证明](evidence/archive-batches-summary.json)。

每包原始字节和PAX原属性均保存。第二批恢复时macOS新增的provenance另列6007次OS事件，不把它描述为所有属性逐字相同；其它受支持元数据核验通过。旧磁盘5个直接探针需先恢复，历史审计需完整历史输入。完整24包一次性展开未执行，每包真实验证和跨包hardlink独立控制分开记录。
