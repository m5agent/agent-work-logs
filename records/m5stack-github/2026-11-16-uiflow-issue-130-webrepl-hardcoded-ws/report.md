# uiflow-micropython #130: webrepl endpoint, NVS and gating review

## Background

`m5stack/uiflow-micropython#130` (FxIII, 2026-11-15T22:44Z, open) reports that the
`webrepl` component in recent releases opens a plaintext outbound WebSocket to a
hardcoded `uiflow2.m5stack.com` endpoint, ignores the `uiflow`/`server` NVS value,
no longer checks whether it should start, and pipes `clientMessage` payloads into
the MicroPython stdin ring buffer.

Goal of this review:

1. check each claim against the source at the current `master`;
2. reconstruct the commit history that produced the current behaviour;
3. check whether the claim is present in the published 2.5.4 images;
4. state evidence class and unverified limits; no code change, no upstream push.

## Version and method

- `m5stack/uiflow-micropython@54b1d2424174cb032a6726cc007e5df4e479456e` (`master`,
  2026-11-13 push). `webrepl.c` blob `0f23c8e2a23d1a00d203329bc4dbdf7872c3e7d9`,
  `main.c` blob `fe19f86352369a5e83fd0663de92844339d72559`. Blob hashes were read
  through the GitHub contents API and match the local clone for `webrepl.c`.
- The local clone's `main.c` has unrelated emulator modifications, so its blob
  differs. The `webrepl` call-site region is byte-identical (`git diff -U1
  m5stack/main.c | grep webrepl` returns nothing) and the authoritative `master`
  content was fetched through the API.
- Commit history inspected in the local clone: `7a5f7598`, `05c2ca20`,
  `8003d01a`, plus later `webrepl` commits.
- Release images: public GitHub Release `2.5.4`, CoreS3 and StickS3 assets,
  inspected with `strings -a`.

## Findings

### 1. Hardcoded endpoint, no NVS read

`m5stack/components/webrepl/webrepl.c`:

```c
#define WEBREPL_URI_TEMPLATE "ws://uiflow2.m5stack.com/ws/realtime?role=device&mac=%s"
```

`webrepl_build_uri()` (`110-126`) reads the MAC (EFUSE on P4, Wi-Fi STA MAC
otherwise) and formats the URI. There is no `nvs.h` include and no `nvs_*` call in
the file, so the `uiflow`/`server` key cannot influence this connection.

For comparison, `m5stack/components/m5things/m5things.c:2198-2205` does read the
same key for MQTT:

```c
if (nvs_read_str_helper(UIFLOW_NVS_NAMESPACE, "server", nvs_server_uri, &uri_len)) {
    sprintf(server_uri, "mqtt://%s:1883", nvs_server_uri);
    mqtt_cfg.broker.address.uri = server_uri;
} else {
    mqtt_cfg.broker.address.uri = "mqtt://uiflow2.m5stack.com:1883";  // default
}
```

The factory NVS image sets the key explicitly: `m5stack/partition_nvs.csv:3`
contains `server,data,string,uiflow2.m5stack.com`, and `m5stack/Makefile:198`
passes the generated `nvs.bin` into `pack_fw`, i.e. it is part of the merged
release image.

Conclusion: the asymmetry described in the issue is real. `m5things` honours the
key; `webrepl` cannot.

### 2. History: gated introduction, then gate removal

`7a5f7598` ("aiflow: Add runtime-gated WebREPL support.") introduced the component
with:

```c
#define WEBREPL_ENABLED_SERVER "aiflow.m5stack.com"

bool webrepl_should_start(void) {
    char server[WEBREPL_SERVER_MAX_LEN] = {0};
    return webrepl_read_server(server, sizeof(server)) && strcmp(server, WEBREPL_ENABLED_SERVER) == 0;
}
```

and `main.c` only created the task inside `if (webrepl_should_start())`.

