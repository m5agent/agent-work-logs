#!/bin/sh
# Rebuild the userspace FSM harness from the recorded sources.
set -e
cd "$(dirname "$0")"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT INT TERM
mkdir -p "$tmp/stub/linux"
cp stub/linux/*.h "$tmp/stub/linux/"
cp harness.c harness_pre_fix.c residual.c "$tmp/"

build() { # $1=fsm source  $2=harness  $3=output binary
	cp "$1" "$tmp/tca8418_fsm.c"
	gcc -Wall -Wextra -std=gnu99 -I "$tmp/stub" -I "$tmp" -o "$3" "$tmp/$2"
}
build fsm_pr_head.c              harness.c        /tmp/h_pr
build fsm_pre_fix.c              harness_pre_fix.c /tmp/h_pre
build fsm_pr_head.c              residual.c       /tmp/r_pr
build fsm_pr_head_timeout_guard.c residual.c      /tmp/r_guard

echo "### pre-fix main"; /tmp/h_pre
echo "### PR head e7f7a18"; /tmp/h_pr
echo "### residual case, PR head"; /tmp/r_pr
echo "### residual case, PR head + WAIT timeout guard"; /tmp/r_guard
