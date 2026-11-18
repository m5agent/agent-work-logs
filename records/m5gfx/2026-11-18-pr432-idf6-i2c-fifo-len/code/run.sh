#!/bin/bash
# Rebuild the code-level check for M5GFX #432 from a local clone.
#
#   ./run.sh <M5GFX clone> [base ref] [head ref]
#
# Default refs: base 452c15b (develop when the PR was reviewed), head c90dda6 (the PR).
# Prints everything to stdout; the recorded output is ../evidence/host-harness-output.txt
# and ../evidence/write-chunk-sim.txt.
set -eu
SRC=${1:?usage: run.sh <M5GFX clone> [base ref] [head ref]}
BASE=${2:-452c15bc982af0b54acf567a79e7eb6066ace9e5}
HEAD=${3:-c90dda61ae3718ea90f48c249055d38698e1f1f6}
HERE=$(cd "$(dirname "$0")" && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

CXX=${CXX:-clang++}
FLAGS=${FLAGS:--std=c++17 -Wall -Wextra -Werror -O1}

echo "# source: $SRC"
echo "# base:   $BASE"
echo "# head:   $HEAD"
echo "# compiler: $($CXX --version | head -1)"
echo "# flags:  $FLAGS"
echo

git -C "$SRC" show "$BASE:src/lgfx/v1/platforms/esp32/common.inl" > "$TMP/base.inl"
git -C "$SRC" show "$HEAD:src/lgfx/v1/platforms/esp32/common.inl" > "$TMP/head.inl"
python3 "$HERE/extract_fifo_fn.py" "$TMP/base.inl" "$HERE/base_fn.inc"
python3 "$HERE/extract_fifo_fn.py" "$TMP/head.inl" "$HERE/pr_fn.inc"
echo "# extracted getFifoLen(): $(wc -l < "$HERE/pr_fn.inc") lines (head), $(wc -l < "$HERE/base_fn.inc") lines (base)"
echo

# Scenario macro sets, each copied from probe-macros.sh output:
#   C5/C6 on 6.x: LGFX_LP_I2C_NUM=1, low power port index 1, I2C_LL_FIFO_LEN 32 / LP 16
#   P4    on 6.x: two high power ports, low power port index 2, same depths
#   C2    on 6.x: no low power port, I2C_LL_FIFO_LEN 16
#   C6    on 5.x: SOC_I2C_FIFO_LEN 32 / SOC_LP_I2C_FIFO_LEN 16
#   ESP32 on 5.x: SOC_I2C_FIFO_LEN 32, no low power port
run_case() { # name hp_ports has_lp exp_hp exp_lp defs use_pr
  name=$1 hp=$2 haslp=$3 ehp=$4 elp=$5 defs=${6:-} use_pr=${7:-}
  if ! $CXX $FLAGS -I"$HERE" -o "$TMP/bin_$name" "$HERE/fifo_harness.cpp" \
        -DHP_PORTS="$hp" -DHAS_LP="$haslp" -DEXP_HP="$ehp" -DEXP_LP="$elp" $defs $use_pr; then
    echo "-- $name: COMPILE FAILURE"; return
  fi
  echo "-- $name"
  "$TMP/bin_$name" || echo "   MISMATCH"
}

C6_6X='-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=1 -DI2C_LL_FIFO_LEN=32 -DI2C_LL_LP_FIFO_LEN=16'
P4_6X='-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=2 -DI2C_LL_FIFO_LEN=32 -DI2C_LL_LP_FIFO_LEN=16'
C2_6X='-DLGFX_LP_I2C_NUM=0 -DI2C_LL_FIFO_LEN=16'
C6_5X='-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=1 -DSOC_I2C_FIFO_LEN=32 -DSOC_LP_I2C_FIFO_LEN=16'
ESP32_5X='-DLGFX_LP_I2C_NUM=0 -DSOC_I2C_FIFO_LEN=32'

echo "## PR head (values expected from the 6.x / 5.x headers)"
run_case pr_c6_603     1 1 32 16 "$C6_6X"    -DUSE_PR
run_case pr_p4_603     2 1 32 16 "$P4_6X"    -DUSE_PR
run_case pr_c2_603     1 0 16 0  "$C2_6X"    -DUSE_PR
run_case pr_c6_554     1 1 32 16 "$C6_5X"    -DUSE_PR
run_case pr_esp32_554  1 0 32 0  "$ESP32_5X" -DUSE_PR
echo
echo "## base develop (the reported behaviour)"
run_case base_c6_603   1 1 32 32 "$C6_6X"
run_case base_c2_603   1 0 32 0  "$C2_6X"
run_case base_c6_554   1 1 32 16 "$C6_5X"
echo
echo "## write chunking (first-chunk arithmetic of writeBytes)"
$CXX $FLAGS -o "$TMP/chunk" "$HERE/write_chunk_sim.cpp" && "$TMP/chunk"
