# Core2 交互应用空白首帧就绪判定报告

## 背景

公开固件 `m5core2_voronoi v1.0.3` 在 Core2 自动审核中返回
`HTTP 408 ready_timeout: application did not satisfy the requested readiness conditions`，
但串口没有 panic、watchdog 或 backtrace，QEMU 仍持续运行。

用户要求实际运行同一固件，区分固件缺陷、设备模型缺陷和审核就绪逻辑缺陷。

## 根因

该固件启动时创建一个全黑 canvas。`DrawTask` 在点列表为空时直接返回，只有触摸结束事件
才会调用 `addPoint()` 并首次提交 Voronoi 画面。因此“输入前黑屏”是应用设计行为，
不是启动失败。

自动矩阵已经让 Device Service 解码 framebuffer 并返回 `nonblack_pixels`，但调用方仍要求
`frame_min_bytes=1024`。Voronoi 最终画面只有两种颜色，`320x240` PNG 的压缩结果仅
`602-615` 字节；虽然 `76,800/76,800` 像素均非黑，仍被文件大小门槛误判。

## 修复

1. `platform/tools/user_firmware_matrix.py` 保持
   `frame_min_nonblack_pixels=16`，把 `frame_min_bytes` 从 `1024` 降为 `1`。
2. 审核控制面在无应用 marker 的 screenshot/input 设备上把输入前观察窗缩短到 `12 s`。
3. 输入前黑屏但 session 正常运行时，先在同一 session 注入设备声明的输入。
4. 输入后再调用像素级 readiness；只有输入被接受且 frame 变为非黑，才记录
   `input_unlocked_frame=true`。
5. 报告同时保留 `initial_ready=false` 和 `ready_after_execution=true`，不修改原始
   wait timeout 证据。

## 执行

### 固件与运行环境

```text
firmware: m5core2_voronoi v1.0.3
sha256:   fb69fa3c7d97ef3db8175de426f3d262be83cc89a7b921fb13bec4e74cf93546
size:     16,777,216 bytes
device:   Core2 / ESP32-D0WDQ6-V3
runtime:  QEMU m5core2
display:  320x240 ILI9342 virtual panel
session:  2c6291d2358c4dcdbd9563ef432d58ad
```

### 直接复现

固定 QEMU 参数运行同一镜像，前 `12 s` 观察到：

```text
session state: running
serial: bootloader + "auto detect board:2"
frame: valid PNG
nonblack pixels: 0
```

在 `(160,120)` 执行一次触摸后，Device Service 接受输入并提交非黑 canvas。

### 自动审核复测

修复后的同一 session 执行两次输入：

| 输入 | 接受 | frame changed | before SHA-256 | after SHA-256 |
| --- | --- | --- | --- | --- |
| center touch | yes | yes | `57580743…` | `94d84a52…` |
| left drag | yes | yes | `94d84a52…` | `a52cbcac…` |

最终帧指标：

```text
width: 320
height: 240
PNG bytes: 615
nonblack pixels: 76800 / 76800
unique colors: 2
```

审核终态：

```text
status: done
lane: SIM_VERIFIED
initial_ready: false
input_unlocked_frame: true
input accepted/changed: 2/2
duration: 21,727 ms
```

### 测试

```bash
PYTHONPATH=platform/tools:. python3 -m unittest discover \
  -s platform/tests -p 'test_user_firmware_matrix.py'
```

结果：`28/28 PASS`。

PR #78 head `4/4` checks 通过；普通 merge 为 `b6b8d6fe`，合并后 main CI
`41385483902` 的 `platform-contracts` 与 `network-namespace-policy` 均成功。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | 固件静态分析有效；矩阵 Python 编译与 `28/28` 测试通过 |
| flash | `PASS` | Core2 QEMU 加载精确 16 MiB 镜像，flash SHA 匹配 |
| transport | `PASS` | 串口启动日志、QMP framebuffer、触摸/拖动输入链路正常 |
| device_response | `PASS` | 两次输入均被 Device Service 接受，frame SHA 均变化 |
| data_behavior | `PASS` | 输入前 0 非黑像素，输入后 76,800 个非黑像素 |
| visual_or_physical | `PASS`（virtual） | 320x240 PNG 可解码，最终双色画面全屏非黑 |
| delivery | `PASS` | PR #78 合并为 `b6b8d6fe`；head `4/4` 与 merge main CI 两 job 通过 |
| physical hardware | `NOT RUN` | 未使用物理 Core2 |

## 验证边界

- 这是 virtual-device validation，不是物理 LCD、触摸、电源或电气测量。
- 结论绑定上述固件 SHA、Core2 板型和当前 QEMU framebuffer/input 路径。
- 恶意软件/木马检测为 `NOT RUN`；静态字符串扫描仅为 `REVIEW`。

## 风险与回滚

- 最小修复只影响 readiness 的 PNG 文件大小门槛；实际非黑像素数仍由 Device Service
  解码验证，不能由客户端伪造文件大小通过。
- 若需回滚，可回退 PR #78 的一行改动；审核控制面的交互解锁逻辑也可独立回退。
