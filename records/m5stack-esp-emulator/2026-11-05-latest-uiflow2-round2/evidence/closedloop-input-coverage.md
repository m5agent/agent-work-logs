# R2-CLA — closed-loop INPUT direction coverage (112 Units, 2026-11-05)

Lane: **virtual-device validation** — Device Service `<agent-service>` (token-less local-control),
canonical Unit runtime `.work/goals/2026-11-04-uiflow-full/runtime-build/build-xtensa/qemu-system-xtensa`
(sha256 `0e16a9bcd86b588dae6b3e3b523dfb8610a9eca37c50c141cce5f2ceb4612068`). Every guest ran with `purge=0` (history retained); no values were fabricated.

Method: (1) audit latest-round `.work/uiflow-latest-20261105/units/results.json` + per-case
`result.json`, (2) audit prior-round tracked evidence (`docs/evidence/2026-11-03-unit-*`) and
`tests/units/*` official-driver probes, (3) fill missing/partial Units with official-driver waves on 8907.
Per-field coverage requires **an injected fixture value and a guest-observed readback** (raw or
driver-converted); fields whose writable input was never injected by a probe are listed as missing.

## Result: `107` COVERED / `5` PARTIAL / `0` MISSING / `0` BLOCKED / `0` NOT RUN (of 112)

Evidence basis: `{'latest-round units (8907)': 82, 'CL-A round-2 fresh execution (8907)': 8, 'CL-A wave1 latest-firmware (8907)': 8, 'prior-round 2026-11-03 docs evidence': 14}`
Fresh round-2 executions (new 8907 sessions, latest firmware): **16** Units; `executed_round2` column below marks Units whose proof is a new session created for round 2.

## Round-2 fresh injection→read executions (8907, latest firmware)

Lead request: fresh execution evidence (simulator state changed → guest code reads it), not re-audit.
Each row is a **new visible session** on the canonical Unit runtime; injected fixture values, the
guest-read values and the firmware identity are taken from that session's `result.json`.

