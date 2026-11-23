# AIFlow #6「Run Always」资源同步路径重复

## 1. 问题与现象

提问者在 StickS3 上点击 AIFlow 的 `Run Always`，随后每次启动都在资源同步阶段失败：

```text
[INFO] Resource sync: files=2 total=4130 bytes
[INFO] File unchanged: main_ota_temp.py size=2065 bytes
[INFO] Downloading file: apps/My_Project_1795168094430.py/My_Project_1795168094430.py size=2065 bytes
[WARN] Download error: apps/My_Project_1795168094430.py/My_Project_1795168094430.py [Errno 2] ENOENT
[INFO] Failed to download file: apps/My_Project_1795168094430.py/My_Project_1795168094430.py
```

设备画面停在 `Failed 50%`。提问者已经指出路径重复：

`apps/My_Project_1795168094430.py/My_Project_1795168094430.py`

目标条目：https://github.com/m5stack/AIFlow/issues/6

## 2. 复现环境

| 项 | 值 |
| --- | --- |
| 主机 | macOS，本机 Device Service（QEMU 后端） |
| 虚拟设备 | `sticks3`（`simulated`，135x240 显示） |
| 固件入口 | AIFlow 仓库 `resources/firmware/aiflow-sticks3.bin`，8,384,512 字节 |
| 固件 artifact SHA256 | `7ebc5d87e04182bcf1c3875b8cbff923e97738dec401b4983e52b2054e8d7b6a` |
| 归一化存储 SHA256 | `d612b47941c3c2ac4a5e6bc5b2e07b4a147270f0813d6a5bd536167bc4a03366` |
| 会话固件（叠加 UART REPL bootstrap） | `9cf3c84c5959a982973ca011ace9c9c6592dad693219ed01e7f2790df156d0c8` |
| 来宾 | `MicroPython v1.27.0-dirty on 2026-07-22; M5STACK StickS3` |
| 会话 | `c32706f184e34452a7fe10ccc3c3c91e` |

说明：本机固件包内 `aiflow-sticks3.bin` 的构建日期是 2026-07-22，提问者日志是 2026-11-17 的固件。
两者 `m5sync` 日志文案不同，但 `devicePath` 使用方式和 `m5things` 拼接实现一致，因此用该固件验证
“重复路径 → ENOENT → Failed”链路。

## 3. 复现方法

在 StickS3 来宾 REPL 中运行 `code/repro_sync_path.py`。脚本做两件事：

1. 在 `/flash/main_ota_temp.py` 写入 2065 字节内容，并按真实 `m5sync.process_files` 的
   “已存在且 MD5 一致”分支推进到 50%。
2. 构造第二条记录，`devicePath` 使用提问者日志中的重复值，`size=2065`，总大小 4130 字节；
   `url` 为本地假 HTTP 传输，MD5 由同一份 2065 字节内容计算。

只替换 HTTP 传输，`m5sync` 的文件存在性判断、`open(..., "wb")`、MD5 校验、重试和
`DownloadView` 状态机都走固件原生代码。

### 3.1 重复路径（Case A）

```text
PROBE_PAYLOAD 2065 2065
file_path: main_ota_temp.py md5: d587c2...
[INFO] File main_ota_temp.py already downloaded.
[INFO] MD5 mismatch for file: My_Project_1795168094430.py
PROBE_GET http://fixture.invalid/My_Project_1795168094430.py
[WARN] Download error: [Errno 2] ENOENT
[WARN] Retry 1...
...
[WARN] Retry 3...
[INFO] Failed to download file: apps/My_Project_1795168094430.py/My_Project_1795168094430.py
PROBE_DUP_ERR 'apps/My_Project_1795168094430.py/My_Project_1795168094430.py\n'
```

画面：`evidence/2026-11-23-failed-50.png`（`Failed 50%`），与提问者截图一致。

### 3.2 修正路径（Case B）

只把 `devicePath` 改成 `apps/My_Project_1795168094430.py`：

```text
[INFO] File main_ota_temp.py already downloaded.
[INFO] MD5 mismatch for file: My_Project_1795168094430.py
PROBE_GET http://fixture.invalid/My_Project_1795168094430.py
[INFO] File http://fixture.invalid/My_Project_1795168094430.py downloaded successfully.
[INFO] Downloaded and verified file: apps/My_Project_1795168094430.py
PROBE_FIXED_ERR ''
PROBE_EXISTS True
```

画面：`evidence/2026-11-23-success-100.png`（`Success 100%`）。

结论：`m5sync` 本身按 `devicePath` 原样保存；失败来自 `devicePath` 已经多了一层文件名，而不是
同步器再自行拼接。

## 4. 代码位置与根因

### 4.1 客户端把完整文件路径放进 `filePaths`

`m5stack/AIFlow @ 0bc08aa`：

- `src/renderer/src/utils/project/projectRunFiles.ts:89-99`

