# ESP Emulator Cardputer-ADV BMI270 当前参考固件闭环

- 日期：`2026-10-29`
- 结果：`PASS`
- 工作类型：`issue` + `virtual_device_validation`
- 问题来源：`FW-03` Backlog 中“Cardputer-ADV 当前参考样本 IMU 全零”
- 源码版本：[`m5agent/m5stack-esp-emulator`](https://github.com/m5agent/m5stack-esp-emulator)
  @ [`af4c6ea6`](https://github.com/m5agent/m5stack-esp-emulator/commit/af4c6ea6162f2c4480137dccc1060c39e71c1b1c)
- 环境：macOS arm64、隔离 Device Service `/api/v1`、QEMU ESP32-S3；
  物理硬件未使用

## 结论

当前 UIFlow2 `v2.5.3` Cardputer-ADV 参考固件已经通过板载 BMI270
`0x69` 数据面。guest 完成 CHIP_ID、软复位、INIT_DATA/INIT_CTRL 和
data-ready 路径，通过官方 `Imu.getAccel()` / `Imu.getGyro()` 读取
QOM 注入值；原样矩阵用例首轮通过并显示绿色 `PASS` frame。

当前主线不需要新增 QEMU 传感器修复。原 `66/67` 中 Cardputer-ADV
IMU 失败仍作为旧 runtime/commit 的历史结果保留，不回写成当时已通过。

## 关键证据

- Base firmware SHA256：
  `a3961c8eda7358771c8e06c9160648e87ada973d23c6f71c9939b76fa973bed9`
- Device Service composed firmware SHA256：
  `ea9fb400cdcb64f8020b4a43fca24c06f88097d7805b8dc2292185281d48c077`
- QEMU SHA256：
  `f0eb5f6c26f82ce99d6dad4006fcd0748991ba1a8d1ce780092d57d01d8e798e`
- 官方 API 回读 accel：`0.25 / -0.50 / 0.75 g`
- 官方 API 回读 gyro：
  `10.009766 / -20.019532 / 30.029296 dps`
- Frame：`240x135`、`5,519` nonblack pixels、`1,920` green pixels，
  SHA256 `a05b389509396e9c6d878b5f783a599c55a96074ef69f9418ca73338112d2b72`
- 定向矩阵：`cardputer-adv-imu` 首轮 `PASS`，`attempts=1`、
  `retry_used=false`、四项 checks 全通过
- 平台测试：`1398` 项 `OK`，`1` skip；
  runtime coverage、peripheral catalog、QEMU profiles 和 project snapshot
  均 PASS
- GitHub CI
  [`40726881242`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40726881242)
  的 `platform-contracts` 与 `network-namespace-policy` 均 PASS
- 主仓证据：
  [Cardputer-ADV IMU 闭环](https://github.com/m5agent/m5stack-esp-emulator/blob/af4c6ea6162f2c4480137dccc1060c39e71c1b1c/docs/evidence/2026-10-29-cardputer-adv-imu/README.md)

## 文件

- [report.md](report.md)：复现、证据、验收层级和边界
- [run.json](run.json)：机器可读结果
- [evidence/summary.json](evidence/summary.json)：脱敏摘要和哈希

## 未覆盖项

- 物理 IMU 精度、噪声、温漂、轴向装配、量程误差和电气测量；
- 其它固件 SHA、其它板型和外部物理传感器输入；
- 不把本次虚拟设备通过扩展为真机或任意 UIFlow2 固件兼容性。
