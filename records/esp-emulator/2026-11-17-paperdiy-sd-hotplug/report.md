# PaperDIY 在运行中的会话内插拔 microSD

已有 native 模型在开机时按 SPI 镜像是否打开设置 GPIO48。运行中切换需要
让 SPI 与检测开关共享同一张卡的在位状态。补丁将 PaperDIY 的两条 GP-SPI
路由接入共享卡状态，并在插拔时更新 GPIO 输入与中断。拔卡清空卡协议状态，
底层仍保存会话拥有的扇区。

## 复验

用 ESP-IDF v5.5.4 构建 `PROBE_PAPERDIY_HOTPLUG=ON`，以 16 MiB Flash
配置合并 BIN。按仓库夹具步骤构建 64 MiB FAT32+MBR，写入
`FIXTURE/ROM.BIN`。在隔离服务设置 `M5SW_SPI_SD_TRACE=1`，执行
`tests/firmware/spi_sd_media/run_hotplug.py`。设备初始有预备介质但未插入。
按插入、拔卡、重新插入和再次拔卡驱动同一个原生 QEMU 进程。

GPIO48 来宾 IRQ 顺序为 0、1、0、1。SPI 控制器 CMD17/CMD24 增量依次为
9/6、0/0、8/0、0/0。空槽和拔卡期间 ESP-IDF 实际挂载均超时。
重新插入完成新一轮卡初始化，并读回先前写入的 `PROOF.BIN`。
停止前收取并校验证据 ZIP，停止后用 API 清单及独立 FAT 读取核对文件，
并核对导出 artifact 的 SHA-256。运行进程退出，租约释放，原始镜像字节不变。

旧后端仍允许开机挂卡，但拒绝带初始拔卡选项的请求。新后端在没有准备
镜像时拒绝插入。额外的常规开机挂卡来宾通过读写及同会话复位，空卡启动
仍报告 GPIO48 高电平。全部 162 层 native 补丁可正反重放，构建源码逐文件匹配。

首次验收脚本因依赖缺失退出，第二次因独立服务缺少运行资产而未启动来宾。
资产齐备后的两次运行分别通过独立 FAT 检查和签入的 HTTP 回归工具。

## 边界

这是虚拟设备和一张会话拥有的可写介质的验证。运行中切换到另一份镜像、
实机机械和电气、浏览器及特定应用的拔卡恢复仍未执行。可以回退到只支持
启动时挂卡的原生构建。Burner 未提交。

[复验摘要](evidence/paperdiy-sd-hotplug-summary.json) · [原生补丁](https://github.com/m5agent/m5stack-esp-emulator/blob/563d4debf6ae11f4bd4092aba920f56aa82df772/patches/qemu-m5stack-peripherals/0215-paperdiy-sd-hotplug.patch) · [PaperDIY 官方引脚](https://docs.m5stack.com/en/core/PaperDIY_Complete_Kit#microsd)