```ts
export const buildDeviceAppFile = (
  projectName: string,
  content: string,
  timestamp = Date.now()
): DeviceAppFile => {
  const fileName = buildDeviceAppFileName(projectName, timestamp)
  return {
    file: new File([content], fileName, { type: 'text/plain' }),
    filePath: `${DEVICE_APPS_PATH}/${fileName}`   // apps/My_Project_xxx.py
  }
}
```

- `src/renderer/src/utils/device/projectDeviceTransfer.ts:41-54`

```ts
if (includeAppFile) {
  const appFile = buildDeviceAppFile(projectName, mainPyContent)
  files.push(appFile.file)
  filePaths.push(appFile.filePath)
}

await downloadFiles({
  files,
  filePaths: filePaths.join(','),
  deviceId,
  clientId
})
```

`Run Always` 即 `includeMainPyInDownload=true`，会额外上传该 app 文件，并同时用
`main_ota_temp.py` 把 `boot_option` 置为 2（`runProjectOnDevice.ts:38-43`）。

### 4.2 设备端把 `devicePath` 当目录前缀

UIFlow2 `m5stack/components/m5things/m5things.c`（本地 HEAD `122954de`，约 1074-1097 行）：

```c
cJSON *new_file_dir = cJSON_GetObjectItemCaseSensitive(new_file, "devicePath");
cJSON *new_file_name = cJSON_GetObjectItemCaseSensitive(new_file, "name");
...
sprintf(new_file_path, "%s%s", new_file_dir->valuestring, new_file_name->valuestring);
```

设备收到的 `devicePath` 是 `apps/My_Project_1795168094430.py/`，`name` 是
`My_Project_1795168094430.py`，拼接后正是日志里的重复路径。也就是说，云端下发时把
`filePaths` 中的 `apps/My_Project_1795168094430.py` 当成了目录，补 `/` 后再交给
`name` 拼文件名。

`m5sync` 的 `process_files` 直接用 `file["devicePath"]` 作为保存路径：

- `uiflow-micropython` 的 `m5sync/sync.py`，2026-11-16 版本（`c7ebcf59`）：
  `[INFO] Downloading file: {file['devicePath']} size=...`，随后
  `download_file(file["url"], file["devicePath"])`。
- 父目录 `/flash/apps/My_Project_1795168094430.py/` 不存在，`open(tmp_path, "wb")` 抛
  `ENOENT`，重试 3 次后 `on_failed()` 显示 `Failed`。

### 4.3 根因

客户端和云端对 `filePaths` 的语义不一致：

- 客户端给的是**完整文件路径**（`apps/<name>.py`）；
- 云端按**目标目录**处理，补 `/` 后与上传文件名再拼一次；
- 设备端按拼接结果原样落盘。

因此 `Run Always` 只要上传 app 文件就会得到 `apps/<name>.py/<name>.py`，与项目内容无关。

## 5. 影响面

`buildDeviceFiles` 用同一个 `filePaths` 字段上传项目资源，值为
`res/<projectRelativePath>`（图片/音频分别为 `res/img/<name>`、`res/audio/<name>`），同样包含
文件名。按当前设备端拼接规则，带资源的项目会出现相同形式的重复后缀：

`res/img/foo.png/foo.png`

这一点是代码级推断，未通过真实云端上传验证（见未覆盖项）。提问者的项目只有 `main.py`，所以
只有自动生成的 app 文件触发了该问题。

## 6. 修复方向（未实施）

需要客户端与云端统一 `filePaths` 语义。按设备端 `m5things` 和 UIFlow2 Web 侧
`/flash/<devicePath>/<fileName>` 的既有用法，`filePaths` 应传目标**目录**：

- app 文件：`apps`；
- 项目普通文件：`res` 或 `res/<子目录>`；
- 图片：`res/img`；音频：`res/audio`。

或者云端接受完整文件路径、不再追加 `name`。无论选哪种，都应加一个含资源文件的
`Run Always` 回归用例，避免只测 `main.py` 项目时漏掉。

## 7. 未覆盖项

- **云端真实上传 NOT RUN**：没有提问者的 AIFlow 账号/设备，未调用
  `upload-resource-batch-and-push`，也未读取云端实现；“把 `filePaths` 当目录”是从设备端收到的
  `devicePath` 与 `m5things` 拼接结果反推。
- **实体 StickS3 NOT RUN**：本轮为 QEMU 虚拟设备；路径处理与实体共用同一份
  `m5things`/`m5sync` 代码，但没有实体串口/屏幕对照。
- **提问者固件版本不同**：本轮使用 AIFlow 仓库内 2026-07-22 固件，提问者日志是 2026-11-17
  固件；两版日志文案不同，失败路径与状态一致。
- **未修复**：没有修改 AIFlow 或 UIFlow2 仓库，也没有提交 patch。
