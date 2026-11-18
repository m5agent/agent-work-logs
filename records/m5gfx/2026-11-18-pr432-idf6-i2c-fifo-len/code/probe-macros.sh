#!/bin/bash
# Where does each ESP-IDF release keep the I2C FIFO depth macros?
#
# Reads soc/soc_caps.h and hal/i2c_ll.h straight out of the upstream repository for
# every (ref, chip) pair and prints one TSV row per pair:
#   ref  chip  soc_caps path  SOC_I2C_FIFO_LEN  SOC_LP_I2C_FIFO_LEN  i2c_ll path  I2C_LL_FIFO_LEN  I2C_LL_LP_FIFO_LEN
# "-" means the header or the macro is absent for that ref/chip.
#
# IDF 6.0 moved the HAL per peripheral, so hal/i2c_ll.h lives under
# components/esp_hal_i2c/<chip>/include/ from then on; 5.x keeps components/hal/<chip>/.
set -u
BASE=https://raw.githubusercontent.com/espressif/esp-idf

probe_ref() {
  ref=$1; shift
  for chip in "$@"; do
    soc=$(curl -sf --max-time 25 "$BASE/$ref/components/soc/$chip/include/soc/soc_caps.h") || soc=
    ll=$(curl -sf --max-time 25 "$BASE/$ref/components/esp_hal_i2c/$chip/include/hal/i2c_ll.h") || ll=
    if [ -n "$ll" ]; then
      ll_path="components/esp_hal_i2c/$chip/include/hal/i2c_ll.h"
    else
      ll=$(curl -sf --max-time 25 "$BASE/$ref/components/hal/$chip/include/hal/i2c_ll.h") || ll=
      ll_path="components/hal/$chip/include/hal/i2c_ll.h"
    fi
    if [ -z "$soc" ]; then printf "%s\t%s\tMISSING\t-\t-\t-\t-\t-\n" "$ref" "$chip"; continue; fi
    s1=$(printf '%s\n' "$soc" | grep -o 'SOC_I2C_FIFO_LEN[[:space:]]*([0-9]*)' | head -1 | sed 's/.*(\([0-9]*\)).*/\1/')
    s2=$(printf '%s\n' "$soc" | grep -o 'SOC_LP_I2C_FIFO_LEN[[:space:]]*([0-9]*)' | head -1 | sed 's/.*(\([0-9]*\)).*/\1/')
    l1=$(printf '%s\n' "$ll" | grep -o 'define I2C_LL_FIFO_LEN[[:space:]]*[0-9]*' | head -1 | awk '{print $NF}')
    l2=$(printf '%s\n' "$ll" | grep -o 'define I2C_LL_LP_FIFO_LEN[[:space:]]*[0-9]*' | head -1 | awk '{print $NF}')
    printf "%s\t%s\tcomponents/soc/%s/include/soc/soc_caps.h\t%s\t%s\t%s\t%s\t%s\n" \
      "$ref" "$chip" "$chip" "${s1:--}" "${s2:--}" "$ll_path" "${l1:--}" "${l2:--}"
  done
}

# Pairs that matter for this change: the two chips with a low power I2C port (plus the
# P4's second high power port), the C2 whose only port is a 16 deep FIFO, and the
# classic ESP32 as the 32 deep reference. 5.3 has no C5 support.
probe_ref v5.3     esp32 esp32c2 esp32c6 esp32p4
probe_ref v5.4.3   esp32 esp32c2 esp32c5 esp32c6 esp32p4
probe_ref v5.5.4   esp32 esp32c2 esp32c5 esp32c6 esp32p4
probe_ref v6.0     esp32 esp32c2 esp32c5 esp32c6 esp32p4
probe_ref v6.0.3   esp32 esp32c2 esp32c5 esp32c6 esp32p4
probe_ref v6.1.1   esp32 esp32c2 esp32c5 esp32c6 esp32p4
probe_ref v6.3-dev esp32c5 esp32c6
