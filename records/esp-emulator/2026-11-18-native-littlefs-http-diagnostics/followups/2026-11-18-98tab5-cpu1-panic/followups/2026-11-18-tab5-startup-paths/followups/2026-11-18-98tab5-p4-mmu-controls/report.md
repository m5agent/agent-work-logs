# 98TAB5 原版冷启动故障与 P4 双核缓存/MMU 对照

固定 Device Service `c7e25be5410d3a9968107bc7a0cab5acb9d708bc`、原生 esp-emu 1.1.0、Tab5 GT911 板型与同一 ROM、eFuse、C6 工件。原版 1.3.0 上传 SHA-256 为 `ea4fb0889e4a2c68d472947137908c52c25a663152d3ff78262ce2605440dc6d`。载入 Flash 和各运行工件的 SHA-256 见回执。[原版诊断沿革](../../README.md) · [上游固定版本](https://github.com/espressif/esp-emulator/tree/34ba27a6e5a3da41743fc861b462cf2452f0ca28)

## 原版自然故障

不连接调试器，各观察约 64 秒。不挂卡时和通过 slot 0 挂入固定 32 MiB FAT16 合成 NHD 时，各记录 34 个 ROM 启动标记、33 次软件复位、零完整帧。两份 152,921 字节串口完全一致。有卡时验明租约拥有的 SD 副本、ZIP 存储回执及停机导出，导出和原始 SD SHA-256 相同。此前同原版打开过合成 NHD，该观察来自调试改变时序后的启动。[原版自然对照](evidence/98tab5-c7e-stock-natural-and-panic.summary.json) · [合成 NHD 历史对照](../2026-11-18-98tab5-synthetic-hdd/README.md)

独立诊断只在 panic 入口设断点。捕获 CPU1 的指令访问异常，`mepc=0`、`mcause=1`、`mtval=0`、`ra=0x4fc02752`；当场 L1/L2 的 raw 及 masked 错误位均为零，其他寄存器多回读同样的通用值，未取得发起访问地址。重新核对先前另一启动的 CPU0 保存帧，在实际 ROM 中 `mepc=0x4fc187d4` 是内部 SRAM 栈上的寄存器保存。相邻调用是仅针对 L2 的地址失效，参数为 `0x408a0000` 起 64 KiB，范围与 CPU1 调度目标项 `0x4015cc58` 分开。已观察到 Flash MMU 选择器 `0x8a` 与内容 `0x1000`，依 ESP32-P4 定义是有效物理页零。更早读到的是另一个选择器，无法建立同一条目的改写关系。[SDK 位定义](https://github.com/espressif/esp-idf/blob/735507283d5b2f9fb363a1901172dbd9e847945d/components/soc/esp32p4/include/soc/ext_mem_defs.h#L54-L60)

## 可重复双核对照

两份 ESP-IDF v5.5.4 固件各执行两次独立普通会话，合计四次，均通过。每次都保留通常的中断看门狗和两个空闲任务的任务看门狗订阅。CPU1 使用实际 DROM 的 volatile 读取，基线由 CPU0 读取另一页，操作阶段由 CPU0 调用原生 ROM 的 L2 定向失效。扩展固件额外经 SDK API 映射 Flash 物理页零，核对引导器字及其物理偏移，随后释放别名并查询确认已失效。两次复验的同固件串口逐字节一致。

| 对照及每次调用数 | CPU1 总读数 | CPU0 调用期间计数 | 错读 / 零读 |
| --- | --- | --- | --- |
| 仅 L2 固件，基线 6,656 | 3,742,969 | 2,856 | 0 / 0 |
| 仅 L2 固件，L2 失效 6,656 | 3,737,426 | 54,095 | 0 / 0 |
| 扩展固件，基线 6,656 | 3,742,709 | 2,841 | 0 / 0 |
| 扩展固件，L2 失效 6,656 | 3,737,422 | 54,148 | 0 / 0 |
| 扩展固件，映射及释放 416 对 | 3,497,189 | 418,595 | 0 / 0 |

调用期间计数取 CPU0 软件进出标记两端一致的样本。它覆盖来宾调用窗口，未测量 cache 停止到恢复的硬件临界期。已验证正常应用阶段的这两类操作。原版双核交接阶段的映射可见性和执行先后仍待隔离。[两类对照与原始包哈希](evidence/98tab5-p4-two-hart-cache-control.summary.json)

## 复现

从对应 [仅 L2 工程](code/mapped-l2/) 或 [扩展映射工程](code/mmap-pagezero/) 构建。使用固定 ESP-IDF v5.5.4（`735507283d5b2f9fb363a1901172dbd9e847945d`）和 RISC-V GCC 14.2.0 `esp-14.2.0_20260121`，设为 ESP32-P4 rev 3 之前的配置。通过 `idf.py -B BUILD build`、`idf.py -B BUILD merge-bin --fill-flash-size 16MB` 生成实验映像。编译时间影响镜像哈希。使用回执固定的服务和原生后端，通过标准 API 上传、导入、创建隔离会话，取串口 `CACHE_XCORE_*` 标记以及停机前证据 ZIP。复验原版时分别以无卡及固定合成 NHD 运行，保持正常时钟、双核和缓存配置。所有会话都核验 ZIP 清单，停机且归还租约。未提交 Burner，未验证真机、浏览器或可启动 PC-98 系统。
