# StackChan PR #137 评审报告

## 1. 任务与范围

- 目标：只读评审 `m5stack/StackChan#137`，按证据等级给出结论，并回复一条英文评论。
- 对象：新增 MicroSD 音乐播放器 App（`MUSIC`），head `db4fee0`，base `28b9f0c`。
- 边界：不关闭 PR、不 push 上游、不修改作者仓库；只发布一条评论。
- 验收层级：`build` = PASS；`flash` = PASS（虚拟 flash）；
  `visual_or_physical` = PARTIAL（虚拟屏幕/触摸，不含实机）；
  `device_response`（真实 SD 卡）= `NOT RUN`。

## 2. 条目现状

`gh pr view 137`：`OPEN`，`comments=[]`，`reviews=[]`，作者 `NicolasChicunque`，
标题与正文均为英文。PR 检查里只有仓库内的 WeCom 转发工作流，没有构建或测试 CI。
不存在 m5agent 已回复或条目已关闭的情况，需要处理。

## 3. 验证路径

优先级按 hardware > virtual-device > host-level > code-level：

1. **hardware**：本机没有 StackChan 实机接入，`NOT RUN`。
2. **virtual-device**：`GET /api/v1/devices` 确认存在 `stackchan` profile
   （qemu-esp32s3、ILI9342C 320x240 触摸、`generic-flash`、`features.storage=false`），
   因此按流程导入自建 merged BIN、创建会话、采集串口与画面。
3. **code-level**：并发、NVS、WAV/MP3 边界、allocator 语义用源码定位。
4. **host-level test**：仓库的 host 测试只覆盖运动坐标helper，与本次改动无关，未运行。

## 4. 改动范围

15 个文件、+8052/-9：

- 新增 App：`app_music_player.cpp` 2,255 行、`.h` 268 行、`minimp3.h` 1,948 行、
  `assets/icon_music.c` 3,543 行、`assets_bin/icon_music.bin` 84,612 B；
- 共享改动：`hal/board/stackchan.cc`（MISO）、`hal/hal.cpp`（刷新时序）、
  `hal/hal_toggles.h`（NVS 键 + 新 App）、`main.cpp`（安装顺序）、
  `app_setup.cpp`（warm reboot 索引 6→7）、`sdkconfig.defaults`（字体）、
  `CMakeLists.txt`（sdmmc/vfs）。

`app_setup.cpp` 的索引调整是必要的：安装顺序变成 AI(0)…Dance(5)、Music(6)、Setup(7)，
与 `AppLauncher` 按未过滤 app 列表取下标的约定一致。

## 5. 结果

### 5.1 构建 PASS

- ESP-IDF v6.1（xtensa-esp-elf GCC 15.2.0），`python3 ./fetch_repos.py` + 63 个
  managed_components，`idf.py build` 2503/2503，退出码 0。
- `stack-chan.bin` 3,976,928 B（0x3caee0），ota_0 分区 0x4f0000，余量 23%。
- merged BIN 12,941,738 B，SHA-256 `de1b0779acf8d8143ad530c2d5e8d0f20e1d561f195c16442db7673a85377583`。

### 5.2 虚拟设备 PASS（集成层）

- 启动到 launcher，`[MUSIC] on create` 出现；轮播第 7 个图标为 MUSIC，图标来自
  assets（`icon_music.bin`），不是 fallback。
- 进入 App 后主界面完整：标题、电量、进度条、时间、VOL/版本、状态、表情、6 按钮。
  无卡时标题为 `NO MUSIC`，播放列表显示 `SD NOT MOUNTED / FORMAT AS FAT32`。
- 设置页 7 个按钮与 BACK 正常；`EXIT` 触发 `warm reboot request to app index: 6`。
- 无卡挂载日志：
  `sdmmc_init_sd_if_cond ... returned 0x108` → `ESP_ERR_INVALID_RESPONSE`，
  App 捕获后继续，不崩溃。
- 资源：进入 MUSIC 后内部 SRAM free 92 KB / minimal 39,828 B（launcher 为 111 KB / 44 KB）。

### 5.3 播放路径 NOT RUN

`stackchan` profile 没有 microSD/storage 模型，也没有可注入的 SD 镜像。扫描、解码、
重采样、seek、切歌、循环/随机、播放中拔卡均未验证；作者正文的 1,022 首实机测试属于
作者自述，不能替代本机证据。

## 6. 逐项发现

### F1（高，建议合并前修）LVGL 锁外调用 `GetStackChan().update()`

`app_music_player.cpp:306-310`：

```cpp
beat_update(now);
GetStackChan().update();

{
    LvglLockGuard lock;
```

`GetStackChan().update()` 会走到 `Avatar::update()`，更新 LVGL 元素
（`stackchan/avatar/skins/default/eyes.cpp` 等使用 `uitk::lvgl_cpp::Container`）。
HAL 的更新任务（`hal.cpp:158`）和 DANCE（`app_dance.cpp:97-118`）都在
`LvglLockGuard` 内调用同一个函数。Mooncake 主循环在 app_main 任务，LVGL 在
esp_lvgl_port 的任务里，因此这里是无锁跨任务访问，长时间播放/频繁刷新时可能破坏
LVGL 状态。把 `GetStackChan().update()` 移进下面的锁作用域即可。

