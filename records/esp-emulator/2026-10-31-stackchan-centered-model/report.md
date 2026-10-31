# StackChan 居中显示模型同步报告

## 背景

用户指出 `https://github.com/yuyun2000/m5stack-models` 刚更新了 StackChan 模型，
要求同步到模拟器。模拟器此前固定该公开模型仓库的
`4879ab51eb8bb11ce024e670ae6880529e3d0f42`，新 upstream `main` 为
`1373680d29667f99438a5412b87b955a3ba7702f`。

上游区间包含三个提交，但只有最后一个是运行时模型变更：

1. `849382d`：GitHub Pages demo/workflow；
2. `2bea455`：Pages 发布文档；
3. `1373680`：把 StackChan 方形头部内的 LCD 居中。

同步脚本继续保留独立的文档 pin `3681a648`，没有把 upstream 新增 artifact、计划文档和
demo 文件带入 vendor runtime。

## 改动

1. 将 `sync_visual_models.py` 的 runtime pin 更新到 `1373680d`。
2. 重新生成 `UPSTREAM.md`、`vendor-manifest.json` 和三个 runtime JS：
   - `src/devices/cores3/CoreS3.js`
   - `src/devices/stackchan/dimensions.js`
   - `src/devices/stackchan/index.js`
3. 更新厂商 pin 契约测试、当前项目状态和生成的 `docs/project-snapshot.md`。

同步后的闭包为 `1,925` 个文件，加一个固定 Three addon。diff 只包含上述受控 vendor
文件和显式 pin/文档更新，没有上游截图或 demo 文件。

## 执行与验证

### 同步和契约

```text
python3 platform/tools/sync_visual_models.py \
  --source <public-model-repo> \
  --commit 1373680d29667f99438a5412b87b955a3ba7702f --check
```

结果：`visual snapshot OK`，`1,925` files 和 pinned Three addon。

- `node platform/tests/test_model_shell.mjs --case controller:stackchan`：PASS
- `node platform/tests/test_model_shell.mjs --case controller:cores3`：PASS
- `npm run --prefix platform/tests test:contracts`：PASS
- Python platform suite：`1,725` tests，`OK (skipped=10)`
- QEMU profile、peripheral catalog、runtime coverage、project snapshot：PASS
- PR #74 head CI 与 CI replay：两 job PASS

### 同固件 browser-QEMU

固定输入：

- firmware：`c854d3ac6b958439ad30c5277266575d8765f228febf75de243da5d011904542`
- WASM：`5d6c36bdafc1129c2652b5ba9422f3deb5ab170475748cea96fdc4cf9520a993`
- export manifest：`ec8a24d80aca1731079c34fa2d796699ae30d3bd5f7508aa6c10c4dd70bbe279`

使用导出站中的真实 `/api/v1` browser-QEMU 会话路径运行完整 StackChan 舞蹈固件，
结果为 `12/12 PASS`：

- yaw `present_position` 范围 `307..597`；
- pitch `present_position` 范围 `677..850`；
- 30 个有效 SCS packet，无拒绝或断连；
- 观察到 23 个原始状态和 577 个显示帧；
- 角度标签、DOM ticks 与原始快照一致；
- 正常 Stop 后 iframe 与 Worker target 清理完成；
- 页面错误、运行时错误和受保护服务请求均为 0。

### 正式 Pages

公开地址：<https://m5agent.github.io/m5stack-esp-emulator/>

- release：`pages-preview-20261031-stackchan-centered`
- prepared-site workflow：`41163764773`，prepare/deploy PASS
- asset：`151915326` bytes，
  SHA256 `21e8049378f9bbb46ca5f4eef5b53a0e6302c7a17e9a026827e81e2c5580eb66`
- 线上 manifest SHA256：`ec8a24d80aca1731079c34fa2d796699ae30d3bd5f7508aa6c10c4dd70bbe279`
- 线上 vendor manifest SHA256：`8e01db08ca3fff7c732b3b78417323c998ae1763f46f1284c532e25100fff776`
- 线上 WASM SHA256：`5d6c36bdafc1129c2652b5ba9422f3deb5ab170475748cea96fdc4cf9520a993`

从正式 HTTPS 加载模型后，`crossOriginIsolated=true`、JavaScript errors 为 0。
StackChan LCD 的本地位置是 `[0, 0, 7.81]`，世界位置是
`[0, 8.25, 30.81]`，与内部 CoreS3 的 `corePosition.y=8.25` 和居中 `lcdCenterY=0`
一致。

## 验证层级

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | vendor 同步检查、Python/Node 契约和生成器 |
| transport | `PASS` | 同一 guest 的 SCS UART/QOM 输出与 30 个有效 packet |
| device_response | `PASS` | 固件实际 yaw/pitch 目标与 present position 变化 |
| data_behavior | `PASS` | 23 个状态、DOM ticks、角度标签及帧身份一致 |
| visual_or_physical | `PASS`（virtual） | 577 帧、3D 中间姿态、线上模型位置与截图 |
| physical hardware | `NOT RUN` | 未使用物理 StackChan |

## 风险和回滚

- 本次只更新公开 vendor 模型 pin 和对应契约，不修改固件执行后端。
- 若线上视觉需要回退，可重新部署上一 release
  `pages-preview-20261031-stackchan-smoothing`。
- 物理屏幕装配、视角和光学表现仍需真机补测。
