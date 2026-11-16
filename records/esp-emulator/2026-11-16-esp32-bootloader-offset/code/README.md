# 复现入口

在记录所列源码版本启动独立 `platform/tools/serve.py` 实例，从授权缓存取得 issue 披露 SHA-256 对应的原版镜像和官方正对照，校验字节后用 `POST /api/v1/artifacts` 上传。给 `POST /api/v1/firmware` 提供 `device_id=stickc-plus2`、`kind=merged` 与 artifact SHA。`POST /api/v1/firmware/import` 使用同一设备和 artifact SHA。旧版用编排返回的固件标识调用 `POST /api/v1/firmware/analyze`，然后通过 `/api/v1/sessions` 以 `runtime=qemu` 观察串口并导出证据 ZIP。修复版用旧版生成的固件记录在独立测试状态下验证重新分析和会话拒绝，再用有效官方镜像验证启动。

审核调用端绑定 `2846fe9b4ee73d4b4dbb9afaf31f439d0b6c34f2`。用独立审核状态创建 `saved_snapshot` 任务，保存公开描述及 SHA 验证通过的原 BIN，无内容代理或提交选项。执行 `Reviewer.run`，核对 `E_STATIC`、两个偏移和虚拟设备会话数量。完整 Python 测试入口分别是 `python3 -m unittest discover -s platform/tests -p 'test_*.py'` 及 `python3 -m unittest discover -s tests`。
