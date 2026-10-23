# ESP Emulator Two-Guest Lab Fabric 报告

## 背景

项目已完成单 guest WiFi、DHCP、DNS/HTTP、pcap、错误密码、radio/AP
丢失恢复和 DHCP renewal，但缺少两台 guest 在同一私有 L2 fabric 内互相
通信、同时禁止宿主/公网访问的可执行证据。原项目状态和 Backlog 仍把该
能力写成待办，与当前工作树不一致。

目标是同时完成：

- 两台真实 QEMU StickS3 guest 的 DHCP 和 guest TCP 请求/响应；
- 两侧 pcap 同时包含双向流量；
- guest 无法访问宿主控制面、公网 IPv4 或 metadata；
- namespace、helper socket 和虚拟网卡在结束后清理；
- 共享 WLAN 模型修改后重跑完整 UIFlow2 外设矩阵；
- 将当前事实、代码地图、工作流和 Backlog 收敛到同一基线。

## 结论

状态：`PASS`（virtual-device）。

关键判断：

- 多 guest 共用一个 WLAN 模型时，必须把显式 NIC MAC 保持到 association
  和 DHCP 生命周期，不能在状态切换时覆盖为固定地址；
- QEMU host ingress 在 association→DHCP 过渡和 802.11 注入队列忙碌时
  需要被接受或暂存，并在队列释放后 flush；
- test switch 不能按 TCP 建连顺序把连接槽位等同于 guest endpoint，必须用
  以太网源 MAC 绑定配置 endpoint；
- 尚未识别的目标 endpoint 必须有 bounded pending queue，不能丢弃首帧；
- 文档中的“最新矩阵”必须绑定具体 QEMU patch、时间和 evidence，不能继续
  引用旧 patch 的 `67/67` 结果。

## 改动范围

- 新增 `platform/tools/network_fabric.py`：
  private namespace、socket L2 switch、DHCP reservation、MAC 绑定、
  bounded pending queue、TAP/bridge primitive 和清理；
- 新增 `tests/network/lab_fabric/`：
  guest A client、guest B server、QEMU fixture、TAP/bridge primitive、
  isolation probe、pcap summary 和脱敏 evidence；
- 新增 QEMU patch
  `patches/qemu-m5stack-peripherals/0028-esp32-wifi-dual-guest-fabric.patch`：
  explicit MAC、DHCP ingress 和 delayed ingress flush；
- CI 增加 namespace bridge/TAP primitive；
- Cardputer-ADV 键盘矩阵等待从 6/1 秒加固到 10/2 秒；
- 更新 README、项目状态、工作流、代码地图、网络方案、Backlog 和文档
  一致性测试。

## 执行环境

- macOS Apple Silicon host；
- Linux fixture container，具备 network/namespace 权限；
- QEMU build：local Linux `qemu-system-xtensa`，SHA256
  `16c6d6185781b7ddfaa3e646adcd3dea2ecd851b319dd35ce502496432a95fb5`；
- guest firmware A SHA256
  `6e44f5f70ac31beaf85aae37d88184f2392f88d4bde7ef2d2ed208f7fb91a5c2`；
- guest firmware B SHA256
  `e9aa38793d9e71dddf6760629e9c7b2eacc3a23499c65d1a27c82dc4d6ab36ab`；
- Ubuntu GitHub Actions `40036279511`。

关键命令：

```text
python3 tests/network/lab_fabric/run_test.py \
  --qemu <qemu> --rom-dir <pc-bios> \
  --image-a <guest-a> --image-b <guest-b> --out-dir <output>

PYTHONPATH=.work/py python3 tests/uiflow2/run_peripheral_matrix.py \
  --out-dir <matrix-output>

PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | Python compileall、平台测试和 CI 全绿 |
| transport | PASS | 两台 guest 完成 DHCP；A→B TCP 请求/响应 |
| device_response | PASS | guest B 返回预期 ACK payload |
| data_behavior | PASS | 双侧 pcap 均含双向 TCP payload hash；MAC 绑定不依赖连接顺序 |
| isolation | PASS | 宿主控制面、公网 IPv4、metadata、默认路由不可达 |
| cleanup | PASS | namespace、helper socket 和虚拟网卡清理 |
| full regression | PASS | `67/67` case、`274/274` check、零 retry |
| delivery | PASS | 源码 commit、CI 和公开记录 |
| visual_or_physical | NOT RUN | 未做真机、RF、功耗或安全模式验证 |

首轮矩阵暴露 Cardputer-ADV 键盘在 6 秒窗口内未更新帧，结果 `66 PASS /
1 FAIL`。定向复现确认帧仍为 `keys: 0`；将启动等待改为 10 秒、输入端等待
改为 2 秒后，定向用例 PASS，随后最终矩阵以单次 attempt 完成 `67/67`。

## 验证边界

- QEMU socket switch 是 test fixture；guest 使用真实 NIC 和自身 TCP/IP
  栈，但这不是物理交换机、RF 或 WPA2/WPA3；
- TAP/bridge + DHCP helper 在 CI 中单独执行，不是本次双 guest QEMU PASS
  的运行路径；
- 当前 fixture 不属于生产 worker，不包含注册、心跳、drain、re-attach、
  多机调度或对象存储；
- 不是恶意固件沙箱，不证明文件系统、资源或租户隔离；
- 物理硬件、外部 IPv6 和 bit-exact Bluetooth controller 仍为 `NOT RUN`。

## 风险与回滚

fixture 创建和删除临时 network namespace/TAP，不修改宿主长期网络配置。
清理失败会保留 namespace 名称供诊断，不会自动访问外部网络。

回滚源码提交 `8e37781326e337d1d479b3dd432099f4734e8c16` 会移除双 guest
fixture、patch `0028`、CI primitive 和本次文档收敛；不会删除已保存的外部
日志或固件缓存。
