#!/usr/bin/env bash
# Run in an empty directory with ESP-IDF v5.4.2 activated.
set -euo pipefail
idf.py create-project-from-example 'espressif/esp_hosted==2.0.13:slave'
cd slave
printf '\n# CONFIG_BT_ENABLED is not set\n' >> sdkconfig.defaults.esp32c6
idf.py set-target esp32c6 build
grep -qx '# CONFIG_BT_ENABLED is not set' sdkconfig
grep -qx 'CONFIG_ESP_SDIO_HOST_INTERFACE=y' sdkconfig
grep -qx '2.0.13' main/coprocessor_fw_version.txt
