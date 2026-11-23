# m5stack/m5stack-linux-dtoverlays #18：CardputerZero 看不到 2.4 GHz 12/13 信道

- 日期：`2026-11-23`
- 结果：`PARTIAL`（驱动失败路径与 DT 补丁已做代码级/主机级验证；真机和虚拟设备运行未复现）
- 工作类型：`issue_triage`
- 条目：[m5stack/m5stack-linux-dtoverlays#18](https://github.com/m5stack/m5stack-linux-dtoverlays/issues/18)
  「CardputerZero: Wi-Fi never sees networks on 2.4 GHz channels 12 and 13 (the firmware
  stays on country US)」，作者 cjct-dev，英文，OPEN，0 条评论，无关联 PR
- 源码：`main` `a3fd3e83c0247e16e194e7e40f7fc1f5be933dd4`；工作树干净
- 环境：macOS arm64；无 CardputerZero 实机；本地 Device Service 的 `cardputer-zero`
  profile 是 Linux ARM64 后端且不可创建（`missing_runtime_files` 为
  `__missing_qemu__` / `__missing_rom__`）；无 Linux ARM64 内核/QEMU 环境可跑
  `brcmfmac` + CYW43439 固件国家逻辑
- 已发布回复：<https://github.com/m5stack/m5stack-linux-dtoverlays/issues/18#issuecomment-7106894286>（1 条，英文；issue 仍 OPEN，未 close、未改上游代码）
- 证据等级：**code-level verification**（Raspberry Pi 6.18.y 驱动与 binding）+
  **host-level device-tree check**（补丁可编译并应用到 CM0 基础 DTB）；信道 12/13
  的实际扫描/连接结果来自报告者的 **hardware validation**，本记录未独立复跑

## 结论

报告者的根因判断与 Raspberry Pi 6.18.y 的 `brcmfmac` 代码一致，`brcm,ccode-map-trivial`
是正确且最小的 DT 修复，没有阻塞问题。

1. CYW43439（chip id 43439）不在驱动的 ISO3166 回退列表中
   （`brmcf_use_iso3166_ccode_fallback()`，rpi-6.18.y `cfg80211.c:8266-8280`）。
   CM0 基础 DTB 没有 `brcm,ccode-map`，因此 `brcmf_translate_country_code()`
   （`:8282`）打印 `No country codes configured for device`（`:8308`）并返回
   `-EINVAL`。
2. `brcmf_cfg80211_reg_notifier()` 在 `:8606-8608` 收到失败后直接返回，`:8610` 的
   `country` iovar 从未写入。报告者观察到固件因此保持默认国家（US，只允许 1–11 信道），
   所以扫描看不到 12/13；`iw reg set GB` 只改变内核/cfg80211 侧的监管域，不能替代
   写给固件的 country 设置。
3. `brcm,ccode-map-trivial` 只在节点 compatible 含 `brcm,bcm4329-fmac` 时读取
   （`of.c:124-127`），且仅在缺少 `brcm,ccode-map` 时生效（`of.c:26-32`）。打开后
   `:8298-8305` 会把 ISO 国家码同时写入 `country_abbrev` 和 `ccode`、revision 为 0，
   驱动随后会继续写 `country` iovar。CM0 的 `wifi@1` 节点正好具备该 compatible。
4. 仓库里没有 `cardputerzero-overlay` 的独立源文件；`dtoverlay=cardputerzero-overlay`
   由 `firmware/CardputerZero/config.txt:58` 加载，模块侧源文件是 v3 / v5 两个
   `-overlay.dts`。把片段作为 `fragment@7` 追加到两者即可（补丁见
   `patches/0001-cardputerzero-ccode-map-trivial.patch`）。
5. 若 stock image 使用仓库内预编译的
   `firmware/CardputerZero/overlays/cardputerzero-overlay.dtbo`，该文件当前没有
   `mmcnr` fragment，也没有 `brcm,ccode-map-trivial`；只改 `.dts` 不会更新它，
   需要一并重生成。

## 关键证据

- `evidence/issue-18.json`：issue 状态、作者、0 评论、完整正文（英文原文）。
- `evidence/kernel-ccode-path.txt`：rpi-6.18.y `d4addd1` 的 `of.c`、`cfg80211.c`、
  `common.c`、`sdio.c`、`sdio_bus.c`、MMC `core.c`、`firmware.c` 与 binding 原文，
  保留行号。
- `evidence/overlay-dt-check.txt`：CM0 基础 DTB 的 `wifi@1` 路径、内核 DT 源文件、
  v3/v5 行号、预编译 dtbo 检查、补丁编译 + `fdtoverlay` 应用结果、SHA256。
- `evidence/device-service-profile.json`：本机 `cardputer-zero` profile 的
  `supported=false` / `creatable=false` / `backend_ready=false`、缺少 QEMU/ROM，
  以及 `device_service_specs.py` 的排除原因。
- `patches/0001-cardputerzero-ccode-map-trivial.patch`：对 base `a3fd3e8` 的
  +7/-0 ×2 补丁，`git apply --check` 通过。

## 未覆盖项

- hardware validation：`NOT RUN`。没有 CardputerZero；报告者的 GB 测试是唯一运行时证据。
- virtual-device validation：`NOT RUN`。`cardputer-zero` profile 明确不可创建，
  后端是 Linux ARM64 且缺 QEMU/ROM；ESP32 模拟器无法运行 `brcmfmac`、CYW43439
  固件或 NVRAM/CLM 国家逻辑。
- 端到端国家设置：`NOT RUN`。未在真机上执行 `raspi-config` / `iw reg set` 后扫描
  12/13，也未验证重启/挂起恢复后的持久性。
- 其他国家码：`NOT RUN`。trivial map 固定 revision 0；GB 已由报告者验证，其他
  ISO 码是否被具体 CLM 接受未覆盖。
- 预编译 dtbo 重生成：`NOT RUN`。本记录只给出补丁与重生成要求，未向上游提交构建产物。

## 文件

- `README.md`：快速结论与导航
- `report.md`：完整根因、驱动链路、补丁位置、验证与边界
- `run.json`：机器可读记录
- `evidence/`：issue、内核源码、DT/overlay、Device Service 证据
- `patches/0001-cardputerzero-ccode-map-trivial.patch`：建议补丁（base `a3fd3e8`）
