# ESP Emulator SVC-03 network parsing boundary 报告

## 背景

`SVC-03` 的目标是降低 `device_service.py` 的单体规模，同时保持 Device
Service 的 HTTP、session、runtime 和 evidence 契约不变。

本次处理的无状态解析包括：

- `parse_network_policy`
- `parse_dns_cname_records`

原实现和请求编排、session class、runtime adapter 位于同一大型模块中。

## 结论

- 状态：`PASS`
- 根因或关键判断：这两个 parser 只依赖错误类型、network policy 和
  CNAME binding 校验，不需要 Device Service 状态，可以安全独立。
- 改动范围：新增 `device_service_network.py`；
  `device_service.py` 保留 same-object re-export 并删除重复定义。

Base commit：
`b438d7325ee8f12fd9ccef5ff39500f2d89c8126`

Source commit：
`16c92b04436b354f8162ae26f16242cc85d54878`

## 证据

### 代码或配置

新增模块定义两个 parser。原模块使用：

```python
from device_service_network import (
    parse_dns_cname_records,
    parse_network_policy,
)
```

因此现有 `device_service.parse_network_policy` 和
`device_service.parse_dns_cname_records` 指向同一函数对象。

### 执行

环境为 macOS arm64、Python 3.12，使用仓库锁定虚拟环境。

```bash
PYTHONPATH=platform/tools .work/py312/bin/python \
  platform/tests/test_device_service_network.py

PYTHONPATH=platform/tools .work/py312/bin/python \
  platform/tests/test_device_service_parsing.py

PYTHONPATH=platform/tools .work/py312/bin/python \
  -m unittest discover -s platform/tests -p 'test_*.py'

PYTHONPATH=platform/tools .work/py312/bin/python \
  platform/tools/project_snapshot.py --check
```

network policy、CNAME binding、错误码和 re-export identity 的定向测试均通过。
完整平台回归为 `1,589` 项，`1,588 PASS + 1 skip`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall 与 targeted module import 通过 |
| transport | `NOT RUN` | 本次未启动 QEMU 或网络 namespace 数据面 |
| device_response | `NOT RUN` | 这是无状态代码边界改动 |
| data_behavior | `PASS` | policy、CNAME、错误码和 symbol identity 契约测试通过 |
| visual_or_physical | `NOT RUN` | 没有显示或物理硬件路径变化 |

补充检查：

- runtime coverage：`PASS`
- peripheral catalog：`PASS`
- QEMU profiles：`PASS`
- project snapshot：`PASS`
- `git diff --check`：`PASS`

## 验证边界

本轮没有执行 QEMU 功能会话，也没有用物理硬件、RF 或电气测量验证。原因是
改动只移动无状态函数并保留对象身份，不修改 runtime 数据面。平台全量测试
覆盖现有 HTTP/network/session/service 契约，但不能替代后续 runtime lane
或物理验证。

## 风险与回滚

风险集中在模块导入路径或 re-export 身份变化。对应测试已显式锁定。
回滚方式是撤销 source commit，把两个函数及其依赖恢复到
`device_service.py`；没有数据迁移、不可逆操作或设备状态变更。
