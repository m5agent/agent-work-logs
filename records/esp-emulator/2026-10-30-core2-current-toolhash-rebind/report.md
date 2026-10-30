# Core2 current tool-hash rebind report

## 背景

- 来源：`CORE2-02` Core2 并发与长稳回归。
- 现象或需求：SVC-03 将多个 parser 从 `device_service.py` 移到独立模块。
  虽然测试证明这些移动无语义变化，但 runner 会绑定
  `device_service.py` 的工具哈希，因此旧 PASS 不能直接代表最新 main。
- 目标：在最新 main 上重跑受影响的零错峰双实例回归，并保持固件、ELF、
  QEMU、runner 和 service 哈希可追溯。

## 结论

- 状态：`PASS`（限定的 virtual-device validation）。
- 根因或关键判断：当前差异是工具产物身份变化；需要在相同 QEMU/guest
  路径上重新绑定，不应通过改写旧 evidence 或忽略哈希变化继承 PASS。
- 改动范围：没有修改运行时实现；只更新源码 evidence、当前状态、
  Backlog、验证台账和生成快照。
- 交付：PR #62 四项 CI PASS 后合入 `674665ea`。

## 证据

### 代码或配置

```text
validation target: 3fc436e4aa99176ef3a4f7a2d35d25c973659219
delivery base: 867ce788b3b42e0b9c55429cd9272781ffd15cb0
configuration:
  runtime=qemu-unified
  profile=core2-native-hci
  concurrency=2
  stagger=0
  hold=60s
  require_psram=true
  tcg,thread=single,tb-size=128
  icount shift=5,align=off,sleep=off
```

工具哈希：

```text
previous device_service.py:
5b4ed0f576dae7a23151049f753acdfd6bf1ddce2d44e3c3389413b2b6349acb

current device_service.py:
a96b15061d104aa79e7af74b513e5881481acf62a847d5ba1e27c5997aa1bbbb

runner:
a9d1f678f2509e794bb4d98e4e4bd5540531df512adec8479543ca73be1da013

qemu_accel:
6ae04d310fd68c99e6200813689af4fbcb75d0a890c8e5882027a16ea35d1dc9
```

### 执行

- 环境：macOS arm64；Python 3.12；Device Service `/api/v1`；
  QEMU virtual Core2。
- 命令形态：`run_service_5x.py --attempts 2 --concurrency 2
  --stagger-seconds 0 --hold-seconds 60 --require-psram`，两个独立
  output directory 分别运行。
- 输入冻结：`before_first_lease`。
- 输入漂移：无；两批运行期间相同 firmware/ELF/QEMU/tool values。
- 结果：

| Batch | Leases | Result | Raw evidence SHA256 |
| --- | ---: | --- | --- |
| A | 2 | `2/2 PASS` | `c0e4ad6d7fe3c4d07c922c0cb7df2072baaf058fa774f00dd72f4e213bed935a` |
| B | 2 | `2/2 PASS` | `4409b748203c6ab4ddcc1c2b70c639fce7c8f7c85047f6ad58a8bbf0b8813dce` |

四个 lease 的公共结果：

- maximum concurrent sessions：`2`；
- PSRAM：每 lease 三次连续 1 MiB sweep/readback；
- network：每 lease 两次 controlled HTTP 和两次 public recheck；
- QOM：32 nodes、effective PSRAM `8 MiB`；
- HLI：`45/45` posts/consumed，36 events、9 ACLs；
- frame：非空 PNG；独立运行 frame hash 可不同，frame 存在性 gate PASS；
- evidence：pcap、manifest、serial、frames、logs、network、QOM 和 ZIP；
- panic、GATT timeout、drops、HLI error、prealloc failure、cleanup error：
  全部为 `0`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Current service starts; platform suite 1,680 with 1 skip |
| transport | `PASS` | WiFi DHCP/HTTP, public DNS/HTTP and external NUS GATT |
| device_response | `PASS` | 8 MiB PSRAM QOM and three 1 MiB guest readback sweeps |
| data_behavior | `PASS` | 4/4 independent leases with no HLI/panic/GATT/cleanup failure |
| visual_or_physical | `NOT RUN` | Nonempty PNG exists; physical display and hardware were not tested |

## 验证边界

- 该记录只重绑当前工具哈希下的双实例回归。
- 八实例 cold-start 在当前宿主负载下没有重跑，因此为 `NOT RUN`；
  不能把 `4/4` 外推为八实例 PASS。
- 九实例容量保持拒绝；历史 panic 与后续 ACK 竞态修复仍独立。
- 所有结果均来自 QEMU 虚拟设备。
- 物理 PSRAM/cache timing、bit-exact controller/baseband、RF、电气和
  真机均未验证。

## 风险与回滚

没有修改运行时行为，回滚仅需撤销源码 evidence 与文档更新。默认容量仍为
8。本任务没有设备烧录、擦除、写入或其它不可逆硬件操作。
