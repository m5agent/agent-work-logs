# 四款主机的接入与执行记录

用户要求把新建四款 3D 模型接入现有模拟器并测试若干固件。模型源固定到 `de6cddc065674ecb53bba29c7fe90d9ab4ee32f7`。三个 ESP32-S3 板型新增独立原生配置。CoreMatrix C158 使用 ESP32-C61，固件头的芯片身份保持独立，避免和 C6 混用。

## 实现和复现

- 原生 Xtensa 构建沿用仓库 bootstrap 的 QEMU 补丁序列。新增两款 Paper 的 `0168` 和初代 Cardputer 的 `0169`。使用专用测试实例和 state 目录启动 Device Service。若 QEMU 未注册对应机器，设备列表报告后端缺失，创建在启动 guest 前失败。
- 两款 Paper 可通过 `tests/firmware/paper_runtime/run_test.py` 重放。PaperS3 使用发布版 Factory V0.5。PaperDIY 使用原厂 V1.0 demo 源码及独立的 `factory_done` NVS，以进入二次启动后的按键页面。官方 UIFlow2 v2.5.4 和带输入绘图探针的复合镜像分开验收。
- 初代 Cardputer 可通过 `tests/firmware/cardputer_k132_stock/run_service.py` 重放。三个样本为 Factory V0.8、Factory V0.9 和官方 UIFlow2 v2.5.4。完整工作台试验使用 Factory V0.9，实际操作为浏览器上传、聚焦 3D 外壳并按 A。
- C61 诊断 QEMU 单独固定 Espressif 上游源码和两份补丁。通过 `tests/firmware/corematrix_backend_feasibility/run_service.py` 运行 IDF 固件，以真实 HP I²C 命令、FIFO、IRQ 驱动 PM1、M5IOE1 和 TM1680。相同 QEMU 的 `run_stock.py` 另行记录未修改的官方镜像结果。

## 观察

- PaperS3 原厂 GT911 触点 `(113,347)` 更新目标图标区域 607 像素。PaperDIY A/B 分别按住和松开，各自区域变化 533 像素，另一键区域 0 像素。两款 UIFlow2 原始镜像都能出画面，探针镜像分别读到触点和 A 键并绘图。
- 初代 Cardputer 工作台的 A 键到 QEMU 原生键矩阵，LCD 从启动提示进入应用菜单。另在原生 Device Service 验证 Factory V0.8 的 Q、V0.9 的 A 和 Fn，及官方 UIFlow2 的 F12/G0。单独组成的 UIFlow2 LittleFS 替换镜像失败记录保留。
- CoreMatrix 同会话 9 个断言覆盖 A/B/C、A+C 同按、独立松开、PM1 位状态与实际 16×16 显存。官方 UIFlow2 输出 Wi-Fi 初始化标记，15 秒采样无可用点阵画面。另以 `--workbench` 在 Chromium 的 3D 外壳复验同一探针的 9 个帧状态和 8 个输入，验证固件上传、会话创建和跨域均被拒绝。
- PaperS3 的隔离浏览器原型使用同一原厂镜像，真实鼠标点按两次驱动目标图标变化，停止后确认 Worker 回收。该实验使用独立 esp32sim 构建。四款模型的 WebGL 帧映射和 Cardputer-ADV 模型回归单独通过。
- 原生 PaperMono 和 Cardputer-ADV 的官方 UIFlow2 v2.5.4 在同一合并版 QEMU 通过启动与画面回归。
- 两款 Paper 的正确原厂和 UIFlow2 镜像通过导入，两次已知原厂镜像跨型号导入均返回 `firmware_board_mismatch`。
- 原生 Device Service 会话先导出证据，再停止、释放可变 Flash，并保留历史。

## 边界与回滚

真实硬件和新增机型的正式 QEMU-WASM 未运行。原生 Paper 的数字扫描不授予墨水屏物理灰阶、时序和音频结论。CoreMatrix 官方应用路径仍缺少必要运行时覆盖。正式工作台的普通 C158 固件准入保持关闭。

回滚代码应恢复本次提交前的设备和模型目录、QEMU 补丁序列和运行时配置。实际运行时替换由独立 Device Service 的运维流程负责。
