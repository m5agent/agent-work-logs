# Host harness for the Chain ENV / DLight / IMU components

`emulate.py` opens a pseudo-terminal, substitutes its slave path into the
`uart.port` of the given YAML, builds the ESPHome host target, runs the
executable and acts as the Chain nodes on the other end of the wire:

- answers the configuration commands with operation status 1;
- answers `GET_AHT20`, `GET_SPA06`, `GET_LUX`, `GET_ACCEL`, `GET_GYRO`,
  `GET_TEMPERATURE` with fixed synthetic readings;
- injects `0xE0` event reports at scripted times (`noevents` disables them).

This is a host build plus a simulated peripheral, not a virtual M5Stack device:
the ESP32 chain firmware and the physical sensor are not exercised.

Requirements: ESPHome 2026.11.0-dev checkout of `m5stack/esphome` at the commit
under review, installed in a Python >= 3.12 environment, plus `host` platform
support. Point `ESPHOME_BIN` at that environment's `esphome`.

`host.yaml` is the full three-node configuration (sensors + alarms);
`host-alarmonly.yaml` keeps only one alarm per node and no sensor entities.
