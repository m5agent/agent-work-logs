# ESP Emulator 运行时资产部署诊断报告

## 背景

- 来源：其他部署者反馈 clone 后找不到 `.work/`，认为仓库不完整。
- 现象：页面或部署流程可以启动，但无法创建虚拟设备会话。
- 目标：区分只读目录部署与 QEMU 运行时部署，给出可操作的根因信息。

## 结论

- 状态：`PASS`（部署服务路径和虚拟设备会话）；物理硬件 `NOT RUN`。
- 根因：`.work/` 是本地构建与运行时缓存，被 `.gitignore` 排除。仓库规模约
  20 MiB，而参考工作站运行时约 48 GiB；二者不是同一发布物。
- 关键判断：全新 clone 可提供目录和只读 API，但不能仅凭源码创建 QEMU
  lease。
- 改动范围：部署文档、README、Device API 字段、`backend_not_ready`
  错误详情、OpenAPI 和一个诊断回归测试。

## 证据

### 代码或配置

```text
bcbdc03 -> 7b973e4
README.md
docs/deployment.md
docs/device-service-api.md
docs/device-service.openapi.yaml
platform/tools/device_service.py
platform/tests/test_device_service.py
```

新增 API 字段 `missing_runtime_files`。当后端未就绪时，错误对象同时包含：

```json
{
  "code": "backend_not_ready",
  "missing": [".work/..."],
  "documentation": "docs/deployment.md"
}
```

### 执行

- 从 `7b973e4` 导出不含 `.work/` 的源码树并启动服务。
- 请求目录页与设备清单，确认静态路径可用。
- 对 `sticks3` 创建 lease，确认返回结构化 `503` 和缺失文件列表。
- 在已 provision 的参考环境创建同一设备 lease，等待状态进入 `running`，
  读取 PNG 帧，然后执行 `DELETE ...?purge=0`。
- 执行项目规定的 Python unittest、runtime coverage 和 peripheral catalog
  检查。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python 入口编译、OpenAPI YAML 解析和 Git whitespace 检查通过 |
| transport | `PASS` | 干净导出的静态 HTTP 与 Device Service API 均可访问 |
| device_response | `PASS` | 缺运行时返回结构化 `503`；已 provision 的 `sticks3` 进入 `running` |
| data_behavior | `PASS` | `backend_ready`、`missing_runtime_files` 与 `missing` 内容一致 |
| visual_or_physical | `NOT RUN` | 本次不是物理硬件或视觉保真度验证 |

自动检查：

- Python unittest：158 项通过。
- `runtime_coverage.py --check`：`RUNTIME_COVERAGE_OK`。
- `peripheral_catalog.py --check`：`PERIPHERAL_CATALOG_OK`。

## 验证边界

本次没有从零重建 48 GiB 运行时，也没有在 Linux/x86_64 上复测运行时包。
仓库目前仍没有一键 bootstrap；文档明确要求使用与 commit、OS 和 CPU 架构
匹配的受控 runtime image，或按固定上游源码和补丁序列重建。

QEMU 会话属于 virtual-device validation，不声称是物理硬件测量，也不覆盖
真实 RF、电气或机械行为。

## 风险与回滚

改动不会移动或删除本地 `.work/`，只增加诊断信息。API 仍保留原有
`backend_not_ready` 错误码与 HTTP `503`，新增字段对旧客户端向后兼容。
回滚可 revert `7b973e4`；已持久化的 stopped session 历史不受影响。
