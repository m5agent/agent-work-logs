# ESP Emulator 本地服务发现与 bootloader Flash 契约报告

## 背景

- 来源：[PR #76](https://github.com/m5agent/m5stack-esp-emulator/pull/76)、
  [PR #77](https://github.com/m5agent/m5stack-esp-emulator/pull/77)
- 现象：
  1. 从本机启动 Device Service 后打开同源网页，页面仍提示设备需要“连接服务”。
  2. Cardputer-ADV 固件 job 以 application readiness 超时失败，串口同时反复报告
     4 MiB Flash 无法容纳位于 `0x340000`、大小 `0x330000` 的分区。
- 目标：确认浏览器部署是否破坏 Skill/API；修复本地同源连接；判断串口错误来自
  guest、QEMU 还是上传镜像，并让必然失败的导入提前、明确地失败。

## 结论

- Skill helper 使用的主要 `/api/v1` discover/upload/compose/create/status/observe/stop
  契约仍兼容；最新服务 OpenAPI 为 `1.51.0`，33 个 Skill/package 测试通过。
- 网页同源自动连接最初确实缺失；连接成功后设备行仍读取旧静态标签，是第二个 UI
  bug。最初用 loopback host 启发式修复后，正式 Pages 验收以
  `no-device-service-requests` 拒绝，因为普通静态服务器也可能位于 loopback。
  最终改为由 `serve.py` 动态声明真实服务 origin；静态导出仍为空。
- bootloader header 字节为 `0x2f`：低半字节 `0xf` 表示 80 MHz，高半字节 `0x2`
  表示 4 MiB。分区表要求到 `0x800000`，因此 guest bootloader 使用 4 MiB 上限是
  正确行为。将上传文件补齐到 8 MiB 不会改变镜像内 bootloader 的容量声明。
- Device Service 在 QEMU 启动前比较有效分区表末尾与 bootloader 声明容量，并新增
  `409 bootloader_flash_size_too_small`。

## 改动范围

- Device Service 在 `site-config.json` 中声明由已验证 Host header 派生的同源
  origin；静态导出不声明服务。
- 显式 `mode=browser` / `mode=model` 链接仍不建立服务连接。
- Device Service 目录连接后，设备行显示“服务可运行”。
- `analyze_esp_image` 输出 flash mode/speed/size code 和 declared size。
- merged、segmented、manifest、UIFlow composition 在 session 分配前验证
  partition-table end 与 bootloader declared flash size。
- 补充 Device Service、firmware analysis、网页入口、Skill workflow、OpenAPI
  描述、API inventory hash 和生成项目快照。

## 执行

环境：

- macOS arm64
- Python 3.12
- `pillow` 和 `littlefs-python` 测试依赖
- Chromium
- 项目锁定的 QEMU native runtime

关键命令：

```text
PYTHONPATH=platform/tools uv run --python 3.12 \
  --with pillow --with littlefs-python \
  python3 -m unittest discover -s platform/tests -p 'test_*.py'

node platform/tests/test_public_qemu_entry.mjs

python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
uv run --python 3.12 --with pillow \
  python3 platform/tools/project_snapshot.py --check
```

结果：

- 平台套件：`1729 tests`, `OK`, `1 skipped`
- Skill/package：`33 tests`, `OK`
- PR CI：`4/4 PASS`
- 正式本地 HTTP 页面：服务广告后自动连接，22 个可运行设备
- 原始 artifact compose：`409 bootloader_flash_size_too_small`
- 修正 bootloader header 的同一 artifact：composition `201`，session `running`

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python/Node 契约、PR CI 和静态站点相关测试通过 |
| transport | `PASS` | 同源浏览器通过 HTTP 读取 `/api/v1/devices` 与 Units |
| device_response | `PASS` | 原始 artifact 返回明确 409；修正镜像可创建 QEMU session |
| data_behavior | `PARTIAL` | serial 不再出现 partition-table 拒绝；应用业务行为未以本 artifact 重新验收 |
| visual_or_physical | `NOT RUN` | 未使用物理 Cardputer-ADV，不验证舵机、屏幕光学或机械行为 |

## 验证边界

原始 4 MiB bootloader 镜像本身无法在 8 MiB 设备上通过分区验证。修正实验只改变
bootloader size header 并重算镜像 hash，用于证明模拟器容量路径；它不是对用户最终
固件的修改。用户应重新生成完整 8 MiB build，使 bootloader、partition table 和
application 来自同一构建配置。

本记录不把 QEMU 结果写成物理硬件、RF、电气或机械结果。

## 风险与回滚

只有实际 Device Service 会通过动态 `site-config.json` 声明自身 origin，普通静态
站点和公开 Pages 都不会探测 `/api/v1`。若需回滚，可撤销 PR #76/#77 对应的 merge
commit；它们不修改 Flash、设备状态或外部用户数据。
