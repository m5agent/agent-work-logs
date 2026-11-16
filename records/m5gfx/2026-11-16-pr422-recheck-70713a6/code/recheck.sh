#!/bin/sh
# Compare the two PR #422 hunks in the two ESP_LOG argument modes.
# usage: sh recheck.sh <repo-root> <master-ref> <head-ref>
set -eu
root=$1; base=$2; head=$3
work=$(mktemp -d "${TMPDIR:-/tmp}/m5gfx-recheck.XXXXXX")
trap 'rm -rf "$work"' EXIT HUP INT TERM
cat > "$work/discard_io.hpp" <<'HPP'
#pragma once
#include "support/native_devices_io.hpp"
#undef ESP_LOGE
#undef ESP_LOGW
#undef ESP_LOGI
#undef ESP_LOGD
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGD(...) ((void)0)
HPP
for ref in "$base" "$head"; do
  tree="$work/$ref"
  git -C "$root" worktree add -q --detach "$tree" "$ref"
  for cfg in expanded discarded; do
    rm -rf "$work/out"; mkdir -p "$work/out"
    fails=0
    if [ "$cfg" = expanded ]; then extra="-include $tree/test/board_detect/support/native_devices_io.hpp"
    else extra="-include $work/discard_io.hpp"; fi
    for src in "$tree"/test/board_detect/*.cpp; do
      name=$(basename "$src" .cpp)
      ${CXX:-c++} -std=c++11 -O2 -Wall -Wextra -Wno-unused-function -Wno-unused-parameter -pedantic \
        '-DM5GFX_BOARD_DETECT_IO_HEADER="support/detect_io.hpp"' $extra \
        -I"$tree/test/board_detect" -I"$tree/src" "$src" -o "$work/out/$name" \
        2>> "$work/$ref-$cfg.log" || fails=$((fails+1))
    done
    tx=$(grep -c 'transaction.inl.*warning:' "$work/$ref-$cfg.log" 2>/dev/null || true)
    dr=$(grep -c 'detector_runner.inl.*warning:' "$work/$ref-$cfg.log" 2>/dev/null || true)
    echo "ref=$ref cfg=$cfg compile_failures=$fails transaction_warnings=$tx detector_runner_warnings=$dr"
    grep -E 'transaction\.inl.*warning:|detector_runner\.inl.*warning:' "$work/$ref-$cfg.log" 2>/dev/null | sed "s#$tree/##" | sort -u | sed 's/^/    /' || true
  done
  git -C "$root" worktree remove --force "$tree"
done