| unit | category | device | new session_id | injected fixture (vectors) | guest read | firmware sha256 | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| joystick | position/input (X/Y/button raw) | cores3 | `8892fd1c234f4c10bcb29c757326b3ad` | {"x-raw": 37, "y-raw": 201, "button-raw": 1} | ["37", "201", "1"] | `5847a2bcae33d6bb…` | **PASS** |
| adc-v11 | electrical/ADC (ADS1110 voltage) | stopwatch | `82257bc0aff04c81bf6cc28f23608162` | {"voltage-mv": 1000.0} | {"voltage": "1.0", "initial-voltage": "1.0", "initial-raw": 2623, "qom-raw": 1311} | `0bcb9269f42186ec…` | **PASS** |
| env | environment (temperature+humidity+pressure, 2 distinct vectors) | atoms3r | `fb8c302a734049bfbbde0a89e98e6a3c` | {"temperature-c": 25.5, "humidity-pct": 60.5, "pressure-pa": 100000.0}; {"temperature-c": 31.25, "humidity-pct": 45.0, "pressure-pa": 90000.0} | ["25.5", "60.5", "1000.0"]; ["31.3", "45.0", "900.0"] | `c289f7df74919b0b…` | **PASS** |
| env-iv | environment (SHT40 temperature+humidity, BMP280 pressure) | atoms3r | `835f81178c6b4eb7a64ef1ffd3717a88` | {"temperature-c": 25.5, "humidity-pct": 60.5, "pressure-pa": 100000.0} | ["25.5", "60.5", "1000.0"] | `c289f7df74919b0b…` | **PASS** |
| co2 | air quality (CO2 ppm + humidity + temperature fixture) | sticks3 | `59a2fd963cfc4cfcb545b6ff1ba07ce4` | {"co2-ppm": 1234, "temperature-c": 25.5, "humidity-pct": 60.5, "data-ready": true} | {"co2": "1234", "humidity": "60.5", "temperature": "25.97", "serial_tuple": "(18, 52, 86, 120, 0, 0)"} | `fd85648dfa1fd965…` | **PASS** |
| tof4m | distance/optical (ToF4M distance) | cores3 | `19cb8012b12643cf81ebff2648f1eb70` | null | {"serial_tail": "f8\r\nload:0x403c8700,len:0xb34\r\nload:0x403cb700,len:0x2d24\r\nentry 0x403c8890\r\nE (2142) i2c.master: this port has not been initialized, please initialize it first\r\nBATCH4_PROBE_START tof4m\nE (2853) i2c.master: this port has not been initialized, please initialize it first\r\nBATCH4_PROBE_READY tof4m\nI2C_TOF4M_MODEL (234, 204, 16)\nI2C_TOF4M_READY 1\nI2C_TOF4M_DIST 1000\nI2C_TOF4M_BUDGET 50\nI2C_TOF4M_END\n"} | `5847a2bcae33d6bb…` | **PASS** |
| env-pro | environment (SHT40/BMP280) | cores3 | `0ced21042c5e4faa905198c5e3c3feda` | null | {"serial_tail": "\nload:0x403cb700,len:0x2d24\r\nentry 0x403c8890\r\nE (1001) i2c.master: this port has not been initialized, please initialize it first\r\nBATCH6_PROBE_START env-pro\nE (1497) i2c.master: this port has not been initialized, please initialize it first\r\nBATCH6_PROBE_READY env-pro\nI2C_BME_ID 97 1\nI2C_BME_RAW 8001188940000478747a\nI2C_BME_STATUS 128\nI2C_BME_DECODED_OBSERVATION 0.0 0.0 0.0 102400.0\nI2C_BME_END\n"} | `5847a2bcae33d6bb…` | **PASS** |
| thermal2 | thermal (Thermal2 raw frame/temperature) | cores3 | `9f6c37be46e8435c89f57d300f70af43` | null | {"serial_tail": "8890\r\nE (993) i2c.master: this port has not been initialized, please initialize it first\r\nBATCH6B_PROBE_START thermal2\nE (1447) i2c.master: this port has not been initialized, please initialize it first\r\nBATCH6B_PROBE_READY thermal2\nT2_DETAIL 0x4064 100.1\nT2_ADDR 0x32\nT2_ALARM 0\nT2_BUTTON 0\nT2_MEASURE 31.5 -63.63 30.0\nT2_DIFF_POS 0 0\nT2_BUFFER_LEN 384\nT2_BUFFER_HEAD 12224 12256 12224 13216\nT2_END\n"} | `5847a2bcae33d6bb…` | **PASS** |

The wave-1 CAN/LoRaWAN fills below are also new latest-firmware sessions from this round:

## Fill waves (new 8907 latest-firmware sessions: wave1 CAN/LoRaWAN + wave2 batch12a re-runs)

| unit | device | session | latest base firmware sha256 | result |
| --- | --- | --- | --- | --- |
| can | cores3 | `7c7d3b36a1ba4aa5881eb567a1332692` | `5847a2bcae33d6bb…` | **COVERED** |
| mini-can | cores3 | `b1318d0a39fc4145b42eb1dd3991ec77` | `5847a2bcae33d6bb…` | **COVERED** |
| lorawan-us915 | cores3 | `253eaf20dbfe4451a0d867c7ee25b7bc` | `5847a2bcae33d6bb…` | **COVERED** |
| cardkb2 | cores3 | `f4126c7a32ec4f519bf05a4481598471` | `5847a2bcae33d6bb…` | **PARTIAL** |
| 8servos2-i2c | cores3 | `5726ef20bdd2462fa7e2930243c7f794` | `5847a2bcae33d6bb…` | **PARTIAL** |
| step16 | cores3 | `fba1ff7d610d417ca7e2b09863166418` | `5847a2bcae33d6bb…` | **PARTIAL** |
| timerpwr | cores3 | `f76c542c17044537b744e20ee88de6e3` | `5847a2bcae33d6bb…` | **PARTIAL** |
| mq | cores3 | `fe686a5f851a4aebb118aea0e852f232` | `5847a2bcae33d6bb…` | **PARTIAL** |

