#!/usr/bin/env bash
# Rebuild the host harness for M5Unit-8Encoder issue 7 against the pre-fix and
# post-fix sources, then print the observed Wire.begin() frequency.
#
#   ./reproduce.sh [workdir]
#
# Requires: git, g++ (or clang++). No Arduino core or hardware needed.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="${1:-$(mktemp -d)}"
SRC="$WORK/M5Unit-8Encoder"

if [ ! -d "$SRC/.git" ]; then
  git clone --quiet https://github.com/m5stack/M5Unit-8Encoder.git "$SRC"
fi
cd "$SRC"
git fetch --quiet origin

mkdir -p "$WORK/fixed" "$WORK/prefix"
git show 7447df753d:src/UNIT_8ENCODER.h    > "$WORK/fixed/UNIT_8ENCODER.h"
git show 7447df753d:src/UNIT_8ENCODER.cpp  > "$WORK/fixed/UNIT_8ENCODER.cpp"
git show 59a8a0a:src/UNIT_8ENCODER.h       > "$WORK/prefix/UNIT_8ENCODER.h"
git show 59a8a0a:src/UNIT_8ENCODER.cpp     > "$WORK/prefix/UNIT_8ENCODER.cpp"

CXX="${CXX:-g++}"
echo "==> pre-fix header (59a8a0a)"
"$CXX" -std=c++17 -Wall -I "$HERE/include" -I "$WORK/prefix" \
  "$WORK/prefix/UNIT_8ENCODER.cpp" "$HERE/harness.cpp" -o "$WORK/harness_prefix"
"$WORK/harness_prefix"

echo "==> post-fix header (7447df753d)"
"$CXX" -std=c++17 -Wall -I "$HERE/include" -I "$WORK/fixed" \
  "$WORK/fixed/UNIT_8ENCODER.cpp" "$HERE/harness.cpp" -o "$WORK/harness_fixed"
"$WORK/harness_fixed"

echo "==> workdir: $WORK"
