# Cardputer-ADV BMI270 当前参考固件闭环报告

## 背景

- 来源：`FW-03` 跨厂商回归 Backlog；
- 现象或需求：旧完整矩阵记录 Cardputer-ADV 当前参考固件的 IMU
  读数为全零，需要核对 guest 板型、器件地址、初始化路径和官方 API；
- 目标：在当前 runtime 上复现并判断是否需要修改板级模型或测试。

## 结论

- 状态：`PASS`；
- 关键判断：当前 QEMU 在 `0x69` 正确建模 BMI270，UIFlow2 guest
  能完成初始化并读取动态样本；没有发现需要新增代码修复的缺陷；
- 改动范围：只更新主仓当前状态、Backlog、验证台账和日期化 evidence；
  不修改 QEMU、外设 catalog、profile 或测试固件。

旧完整矩阵中的 Cardputer-ADV IMU FAIL 仍有效，因为它绑定旧
runtime/commit。本次结果只关闭当前参考固件在当前 runtime 上的待办。

## 证据

### 代码或配置

```text
device: cardputer-adv
machine: m5cardputeradv
I2C address: 0x69
components: tca8418 @0x34, bmi270 @0x69, es8311 @0x18
sensor properties: accel-x/y/z, gyro-x/y/z
```

### 执行

- 环境：macOS arm64、隔离 Device Service `/api/v1`、QEMU SHA256
  `f0eb5f6c26f82ce99d6dad4006fcd0748991ba1a8d1ce780092d57d01d8e798e`；
- 原样 source：`tests/uiflow2/cardputer_adv_peripherals/main.py`；
- Device Service 在 guest READY 后注入六个物理量；
- QEMU I2C trace 记录 CHIP_ID `0x24`、软复位、INIT burst、
  data-ready 和 `0x0C..0x17` 数据读取；
- 同一底固件另跑仓库定向矩阵，首轮无重试通过。

复现入口：

```bash
python3 platform/tools/serve.py <isolated-local-port> \
  --state-dir <ignored-state-dir> \
  --max-sessions 2 --max-per-device 2

PYTHONPATH=platform/tools:tests/uiflow2 \
  .work/issue-review-venv/bin/python3.12 \
  tests/uiflow2/api_sweep/run_hardware_guest.py \
  --api <isolated-local-service-origin> \
  --device cardputer-adv \
  --source tests/uiflow2/cardputer_adv_peripherals/main.py \
  --runtime-env-json <i2c-trace-runtime-env.json> \
  --drive-json <qom-injection-schedule.json> \
  --done-marker CARDPUTER_ADV_IMU_GYRO \
  --out-dir <new-ignored-output-dir>

PYTHONPATH=.work/py python3 \
  tests/uiflow2/run_peripheral_matrix.py \
  --case cardputer-adv-imu \
  --out-dir <new-temporary-output-dir>
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | 主仓 CI `40726881242` 两 job 成功；平台测试 `1398 OK / 1 skip` |
| transport | `PASS` | ESP32-S3 I2C controller 上的 `0x69` trace，含 ID/复位/INIT/data-ready/样本读取 |
| device_response | `PASS` | CHIP_ID `0x24`、软复位与 INIT 序列完成 |
| data_behavior | `PASS` | QOM 注入后官方 API 返回 `(0.25,-0.50,0.75 g)` 与约 `(10.01,-20.02,30.03 dps)` |
| visual_or_physical | `PASS`（仅虚拟 frame） | `240x135`、`5,519` nonblack、`1,920` green；物理验证 `NOT RUN` |

## 验证边界

本记录只证明 Cardputer-ADV 当前参考固件、当前 QEMU、板级 I2C 路由、
BMI270 寄存器模型、官方 `Imu` API、QOM 注入和可见 frame 的同一 guest
闭环。不能证明：

- 物理 IMU 的精度、噪声、温漂、轴向安装或量程误差；
- 电气、功耗、机械或真机时序；
- 其它固件 SHA、其它板型或外部物理传感器输入。

## 风险与回滚

本次没有修改 runtime 或固件，不存在需要回滚的数据面变更。文档更新可以
通过反向提交恢复；历史验证台账与旧失败证据不改写。