Wave 1 re-ran the three CAN/LoRaWAN Units that appeared BLOCKED in the latest-round batch8 lane
(batch8 `EXPECTED_BLOCKED`: it does not attach the CAN/TWAI or UART responder lanes). The dedicated
official-driver `run_can_lorawan_cases.py` lane was re-run by CL-A on 8907 against the latest
firmware: `can` / `mini-can` inject one host CAN frame through the Unit QOM `inject-hex` and the guest
receives exactly that frame; `lorawan-us915` applies the UART `responses-hex` fixture and the guest
AT byte layer is observed. All checks passed (13/13, 13/13, 15/15).

## Per-Unit coverage table

| # | unit | declared inputs (injectable) | evidence basis | identity | covered | missing | verdict | executed_round2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | earth | analog-mv, digital-level | latest-round units (8907) | latest fw `c289f7df7491…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 2 | hall | magnetic-detected | latest-round units (8907) | latest fw `fd85648dfa1f…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 3 | reflective-ir | analog-mv, digital-level | latest-round units (8907) | latest fw `0bcb9269f421…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 4 | dlight | illuminance-lx | latest-round units (8907) | latest fw `c289f7df7491…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 5 | accel | accel-x-g, accel-y-g, accel-z-g, int-source | latest-round units (8907) | latest fw `fd85648dfa1f…` / canonical runtime | 4/4 | — | **COVERED** | no |
| 6 | weight-i2c | adc-raw, weight-fw, weight-g | latest-round units (8907) | latest fw `0bcb9269f421…` / canonical runtime | 3/3 | — | **COVERED** | no |
| 7 | ncir2 | button-pressed, chip-c, object-c | latest-round units (8907) | latest fw `c289f7df7491…` / canonical runtime | 3/3 | — | **COVERED** | no |
| 8 | extio2 | adc-mv, fw-version, input-levels | latest-round units (8907) | latest fw `fd85648dfa1f…` / canonical runtime | 3/3 | — | **COVERED** | no |
| 9 | hbridge | adc-mv, vin-current-a | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 10 | joystick | button-raw, x-raw, y-raw | CL-A round-2 fresh execution (8907) |  | 3/3 | — | **COVERED** | yes |
| 11 | watering | analog-mv | latest-round units (8907) | latest fw `c289f7df7491…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 12 | fader | analog-mv | latest-round units (8907) | latest fw `c289f7df7491…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 13 | dac | dac-raw | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 14 | bps | pressure-pa, temperature-c | latest-round units (8907) | latest fw `fd85648dfa1f…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 15 | adc-v11 | voltage-mv | CL-A round-2 fresh execution (8907) |  | 1/1 | — | **COVERED** | yes |
| 16 | env | humidity-pct, pressure-pa, temperature-c | CL-A round-2 fresh execution (8907) |  | 3/3 | — | **COVERED** | yes |
| 17 | ameter | current-a | latest-round units (8907) | latest fw `fd85648dfa1f…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 18 | extencoder | counter, fw-version, perimeter, pulse, zero-mode, zero-pulse | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 6/6 | — | **COVERED** | no |
| 19 | ain4-20ma | adc-raw, cal-ma, current-ma, fw-version | latest-round units (8907) | latest fw `0bcb9269f421…` / canonical runtime | 4/4 | — | **COVERED** | no |
| 20 | acssr | fw-version | latest-round units (8907) | latest fw `c289f7df7491…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 21 | gesture | gesture, gesture-flags | latest-round units (8907) | latest fw `fd85648dfa1f…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 22 | rfid | card-present | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 23 | tube-pressure | analog-mv | latest-round units (8907) | latest fw `c289f7df7491…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 24 | laser-rx | digital-level | latest-round units (8907) | latest fw `c289f7df7491…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 25 | extio | input-levels | latest-round units (8907) | latest fw `fd85648dfa1f…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 26 | scales | adc-raw, button-status, weight-g | latest-round units (8907) | latest fw `fd85648dfa1f…` / canonical runtime | 3/3 | — | **COVERED** | no |
| 27 | vmeter | voltage-v | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 28 | adc | voltage-v | latest-round units (8907) | latest fw `0bcb9269f421…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 29 | env-iv | humidity-pct, pressure-pa, temperature-c | CL-A round-2 fresh execution (8907) |  | 3/3 | — | **COVERED** | yes |
| 30 | co2 | co2-ppm, data-ready, humidity-pct, temperature-c | CL-A round-2 fresh execution (8907) |  | 4/4 | — | **COVERED** | yes |
| 31 | pbhub | analog-inputs, digital-inputs | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 32 | ultrasonic-io | distance-mm | latest-round units (8907) | latest fw `0bcb9269f421…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 33 | rs485-iso | rx-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 34 | laser-tx | — | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 0/0 | — | **COVERED** | no |
| 35 | co2l | co2-ppm, data-ready, humidity-pct, temperature-c | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 4/4 | — | **COVERED** | no |
| 36 | neco | — | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 0/0 | — | **COVERED** | no |
| 37 | midi | rx-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 38 | tof4m | data-ready, distance-mm | CL-A round-2 fresh execution (8907) |  | 2/2 | — | **COVERED** | yes |
| 39 | weight | adc-raw, channel | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 40 | bldc-driver | direction, mode, pole-pairs, pwm, rpm | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 5/5 | — | **COVERED** | no |
| 41 | ac-measure | active-power-w, apparent-power-va, current-a, data-ready, energy-kwh, power-factor, voltage-v | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 7/7 | — | **COVERED** | no |
| 42 | dds | freq-reg, frequency-hz, phase-deg, phase-reg, waveform | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 5/5 | — | **COVERED** | no |
| 43 | gps | nmea-lines | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 44 | uhf-rfid | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 45 | pbhub-v11 | analog-inputs, digital-inputs | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 46 | op90 | digital-level | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 47 | 8angle | adc12-raw, adc8-raw, switch-pressed | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 3/3 | — | **COVERED** | no |
| 48 | kmeter-iso-v11 | data-ready, internal-temperature-c, thermocouple-temperature-c | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 3/3 | — | **COVERED** | no |
| 49 | pahub-v20 | — | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 0/0 | — | **COVERED** | no |
| 50 | rtc | running, unix-time | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 51 | tmos-pir | gain-mode, motion, odr, presence, shock, tambient-c, tobject-c | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 7/7 | — | **COVERED** | no |
| 52 | neohex | — | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 0/0 | — | **COVERED** | no |
| 53 | lora-e220-433 | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 54 | zigbee | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 55 | nbiot2 | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 56 | mini-scales | adc-raw, weight-g | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 57 | op180 | digital-level | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 58 | mini-imu | accel-range, accel-x-g, accel-y-g, accel-z-g, gyro-range, gyro-x-dps, gyro-y-dps, gyro-z-dps, temperature-c | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 9/9 | — | **COVERED** | no |
| 59 | env-pro | data-ready, gas-resistance-ohm, humidity-pct, pressure-pa, temperature-c | CL-A round-2 fresh execution (8907) |  | 5/5 | — | **COVERED** | yes |
| 60 | unit-id | — | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 0/0 | — | **COVERED** | no |
| 61 | thermal2 | average-c, differential-c, median-c | CL-A round-2 fresh execution (8907) |  | 3/3 | — | **COVERED** | yes |
| 62 | qrcode | — | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 0/0 | — | **COVERED** | no |
| 63 | uwb | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 64 | dmx | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 65 | finger | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 66 | mini-tof-90 | distance-mm | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 67 | hbridge-v11 | adc-mv, vin-current-a | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 68 | cardkb-original | keycode, keys | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 69 | env-ii | humidity-pct, pressure-pa, temperature-c | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 3/3 | — | **COVERED** | no |
| 70 | catm | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 71 | catm-gnss | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 72 | lorawan-cn470 | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 73 | can | inject-hex | CL-A wave1 latest-firmware (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | yes |
| 74 | mini-imu-pro | acceleration-x, acceleration-y, acceleration-z, gyroscope-x, gyroscope-y, gyroscope-z, magnetic-x, magnetic-y, magnetic-z, pressure-pa, temperature-c | prior-round 2026-11-03 docs evidence | prior fw `0e4d6a47673c…` (2026-11-03) | 11/11 | — | **COVERED** | no |
| 75 | gps-v11 | baud, nmea-lines | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 76 | gps-sma | baud, nmea-lines | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 77 | mini-can | inject-hex | CL-A wave1 latest-firmware (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | yes |
| 78 | oled | contrast, display-on, inverse, start-line | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 4/4 | — | **COVERED** | no |
| 79 | mini-oled | contrast, display-on, inverse, start-line | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 4/4 | — | **COVERED** | no |
| 80 | glass2 | contrast, display-on, inverse, start-line | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 4/4 | — | **COVERED** | no |
| 81 | nbiot-cn | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 82 | lora-e220-920 | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 83 | lorawan-us915 | responses-hex | CL-A wave1 latest-firmware (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | yes |
| 84 | mic | analog-mv, comparator-level | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 85 | glass | button-states, buzzer-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 2/2 | — | **COVERED** | no |
| 86 | rf433r | input-level, sample-rate | prior-round 2026-11-03 docs evidence | prior fw `b25670b85651…` (2026-11-03) | 2/2 | — | **COVERED** | no |
| 87 | lorawan-as923 | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 88 | lorawan-eu868 | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 89 | audioplayer | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 90 | fingerprint2 | responses-hex | prior-round 2026-11-03 docs evidence | prior fw `8cf858209117…` (2026-11-03) | 1/1 | — | **COVERED** | no |
| 91 | cardkb2 | key-code, mode | CL-A wave1 latest-firmware (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/2 | mode | **PARTIAL** | yes |
| 92 | 8servos2-i2c | adc-values-hex, channel-modes-hex, input-levels-hex, pwm-hex, rgb-hex, rotary, servo-angles-hex, sys-dc-mv, sys-grove-mv, sys-ma, sys-ref-mv, timer-freq-hex, uid-hex | CL-A wave1 latest-firmware (8907) | latest fw `5847a2bcae33…` / canonical runtime | 6/13 | adc-values-hex, input-levels-hex, sys-dc-mv, sys-grove-mv, sys-ma, sys-ref-mv, timer-freq-hex | **PARTIAL** | yes |
| 93 | bmm350 | magnetic-x, magnetic-y, magnetic-z | prior-round 2026-11-03 docs evidence | prior fw `14eeda98e5c0…` (2026-11-03) | 3/3 | — | **COVERED** | no |
| 94 | ina226-10a | bus-voltage-v, current-a | prior-round 2026-11-03 docs evidence | prior fw `38e69ea96898…` (2026-11-03) | 2/2 | — | **COVERED** | no |
| 95 | rollercan | mode, target-position-deg, target-speed-rpm | prior-round 2026-11-03 docs evidence | prior fw `6076bcebaf1d…` (2026-11-03) | 3/3 | — | **COVERED** | no |
| 96 | dcssr | relay-level | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 97 | ina226-1a | bus-voltage-v, current-a | prior-round 2026-11-03 docs evidence | prior fw `cc620ec87132…` (2026-11-03) | 2/2 | — | **COVERED** | no |
| 98 | dof6 | acceleration-x, acceleration-y, acceleration-z, gyroscope-x, gyroscope-y, gyroscope-z, temperature-c | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 7/7 | — | **COVERED** | no |
| 99 | dof9 | acceleration-x, acceleration-y, acceleration-z, gyroscope-x, gyroscope-y, gyroscope-z, temperature-c | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 7/7 | — | **COVERED** | no |
| 100 | dof10 | acceleration-x, acceleration-y, acceleration-z, gyroscope-x, gyroscope-y, gyroscope-z, temperature-c | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 7/7 | — | **COVERED** | no |
| 101 | asr | responses-hex | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 1/1 | — | **COVERED** | no |
| 102 | roller485 | mode, target-position-deg, target-speed-rpm | prior-round 2026-11-03 docs evidence | prior fw `c7b25f6309be…` (2026-11-03) | 3/3 | — | **COVERED** | no |
| 103 | roller485-lite | mode, target-position-deg, target-speed-rpm | prior-round 2026-11-03 docs evidence | prior fw `5dbc6a3bfd2b…` (2026-11-03) | 3/3 | — | **COVERED** | no |
| 104 | rollercan-lite | mode, target-position-deg, target-speed-rpm | prior-round 2026-11-03 docs evidence | prior fw `aad9920e3839…` (2026-11-03) | 3/3 | — | **COVERED** | no |
| 105 | byteswitch | brightness, irq-enable, led-mode, rgb-hex, state-bitmap | latest-round units (8907) | latest fw `5847a2bcae33…` / canonical runtime | 5/5 | — | **COVERED** | no |
| 106 | bytebutton | brightness, irq-enable, led-mode, rgb-hex, state-bitmap | prior-round 2026-11-03 docs evidence | prior fw `30641e6ec218…` (2026-11-03) | 5/5 | — | **COVERED** | no |
| 107 | step16 | direction, led-brightness, led-config, position, rgb, rgb-brightness, rgb-power | CL-A wave1 latest-firmware (8907) | latest fw `5847a2bcae33…` / canonical runtime | 4/7 | led-config, rgb-brightness, rgb-power | **PARTIAL** | yes |
| 108 | timerpwr | backlight, battery-i-ma, battery-mv, charging, cycle, grove-i, grove-output, grove-v, schedule-off, schedule-on, trigger-bits, usb-i, usb-v | CL-A wave1 latest-firmware (8907) | latest fw `5847a2bcae33…` / canonical runtime | 3/13 | backlight, battery-i-ma, cycle, grove-i, grove-output, grove-v, schedule-off, schedule-on, trigger-bits, usb-i | **PARTIAL** | yes |
| 109 | mq | heat-high, heat-low, led, mq-mode, ntc-mv, ntc-ohm, ref-mv, sensor-mv, valid-tags | CL-A wave1 latest-firmware (8907) | latest fw `5847a2bcae33…` / canonical runtime | 8/9 | ntc-mv | **PARTIAL** | yes |
| 110 | 8servos2-chain | adc-values, channel-modes, current-ma | prior-round 2026-11-03 docs evidence | prior fw `3b1fe77ec918…` (2026-11-03) | 3/3 | — | **COVERED** | no |
| 111 | cat1-cn | responses-hex | prior-round 2026-11-03 docs evidence | prior fw `0162397ca202…` (2026-11-03) | 1/1 | — | **COVERED** | no |
| 112 | chainbus | adc-values, chain-uid, gpio-levels | prior-round 2026-11-03 docs evidence | prior fw `7303abc17b7f…` (2026-11-03) | 3/3 | — | **COVERED** | no |

## PARTIAL Units — field-level evidence gaps

All PARTIAL Units come from prior-round (2026-11-03) official-driver reports; their declared
writable input surface is broader than what those probes injected. The remaining Units of
batch11/12a/12b/12c are being re-executed on latest firmware by the U1/U2 lanes this round
(`.work/uiflow-latest-20261105/round2/units/U1|U2`); those re-runs repeat the same probe vectors, so
they do not by themselves close the field-level gaps listed here.

### cardkb2

- evidence: CL-A wave1 latest-firmware (8907) — `.work/uiflow-latest-20261105/round2/closedloop/input/waves/w2/cardkb2/cardkb2/result.json`
- covered injected→readback fields: key-code
- **missing** `mode`: no injected 'mode' fixture in report; probe only reads FW version register; BLE HID/ESP-NOW modes NOT RUN
- note: UART AA03 v2 report mode fixed in probe; I2C key path only

### 8servos2-i2c

- evidence: CL-A wave1 latest-firmware (8907) — `.work/uiflow-latest-20261105/round2/closedloop/input/waves/w2/8servos2-i2c/8servos2-i2c/result.json`
- covered injected→readback fields: channel-modes-hex, pwm-hex, rgb-hex, rotary, servo-angles-hex, uid-hex
- **missing** `adc-values-hex`: not injected/read in probe
- **missing** `input-levels-hex`: not injected/read
- **missing** `sys-dc-mv`: not injected/read
- **missing** `sys-grove-mv`: not injected/read
- **missing** `sys-ma`: not injected/read
- **missing** `sys-ref-mv`: not injected/read
- **missing** `timer-freq-hex`: not injected/read
- note: writable registers in catalog are broader than the batch12a probe; needs extended official-driver probe

### step16

- evidence: CL-A wave1 latest-firmware (8907) — `.work/uiflow-latest-20261105/round2/closedloop/input/waves/w2/step16/step16/result.json`
- covered injected→readback fields: direction, led-brightness, position, rgb
- **missing** `led-config`: ST_LED_DEFAULT 254 50 read only; no injection
- **missing** `rgb-brightness`: not injected
- **missing** `rgb-power`: not injected
- note: probe only injects position; LED/RGB power writable inputs unexercised

### timerpwr

- evidence: CL-A wave1 latest-firmware (8907) — `.work/uiflow-latest-20261105/round2/closedloop/input/waves/w2/timerpwr/timerpwr/result.json`
- covered injected→readback fields: battery-mv, charging, usb-v
- **missing** `backlight`: readback only, no injection
- **missing** `battery-i-ma`: not injected (raw 00000000)
- **missing** `cycle`: not injected
- **missing** `grove-i`: not injected
- **missing** `grove-output`: readback only, no injection
- **missing** `grove-v`: not injected
- **missing** `schedule-off`: not injected
- **missing** `schedule-on`: not injected (schedule readback 0c2200 is default)
- **missing** `trigger-bits`: not injected
- **missing** `usb-i`: not injected
- note: only 3 of 13 declared inputs were host-injected by batch12a probe; other writable fields unexercised

### mq

- evidence: CL-A wave1 latest-firmware (8907) — `.work/uiflow-latest-20261105/round2/closedloop/input/waves/w2/mq/mq/result.json`
- covered injected→readback fields: heat-high, heat-low, led, mq-mode, ntc-ohm, ref-mv, sensor-mv, valid-tags
- **missing** `ntc-mv`: derived from ntc-ohm by driver; direct ntc-mv not injected
- note: valid-tag semantic conflict (driver says 1=valid, protocol PDF says 0) recorded UNRESOLVED in report

## Retried / load-affected round-2 runs

Lead instruction at 17:35 throttled CL-A to 1 concurrent guest; load-induced timeouts are retried
once and recorded as `INFRA-LOAD` in `round2_fresh/run-status.jsonl`.

- `ncir2`: attempt 2 status=FAIL classification=INFRA-LOAD

## Not covered / caveats

- Queue Units with no model/driver at all: **none** — all 112 have runtime `implemented` models and
  official-driver evidence (see `NOT-RUN.md` for the exact residual list).
- Prior-round evidence is bound to earlier firmware images (different base SHA-256) and a different
  runtime binary; it is labelled `prior-round` above and must not be transferred to the latest
  firmware as a new PASS. Latest-round re-execution for those Units is owned by the U1/U2 lanes.
- CAN/LoRaWAN: frame/UART byte layer only; electrical/transceiver/termination/bit-timing
  (CAN) and RF/join/OTAA/ABP/duty-cycle/FCC (LoRaWAN) are NOT RUN (see per-report boundaries).
- All results are virtual-device validation, not physical hardware.