`05c2ca20` ("aiflow: enable fixed websocket webrepl", 2026-08-14) removed
`webrepl_read_server()`, `webrepl_should_start()`, the `nvs.h` include, the
`ws://%s/...` template and the `if` in `main.c`, replacing all of it with a fixed
URI and an unconditional `xTaskCreatePinnedToCore(webrepl_task, ...)`. `8003d01a`
("aiflow: derive websocket MAC from device") replaced the fixed developer MAC
with the `%s` MAC template 19 minutes later. No later commit restored the gate;
`grep -rn "webrepl_should_start\|webrepl_read_server" m5stack/` returns nothing.

Two details that refine the issue text:

- The removed gate compared `server` to the single host `aiflow.m5stack.com`. It
  was an allow-list used to enable the feature on provisioned devices, not a
  general "use whatever host the user configured" mechanism. A device keeping
  the factory default `server=uiflow2.m5stack.com` never started webrepl before
  2.5.1. So the regression is "gate removed", but the old code did not provide
  self-hosting either.
- `05c2ca20`'s fixed developer MAC never reached the 2.5.x tags checked here:
  2.5.0 has the gated blob, 2.5.1/2.5.2 already contain `8003d01a`'s dynamic-MAC
  version. Intermediate CI images were not checked.

### 3. Unconditional start

`m5stack/main.c:319-321`:

```c
#if WEB_REPL_ENABLE
xTaskCreatePinnedToCore(webrepl_task, "webrepl_task", 6000, NULL, MP_TASK_PRIORITY + 1, &webrepl_task_handle, MP_TASK_COREID);
#endif
```

`WEB_REPL_ENABLE` defaults to `0` (`CMakeListsDefault.cmake:174-179`) and is set to
`1` by 13 of the 53 board directories: AirQ, AtomS3, AtomS3R, CardputerADV,
CoreS3, Dial, PaperMono, PaperS3, StackChan, StamPLC, StickS3, StopWatch, Tab5.
The issue's "almost all S3/P4 board configs" is broader than the actual set
(Cardputer, StampS3, StampP4 and others are not enabled), but every model it named
is enabled.

The task blocks in `webrepl_wait_network()` (`442-447`) until `wifi_sta_connected`
or `lan_connected`, then starts the client and retries every 3 s
(`WEBREPL_RESTART_DELAY_US`, `reconnect_timeout_ms`). This matches "upon Wi-Fi
connection"; it is not tied to any user action.

### 4. Message path into the REPL

```c
cJSON *type = cJSON_GetObjectItem(root, "type");
if (cJSON_IsString(type) && strcmp(type->valuestring, "clientMessage") == 0) {
    cJSON *payload = cJSON_GetObjectItem(root, "payload");
    if (cJSON_IsString(payload) && payload->valuestring != NULL) {
        webrepl_queue_input(payload->valuestring, strlen(payload->valuestring));
    } else if (cJSON_IsNumber(payload)) {
        ...
    }
}
```

`webrepl_process_text_message()` (`299-335`) has no sender, session or permission
check. `webrepl_queue_input()` (`181-195`) maps `\n` to `\r` and routes `0x03` to
`webrepl_interrupt()`; all other bytes go into the 4 KiB rx ring.
`webrepl_drain_rx_to_stdin()` (`197-218`) moves them into MicroPython's
`stdin_ringbuf`, and `0x03` additionally calls `mp_sched_keyboard_interrupt()`
when the REPL has enabled the interrupt character (which `pyexec` does while the
friendly REPL reads input).

Consequences, stated at code level:

- A `clientMessage` frame is indistinguishable from serial keyboard input.
- An injector can send `0x03` first to break out of a running program where the
  REPL has enabled interrupts, then send commands; arbitrary execution is not
  limited to an already-idle prompt.
- If a program never reads stdin, bytes accumulate in the 4 KiB rx buffer and are
  consumed later, so the window does not close.
- Output is mirrored only when `dupterm_objs[0]` is free
  (`webrepl_install_dupterm_if_needed()`, `557-573`); input injection does not
  depend on that.

### 5. Transport and authentication

