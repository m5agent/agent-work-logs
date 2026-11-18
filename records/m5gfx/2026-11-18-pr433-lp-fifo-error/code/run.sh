#!/bin/bash
# Rebuild the code-level check for M5GFX #433 from a local clone.
#
#   ./run.sh <M5GFX clone> [base ref] [head ref]
#
# Default refs: base e88846e (develop = merge of #432), head 99eb30e (the PR).
# Recorded output: ../evidence/host-harness-output.txt
set -u
SRC=${1:?usage: run.sh <M5GFX clone> [base ref] [head ref]}
BASE=${2:-e88846e781091ff489de3afb5770f7333af1d864}
HEAD=${3:-99eb30e815438bc01bd2a114992db5c0e076acd4}
HERE=$(cd "$(dirname "$0")" && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

CXX=${CXX:-clang++}
FLAGS=${FLAGS:--std=c++17 -Wall -Wextra -Werror -O1}
# isLpPort() is used elsewhere in the real file, so it is "unused" in this extract only
# for chips without an LP port.
NOUNUSED=-Wno-unused-function

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
echo "# extracted isLpPort()+getFifoLen(): $(wc -l < "$HERE/pr_fn.inc") lines (head), $(wc -l < "$HERE/base_fn.inc") lines (base)"
echo

# name hp_ports has_lp exp_hp exp_lp defs [extra]
run_case() {
  name=$1 hp=$2 haslp=$3 ehp=$4 elp=$5 defs=${6:-} extra=${7:-}
  if ! $CXX $FLAGS -I"$HERE" -o "$TMP/bin_$name" "$HERE/fifo_harness.cpp" \
        -DHP_PORTS="$hp" -DHAS_LP="$haslp" -DEXP_HP="$ehp" -DEXP_LP="$elp" $defs $extra 2> "$TMP/err_$name"; then
    echo "-- $name: COMPILE FAILURE"; sed -n 1,3p "$TMP/err_$name"; return; fi
  echo "-- $name"
  "$TMP/bin_$name" || echo "   MISMATCH"
}

# A configuration with an LP port but neither depth macro: the PR must refuse to build.
run_expect_error() {
  name=$1; shift
  if $CXX $FLAGS -I"$HERE" -o "$TMP/bin_$name" "$HERE/fifo_harness.cpp" \
        -DHP_PORTS=1 -DHAS_LP=1 -DEXP_HP=32 -DEXP_LP=16 "$@" 2> "$TMP/err_$name"; then
    echo "-- $name: UNEXPECTEDLY BUILT"; "$TMP/bin_$name"; return; fi
  echo "-- $name: build stopped"
  grep -E "error" "$TMP/err_$name" | head -2 | sed 's/^/   /'
}

C6_6X='-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=1 -DI2C_LL_FIFO_LEN=32 -DI2C_LL_LP_FIFO_LEN=16'
P4_6X='-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=2 -DI2C_LL_FIFO_LEN=32 -DI2C_LL_LP_FIFO_LEN=16'
C2_6X='-DLGFX_LP_I2C_NUM=0 -DI2C_LL_FIFO_LEN=16'
ESP32_6X='-DLGFX_LP_I2C_NUM=0 -DI2C_LL_FIFO_LEN=32'
C6_5X='-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=1 -DSOC_I2C_FIFO_LEN=32 -DSOC_LP_I2C_FIFO_LEN=16'
P4_5X='-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=2 -DSOC_I2C_FIFO_LEN=32 -DSOC_LP_I2C_FIFO_LEN=16'
ESP32_5X='-DLGFX_LP_I2C_NUM=0 -DSOC_I2C_FIFO_LEN=32'
# LP port, HP depth macro only: this is the "depth renamed again" case.
UNKNOWN_5X='-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=1 -DSOC_I2C_FIFO_LEN=32'
UNKNOWN_6X='-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=1 -DI2C_LL_FIFO_LEN=32'

echo "## released configurations (head must give the 5.x/6.x header values)"
run_case head_c6_6x   1 1 32 16 "$C6_6X"
run_case head_p4_6x   2 1 32 16 "$P4_6X"
run_case head_c2_6x   1 0 16 0  "$C2_6X"    $NOUNUSED
run_case head_esp32_6x 1 0 32 0 "$ESP32_6X" $NOUNUSED
run_case head_c6_5x   1 1 32 16 "$C6_5X"
run_case head_p4_5x   2 1 32 16 "$P4_5X"
run_case head_esp32_5x 1 0 32 0 "$ESP32_5X" $NOUNUSED
echo
echo "## same configurations on base (must be identical: this PR changes no compiled code)"
run_case base_c6_6x   1 1 32 16 "$C6_6X"
run_case base_p4_6x   2 1 32 16 "$P4_6X"
run_case base_c2_6x   1 0 16 0  "$C2_6X"    $NOUNUSED
run_case base_esp32_6x 1 0 32 0 "$ESP32_6X" $NOUNUSED
run_case base_c6_5x   1 1 32 16 "$C6_5X"
run_case base_p4_5x   2 1 32 16 "$P4_5X"
run_case base_esp32_5x 1 0 32 0 "$ESP32_5X" $NOUNUSED
echo
echo "## LP port with no depth macro (synthetic rename of the depth macro)"
echo "-- base: falls back to the HP depth without a word"
run_case base_unknown_5x 1 1 32 32 "$UNKNOWN_5X"
echo "-- head: build must stop"
run_expect_error head_unknown_5x $UNKNOWN_5X -DUSE_PR
run_expect_error head_unknown_6x $UNKNOWN_6X -DUSE_PR
