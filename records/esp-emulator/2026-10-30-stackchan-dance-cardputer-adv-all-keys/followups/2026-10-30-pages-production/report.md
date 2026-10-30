# ESP Emulator StackChan / Cardputer Pages 发布报告

## 背景

- 用户要求立即合并 StackChan 跳舞 / Cardputer-ADV 全键修复并构建新网页。
- 初始修复位于 PR #65，head
  `6db2b817506fade96fde45e5984aa46b1c7876ed`。
- 正式发布要求从 `main` 源码构建 WASM、执行全公开板型浏览器门禁，再部署
  GitHub Pages。

## 发布与门禁时间线

1. PR #65 以 merge commit `c7cb7f29` 合并。
2. 首次发布 `41040407490` 在 StopWatch 的 engine target 30 秒清理窗口失败。
3. PR #66 将后置 target 关闭回执扩到 60 秒并合并为 `dcb012c4`。
4. 下一次运行在 Atoms3 暴露 `boardRun` 在 Node 作用域读取的测试错误；
   PR #68 改为通过 `page.evaluate` 读取并合并为 `59887375`。
5. Sticks3 又超过 60 秒，PR #67 将预算扩到 120 秒并合并为 `acf738bb`。
6. 进一步检查发现 timeout 只等到浏览器关闭：engine 已收到 closing 通知，
   但 owner 没有 finalize Worker handle。PR #69 在确认通知后执行一次正常
   `Worker.terminate()`，单独计数为 `engineNormalTerminations=1`，fallback
   保持 0，并以 merge commit `11e54805` 合并。
7. 当前 wrapper 的本机真实浏览器 StopWatch/Sticks3 均 PASS，target 在
   iframe 移除前关闭；StackChan 与 Cardputer 原完整 Flash 也重新通过。
8. regular hosted macOS 运行 `41056051554` 的 StopWatch PASS，但 Sticks3
   仍在 normal finalize 后残留 CDP target graph 条目，regular 发布保持失败。
9. 使用当前导出站走 prepared-site 流程：
   run `41058959787` prepare/deploy 均 PASS。
10. Web/API/coverage/snapshot 与部署证据通过 PR #70 合并到 `main`，
    merge commit `0f7f6fc635f91aef6215f08de01961e50fc5d1a7`，CI 2/2 jobs PASS。

## 部署产物

- release tag：`pages-preview-20261030-stackchan-dance`
- asset：`public-site-preview-live.tar.gz`
- bytes：`151909857`
- SHA256：
  `ad0607f01cac1b7d313b21a1cd339341156f36535bfc5cbca0e21e5206757026`
- manifest SHA256：
  `3c3cdb2f3ea71b458d48c9b6203282ee14bc205e9edad257cb955094c24a958b`

## 本机虚拟设备验证

- StopWatch：24/24 checks；engine normal termination 1、fallback 0；
  iframe 保留时所有 Worker target 已关闭。
- Sticks3：25/25 checks；相同清理结果。
- StackChan：11/11 checks；30 个 SCS 包、present/goal 三档 yaw/pitch，
  DOM/3D/标签同步。
- Cardputer-ADV：36/36 checks；56/56 物理键、55/55 direct PC code、
  modifiers、Escape/Delete/Fn arrows、四旋转。

## 线上回读

- 首页与完整 WASM HTTP 200。
- Pages Service Worker 生效后 `crossOriginIsolated=true`。
- 线上 manifest、`public-qemu-instance.js`、
  `cardputer-adv-keymap.js` 与本地导出逐字节 SHA256 一致。
- 线上 profile 精确包含 StackChan Flash
  `c854d3ac…04542` → `stackchan-wasm-dance-div6`。
- 真实 Chromium 可切换到 StackChan 并显示工作台。

## 验证边界

- 正式页面部署 `PASS`，但 regular all-admitted hosted macOS gate
  `NOT PASS`。
- 公网 CoreS3 guest 重测未执行：上游 M5Burner composer 返回 HTTP 503。
- 物理硬件、机械、舵机供电、键盘、LCD 光学和 RF 均未验证。
- 该次 prepared-site 部署不能被描述为完整生产发布 PASS。
