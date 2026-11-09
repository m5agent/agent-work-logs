# PaperMono 客体绘图验收

新增 ET047TC1 分支时，PaperMono 专用的 EPD 模式调用使用了字面反斜杠与 `n`，其后紧接下一句。上传的 Python 在行尾产生了语法错误，原始客体的 raw-paste 会话提前结束。只将该字符对改为换行，保持模式、尺寸、帧、硬件复位及清理断言。

修复前两工作线程全站试验在 PaperMono 检查停止，27 例通过、1 例失败、44 例未运行。失败会话的六个 Worker 已实际回收。修复后通过精确 PaperMono 启动镜像、原显示 API 和浏览器 Canvas 走真实客体。检查原始 raw-paste、固件输出标记、PaperMono 480×800 黑白画面、复位后的新 console epoch 及 Chrome CDP 目标。物理硬件与其他固件不在该复测范围。

```sh
M5_PUBLIC_SITE=.work/public-site M5_PUBLIC_BASE_PATH=/m5stack-esp-emulator/ \
  M5_PUBLIC_QEMU_OUT=.work/papermono-editor-fixed M5_QEMU_DEVICE=papermono \
  node platform/tests/test_public_uiflow_guest.mjs
```
