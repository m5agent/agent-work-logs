#!/bin/bash
# Survey SOC_LP_I2C_NUM / SOC_LP_I2C_FIFO_LEN (soc_caps.h) and I2C_LL_LP_FIFO_LEN
# (hal/i2c_ll.h) for the ESP-IDF tags that decided when the LP I2C port is usable and
# where its FIFO depth is named. Chips: the ones with an LP I2C port in any tag, plus
# ESP32 / C2 as the no-LP reference.
# Usage: bash probe-lp-macros.sh > out.tsv
set -u
TAGS="v5.4.1 v5.4.2 v5.4.3 v5.5.1 v5.5.2 v5.5.3 v5.5.4 v6.0 v6.0.1 v6.0.2 v6.0.3 v6.1.1 master v6.3-dev"
CHIPS="esp32 esp32c2 esp32c5 esp32c6 esp32c61 esp32h4 esp32p4 esp32s31"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

fetch() { # tag dir path
  local t=$1 d=$2 p=$3
  curl -sfL "https://raw.githubusercontent.com/espressif/esp-idf/$t/$p" -o "$d/$(echo "$p" | tr '/' '_')" \
    || echo "FAIL $t $p" >> "$d/failed"
}
export -f fetch

printf "tag\tchip\tSOC_LP_I2C_NUM\tSOC_LP_I2C_FIFO_LEN\tI2C_LL_LP_FIFO_LEN\ti2c_ll_path\n"
for t in $TAGS; do
  d="$WORK/$t"; mkdir -p "$d"
  gh api "repos/espressif/esp-idf/git/trees/$t?recursive=1" --jq '.tree[].path' 2>/dev/null > "$d/paths"
  grep -E "soc_caps\.h$|i2c_ll\.h$" "$d/paths" | grep -v "/linux/" > "$d/allfiles"
  : > "$d/files"
  for c in $CHIPS; do
    grep -E "/$c/include/(soc/soc_caps|hal/i2c_ll)\.h$" "$d/allfiles" >> "$d/files"
  done
  xargs -P 8 -I{} bash -c 'fetch "$@"' _ "$t" "$d" {} < "$d/files"
  for c in $CHIPS; do
    f="$d/$(echo "components/soc/$c/include/soc/soc_caps.h" | tr '/' '_')"
    [ -e "$f" ] || { printf "%s\t%s\t(source missing)\t-\t-\t-\n" "$t" "$c"; continue; }
    num=$(grep -E "define SOC_LP_I2C_NUM " "$f" | sed -E 's/.*define SOC_LP_I2C_NUM +//;s/[[:space:]]*(\/\/|\/\*).*//;s/[[:space:]]+$//')
    fifo=$(grep -E "define SOC_LP_I2C_FIFO_LEN " "$f" | sed -E 's/.*define SOC_LP_I2C_FIFO_LEN +//;s/[[:space:]]*(\/\/|\/\*).*//;s/[[:space:]]+$//')
    llp=$(grep -m1 "/$c/include/hal/i2c_ll\.h$" "$d/files")
    ll="-"
    if [ -n "${llp:-}" ]; then
      lf="$d/$(echo "$llp" | tr '/' '_')"
      ll=$(grep -E "define I2C_LL_LP_FIFO_LEN " "$lf" | sed -E 's/.*define I2C_LL_LP_FIFO_LEN +//;s/[[:space:]]*(\/\/|\/\*).*//;s/[[:space:]]+$//')
      ll=${ll:--}
    else
      llp="-"
    fi
    printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$t" "$c" "${num:--}" "${fifo:--}" "$ll" "${llp:--}"
  done
  [ -e "$d/failed" ] && sed 's/^/download-failed: /' "$d/failed" >&2
done
