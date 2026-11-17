# m5stack/esphome #1 review: Chain ENV, DLight and IMU components

## What the PR adds

24 new files under `esphome/components/m5_chain_{env,dlight,imu}` (2171 lines):
one hub component per device built on `m5_chain_base`, plus `sensor`,
`binary_sensor` and `output` sub-platforms. Each node exposes its readings, the
firmware's own threshold alarms and its single RGB LED as per-channel float
outputs. The author tested on a Chain Captain with all three devices on one
chain and in Home Assistant; the PR says unit tests, component test YAMLs and
`CODEOWNERS` are not included, and that the Bright alarm and the ENV humidity,
pressure and altitude alarms were not triggered on hardware.

## Method

1. Checked the local Device Service (`GET /api/v1/devices`): 36 profiles, none
   is a Chain Captain or any Chain node, so a virtual-device run cannot exercise
   these components. No physical Chain hardware was available either.
2. Built the PR head with ESPHome 2026.11.0-dev, first for `esp32dev`
   (ESP-IDF 5.5.6) with three nodes on one UART, then for the ESPHome **host**
   target.
3. Ran the host binary against a pseudo-terminal that impersonates the three
   Chain nodes: it answers configuration commands with operation status 1,
   answers the read commands with fixed synthetic values, and injects `0xE0`
   event reports at scripted times. This exercises the component code and the
   `m5_chain_base` framing/scheduling, but not the device firmware, the UART
   electrical layer or the sensors.
4. Cross-checked every command code, payload order, unit and event mask against
   `m5stack/M5Chain` (`277dcfe8`, public Arduino library for the Chain series)
   and the Chain IMU UART protocol page (`docs.m5stack.com`, section 6.6).

## What works

- `esphome config` and `esphome compile --only-generate` accept a configuration
  with ENV + DLight + IMU on one bus, all sensors, all alarms and six outputs.
- `esphome compile` succeeds for `esp32dev` (ESP-IDF 5.5.6): 725079 bytes,
  Flash 39.5 %, RAM 27.3 %.
- Boot settings are emitted with the documented payloads, for example
  ENV `0x36 942700` (1013.2 hPa, no flash write), `0xE3 000a28`
  (source AHT20, 10..40 °C), `0xE5 1450` (20..80 %), `0xE7 1c250429`
  (950.0..1050.0 hPa), `0xE9 d0070000a0860100` (20..1000 m), `0xE1 0f`;
  DLight `0x33 8813000032000000` (high 5000 then low 50), `0x31 01`, `0xE1 01`;
  IMU `0xE3 2828` (40/40), `0xE5 003c`, `0xE1 07`.
- Readings decode correctly: AHT20 2350/100 -> 23.50 °C and 45 %, SPA06
  2400/10132/1234 -> 24.00 °C, 1013.2 hPa, 12.34 m, DLight 1234 lx,
  accel (0,0,1000) mg -> 9.80665 m/s², gyro 10/-10/30 dps, temperature 27.50 °C.
- The sparse 6-byte SPA06 answer is handled as well as the 8-byte one
  (`m5_chain_env.cpp:296-304`).
- Event decoding matches the library masks: ENV `0x01 0f` turns the temperature
  alarm on and `0x00 0f` releases it; IMU `0x03 10` sets motion+rotation,
  `0x04 10` clears both and sets the temperature alarm, `0x00 10` clears it;
  DLight `0x00/0x02/0x01/0x03` drives Dark/Bright on and off.
- `on_unsolicited()` filters by chain index, and late readings that arrive after
  a timeout are still decoded (`m5_chain_env.cpp:263-272` and equivalents).

## Findings

### 1. An alarm without its reading sensor never gets an initial state

`poll_next_()` gates every read on a sensor entity:

- `m5_chain_env.cpp:147-154`: AHT20 is read only if a temperature or humidity
  sensor exists; SPA06 only if pressure, altitude or barometer temperature exists.
- `m5_chain_dlight.cpp:108-112`: lux is read only if the illuminance sensor exists.
- `m5_chain_imu.cpp:137-147`: accel/gyro/temperature are read only for their sensors.

`publish_initial_alarm()` (`m5_chain_env.cpp:32-35`, `m5_chain_dlight.cpp:24-27`,
`m5_chain_imu.cpp:24-27`) can only be reached from those reads, so a
configuration that declares e.g. only `temperature_alarm`, only `low_light`, or
only `motion` never talks to the device except for the boot settings and leaves
the entity `unknown` until the first spontaneous crossing. The device is not
polled for the very quantity the alarm is about.

Reproduced with `code/host-alarmonly.yaml` (one alarm per node, no sensors):
7 configuration frames, **0 read requests, 0 state publications** in 13 s.
The full configuration publishes `OFF` for all alarms on the first read.

Suggested fix: queue the corresponding read when the alarm exists (or poll the
reading whenever an alarm is configured), so the initial state has a source.

### 2. No component test YAMLs and a stale CODEOWNERS

Every existing Chain component ships `tests/components/m5_chain_*` with
`common.yaml`, `test.esp32-idf.yaml` and a `<name>_test.cpp` unit test (12 of
12); these three have nothing, so the new sources are never built or tested by
CI. `script/build_codeowners.py --check` fails on the PR head ("CODEOWNERS file
is not up to date"), and `.github/workflows/ci.yml:238` runs exactly that check,
so CI will fail until the file is regenerated. The author already listed both
gaps in the PR body; they still gate the merge.

### 3. Minor: `update_interval` is declared twice

`m5_chain_env/__init__.py:29`, `m5_chain_dlight/__init__.py:37` and
`m5_chain_imu/__init__.py:59` extend `m5_chain_base.BASE_SCHEMA` (which already
defines `update_interval` with a 100 ms default) and then re-declare the same key
with a 10 s / 1 s default. The later default wins, as intended, but the emitted
code calls `set_update_interval()` twice per node and the base default silently
disappears. A single definition (or a comment) would avoid the duplication.

### 4. Open question: DLight interrupt mode versus polling

`ChainDLight`'s own documentation for `0x31` says that when interrupt
measurement is enabled "lux values are acquired only when they exceed the
configured interrupt threshold range". The PR enables `0x31` and `0xE1` whenever
a Dark/Bright alarm is configured, and keeps polling `0x30`. If the firmware
really stops updating the in-band value, the illuminance sensor would go stale
whenever an alarm is configured. This could not be checked here; a hardware
check with the sensor covered (in-band) while the alarms are active would settle
it, and the docs should state the interaction either way.

## Limits

- `NOT RUN` virtual-device validation. No Chain controller profile and no Chain
  peripheral model exist in the local Device Service, so the QEMU/esp-emu path
  cannot exercise this code.
- `NOT RUN` hardware validation. No Chain Captain, ENV, DLight or IMU was
  attached.
- The host harness answers in ~140 ms (ESPHome host UART read pacing), so
  "Slow response" log lines are a harness artefact, not a device measurement.
  Poll intervals were raised to 2 s to keep the three nodes from starving each
  other; no conclusion about real-bus timing is drawn.
- Not reviewed: home-assistant entity metadata beyond the generated config,
  documentation for the new components, and the `CODEOWNERS` content itself.
- The synthetic readings are fixed; sensor accuracy, calibration and the
  device's own threshold hysteresis were not exercised.