### F2（中）`visible_mask` 改名会重置老用户偏好

`hal_toggles.h:10` 把键从 `visible_mask` 改为 `visible_mask_v2`。`save_states()`
（`hal_toggles.cpp:57-74`）只写 mask，从不写 `TOGGLE_LIST[i].key` 对应的旧独立键；
`load_states()` 在 v2 缺失时回退到这些键，现网设备通常没有，于是回到默认全开。
升级后用户此前隐藏的 DANCE/AVATAR 等会重新出现。

建议：v2 缺失时先读 `visible_mask`，用低 6 位恢复，Music 位补 1，再写回 v2。

### F3（低）24-bit WAV 探测成功但播放静默跳过

`probe_wav()`（:614）对任意 PCM 都置 `valid=true`；播放分支只处理 16/8 bit
（:864-874），其余立即 `close_file()` + `_track_eof=true`，表现为显示时长、播放时
直接跳下一首。建议探测阶段把 bits 限制为 8/16，或实现 24-bit 转换并给出提示。

### F4（低）MP3 坏帧整块丢弃缓冲

`frame_info.frame_bytes == 0` 且未 EOF 时（:936）直接 `mp3_buf_filled = 0`，丢掉最多
16 KB 已读数据，遇到文件中部垃圾/标签时会吞掉后续有效音频。前移 1 字节重新同步更稳。
另：`probe_mp3()`（:647）在没找到帧头时也置 `valid=true`，坏文件会显示 0:00。

### F5（低）`PsramAllocator::allocate` 的 OOM 语义

`app_music_player.h:27-34` 在 OOM 时返回 `nullptr`。标准 allocator 要求抛
`std::bad_alloc`；`std::vector`/`std::string` 扩容依赖该契约，返回空指针属于未定义行为。
建议抛异常或改用 `heap_caps` + 显式容量检查。

### F6（低）全局时序改动与本功能无关

`hal.cpp:151-160` 把非 idle 分支的 `vTaskDelay` 从 100 ms 改为 80 ms。移出
`LvglLockGuard` 本身是改进，但 20 ms 的全局节奏变化影响所有 App，建议拆出或给出测量依据。

### F7（低）打开 App 时同步扫描

`onOpen()`（:245-246）先 `mount_sd()` + `scan_tracks()` 再 `build_ui()`；扫描递归 3 层、
上限 2,000 条，循环内无让出。1,000+ 曲目时首帧延迟为秒级。可先出 UI 再异步扫描并显示进度。
`open_list()`（:1941-1948）在列表为空时会重试挂载，插卡后有恢复路径，这点是好的。

### 已核实不是问题

- **GPIO35 共用**：IDF v6.1 `esp_lcd_panel_io_spi.c` 在每笔事务后关闭 D/C 输出
  （:438-441），事务之间 GPIO35 回到输入，SD 可读 MISO；LCD/SD 事务由 SPI3 串行化。
  该改动成立，但建议在 board 文件加注释，避免后续 IDF 或驱动变化时回退成“D/C 常开”。
- **FATFS 长文件名**：本机构建的 `sdkconfig.h` 为 `CONFIG_FATFS_LFN_HEAP=1`、
  `CONFIG_FATFS_MAX_LFN=255`，IDF 6.1 默认已开，不需要额外配置。
- **PSRAM 任务栈**：ESP32-S3 上 `CONFIG_FREERTOS_TASK_CREATE_ALLOW_EXT_MEM` 默认为 y，
  音频任务自身不做 flash/NVS 写（NVS 由主任务写），当前用法可用；但栈在 PSRAM 的方案
  需要保证该任务永不触发 flash 操作，建议注释说明。

## 7. 未覆盖项

- 真实 SD 卡：挂载、扫描、MP3/WAV 解码、24 kHz 重采样、seek、切歌、循环/随机——`NOT RUN`。
- 音频输出质量、音量、爆音、I2S 时钟——`NOT RUN`。
- 舵机摆动、RGB 随拍、头部校准的实际运动——`NOT RUN`。
- NVS 跨断电持久化、升级后偏好迁移——`NOT RUN`（后者由源码判定会丢）。
- 实机 GPIO35 pad 级电气行为——`NOT RUN`。
- EXIT 后 warm reboot 在虚拟设备上停在 `cpu_start: Multicore app`；复位日志为
  `RTC_SW_CPU_RST`，无 panic/TWDT，停点在 app_main 之前，判为虚拟设备 reset 路径限制，
  没有在实机复现。

## 8. 合并建议

可以进入合并讨论。合并前建议至少修 F1、F2；F3–F7 可作为 follow-up。作者已在实机跑过
1,022 首曲目，若能补一份该 commit 的串口日志（挂载参数、扫描数量、实际解码/输出错误）
和一次 24-bit WAV / 损坏 MP3 的对照，会更完整。

## 9. 证据修正说明

本记录早期只有源码阅读的草稿曾把 GPIO35 共用判为阻塞缺陷。在阅读本机 ESP-IDF v6.1
`esp_lcd_panel_io_spi.c` 并完成构建 + 虚拟设备启动后，该判断被推翻：D/C 输出在每笔
事务后关闭，GPIO35 在事务间恢复为 MISO 输入。本版本为修正后的结论。
