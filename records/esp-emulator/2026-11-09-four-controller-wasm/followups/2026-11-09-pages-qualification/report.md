# 资格验收与故障复现

## Worker 清理

同一 23 板静态导出上的全站并发验收记录了 AtomS3 Lite 的两次失败。第一次在按键用例中发生，第二次在编辑器硬复位回合结束后发生。两次均收到 QMP 退出码 0。五个内层 pthread 退出后，Chrome 的独立目标列表仍保留引擎 Worker。第二次在真实 iframe 保持连接时核对内层目标，移除 iframe 后连续等了 120 秒及独立的 30 秒故障取证窗口。仍无法确定该目标当时的 V8 上下文是否能执行。对照用例不复现残留，未把 iframe 存活顺序写成已定位的根因。

主页面拥有引擎 Worker 的浏览器生命周期，私有端口协议和单次正常回收仍由会话 iframe 管理。新方案在正式配置下复验了原版 CoreMatrix 以及 AtomS3 Lite 两次真实按键。全站并发复现保持为独立失败记录。原始报告和本机路径留在本地，发布摘要仅保留可复查的版本、哈希、场景和结果。

## 下载

两次 GitHub Actions 构建失败均发生于 Emscripten 版本检查后，原始任务仅报告 HTTP 504。本机相同 Python 下载逻辑对 libffi 官方发布直链连续三次返回 504。通过 libffi 官方仓库的 GitHub Release Asset API 读取，文件长度 1,393,979 字节，SHA-256 为 `138607dee268bdecf374adf9144c00e839e38541f75f24a1fcf18b78fda48b2d`。同一方法对 PCRE2 及其 WrapDB 补丁也通过。下列是三个 API 资产，两个目标仍各自使用原始锁文件校验内容。

- [libffi 3.4.7](https://api.github.com/repos/libffi/libffi/releases/assets/227440472)
- [PCRE2 10.44](https://api.github.com/repos/PCRE2Project/pcre2/releases/assets/172496647)
- [PCRE2 WrapDB 补丁](https://api.github.com/repos/mesonbuild/wrapdb/releases/assets/192615396)

Python 获取器对 408、429 和暂态网关响应执行有界重试。一个真实回环 HTTP 服务先返回 504、再返回 200，验证了同 URL 重试、字节校验、原子保存和暂存清除。错误内容哈希仍会立即拒绝。资格流程继续从源码构建，并用实际浏览器客体门禁决定是否部署。
