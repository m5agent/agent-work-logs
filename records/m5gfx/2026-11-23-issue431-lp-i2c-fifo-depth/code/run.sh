set -u
CC=${CXX:-g++}
declare -a CFG=(
 "idf61_c5|-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=1 -DI2C_LL_FIFO_LEN=32 -DI2C_LL_LP_FIFO_LEN=16"
 "idf61_c6|-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=1 -DI2C_LL_FIFO_LEN=32 -DI2C_LL_LP_FIFO_LEN=16"
 "idf61_p4|-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=2 -DI2C_LL_FIFO_LEN=32 -DI2C_LL_LP_FIFO_LEN=16"
 "idf61_c2|-DLGFX_LP_I2C_NUM=0 -DI2C_LL_FIFO_LEN=16"
 "idf61_esp32|-DLGFX_LP_I2C_NUM=0 -DI2C_LL_FIFO_LEN=32"
 "idf554_c5|-DLGFX_LP_I2C_NUM=1 -DLGFX_LP_I2C_PORT=1 -DSOC_I2C_FIFO_LEN=32 -DSOC_LP_I2C_FIFO_LEN=16"
 "idf554_esp32|-DLGFX_LP_I2C_NUM=0 -DSOC_I2C_FIFO_LEN=32"
)
for v in base head; do
  echo "==== $v ===="
  for entry in "${CFG[@]}"; do
    name=${entry%%|*}; flags=${entry#*|}
    bin=bin_${v}_${name}
    if $CC -std=c++17 -Wall -Wextra -Werror -O0 $flags main_$v.cpp -o $bin 2>err_${v}_${name}.txt; then
      printf '%-12s ' "$name"; ./$bin | head -1
    else
      printf '%-12s COMPILE-FAIL: %s\n' "$name" "$(head -1 err_${v}_${name}.txt)"
    fi
  done
done
