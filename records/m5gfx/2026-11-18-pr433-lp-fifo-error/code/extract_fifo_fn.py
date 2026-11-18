#!/usr/bin/env python3
"""Extract isLpPort() + getFifoLen() verbatim from an M5GFX common.inl.

Usage: extract_fifo_fn.py <common.inl> <out.inc>

The functions are copied as-is (comments included) so the harness compiles exactly the
code under review, not a paraphrase of it.
"""
import pathlib
import sys


def grab(path: str) -> str:
    lines = pathlib.Path(path).read_text().splitlines()
    start = next(i for i, l in enumerate(lines) if "static inline bool isLpPort" in l)
    fn = next(i for i, l in enumerate(lines) if "static inline uint32_t getFifoLen" in l)
    depth = 0
    started = False
    for j in range(fn, len(lines)):
        depth += lines[j].count("{") - lines[j].count("}")
        if "{" in lines[j]:
            started = True
        if started and depth == 0:
            return "\n".join(lines[start:j + 1]) + "\n"
    raise SystemExit("unterminated getFifoLen")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    pathlib.Path(sys.argv[2]).write_text(grab(sys.argv[1]))