`webrepl_start_client()` (`449-480`) builds a client config with `uri`,
`task_name`, buffer/timeouts and keep-alive only. There is no `headers` field, no
token, no username/password, and the scheme is `ws://` (no TLS). The only
identity presented is the MAC in the query string, in clear text.

Therefore the trust boundary is (a) the server and (b) the integrity of the
network path. An on-path party can forge a `clientMessage` without knowing any
credential; whether a third party can also open a session claiming an arbitrary
MAC depends on server-side checks that are not in this repository.

### 6. Presence in published images

`2.5.4` CoreS3 and StickS3 images (asset names below) contain the exact template
string, the C task names `webrepl_task` / `webrepl_ws`, and zero `wss://` strings:

| asset | size | sha256 |
| --- | --- | --- |
| `uiflow-e437118-esp32s3-spiram-16mb-cores3-v2.5.4-20261030.bin` | 16,121,856 | `a7b2483a74323800a6febfb652c89581b01371abf7503c1cc338012930ec2e5f` |
| `uiflow-e437118-esp32s3-spiram-8mb-sticks3-v2.5.4-20261030.bin` | 8,384,512 | `44fca7556643c34e316532c3dddcc184bef43f420ae711598212259ef73106f9` |

This proves the published build contains the component and the endpoint template.
It does not prove runtime behaviour; that is covered separately below.

### 7. Suggested fix directions (not implemented here)

The issue's three suggestions address distinct gaps and are consistent with the
code:

1. read `uiflow`/`server` in `webrepl_build_uri()` and use it as the host, with a
   documented fallback. Note `webrepl_uri[192]` and `char nvs_server_uri[32]` in
   `m5things` show the existing size assumptions; a longer host needs an explicit
   length policy.
2. restore a device-side gate so the task does not start without an explicit
   opt-in. Reinstating the `aiflow.m5stack.com` equality check would restore
   pre-2.5.1 behaviour only; honouring the user's `server` value needs a separate
   decision, because the factory default would then enable the channel on every
   device.
3. `wss://` and a per-device or shared secret require a matching server-side
   change; the client alone cannot close the plaintext/impersonation gap.

## Evidence and commands

All evidence is under `evidence/`:

- `webrepl-key-lines.txt`: numbered excerpts of the current source from the GitHub
  contents API.
- `original-gate-7a5f7598.txt`: the pre-regression gated implementation.
- `checks.txt`: blob hashes by tag, commit IDs, board counts, residual-gate grep.
- `release-bin-strings.txt`: asset hashes and `strings` matches.

Reproduce the binary check:

```bash
gh release download 2.5.4 --repo m5stack/uiflow-micropython \
  -p '*sticks3-v2.5.4*.bin' -p '*cores3-v2.5.4*.bin'
shasum -a 256 *.bin
strings -a <image>.bin | grep -n 'ws://uiflow2.m5stack.com/ws/realtime'
strings -a <image>.bin | grep -c 'wss://'   # 0
```

## Limits and risk

- `NOT RUN` runtime injection. Reproducing the execution path end to end would
  require sending a `clientMessage` through the production channel (creating a
  device session) or running an on-path proxy against a machine on that channel.
  Neither was done; the conclusion is source-level.
- `NOT RUN` device/emulator boot. The retail image is built at default log level,
  so the `ESP_LOGD` "task start" marker would not appear; a boot would only show
  the outbound connection, not the injection path.
- `NOT RUN` server implementation. Device authentication, MAC ownership and frame
  authorization are server-side and were not inspected.
- `NOT RUN` web IDE opt-in. Whether the UIFlow2 front end exposes an explicit
  opt-in was not checked; the device has no local opt-in regardless.
- Scope note: `m5things` already connects to `uiflow2.m5stack.com` by default for
  MQTT, so "the device contacts the cloud" is not new. What is new in 2.5.1+ is
  the ungated, plaintext REPL channel.
- The fixed MAC value from `05c2ca20` is intentionally omitted from this record.
