#!/usr/bin/env python3
"""Record-version wrapper to reuse the checked-in api_sweep run_guest.run().

Only the CLI device restriction of the checked-in runner is bypassed (it lists
cores3/cardputer-adv/stopwatch/sticks3/core2); image composition, the visible
Device Service session, evidence-before-stop and purge=0 are the checked-in
implementation. The executed copy hardcoded the emulator checkout; this copy
takes --repo-root so it stays reproducible outside the author's machine.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--api", required=True)
    parser.add_argument("--token-file", required=True, type=Path)
    parser.add_argument("--device", required=True)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--done-marker", required=True)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--prepare-timeout", type=int, default=600)
    parser.add_argument("--ready-timeout", type=int, default=180)
    parser.add_argument("--runtime", default="qemu")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    sys.path[:0] = [
        str(root / "tests/uiflow2"),
        str(root / "tests/uiflow2/api_sweep"),
        str(root / "tests/firmware/core2_startup"),
        str(root / "platform/tools"),
    ]
    import run_guest  # noqa: E402

    namespace = argparse.Namespace(
        api=args.api,
        token_file=args.token_file,
        device=args.device,
        runtime=args.runtime,
        source=args.source,
        append_code=None,
        base_image=None,
        expected_base_sha256=None,
        fixture_dir=None,
        out_dir=args.out_dir,
        done_marker=args.done_marker,
        timeout=args.timeout,
        prepare_timeout=args.prepare_timeout,
        ready_timeout=args.ready_timeout,
        program_transport=None,
        uart_repl_bootstrap=None,
        runtime_env=None,
        units=None,
        network=None,
        keep_session=False,
    )
    return run_guest.run(namespace)


if __name__ == "__main__":
    raise SystemExit(main())
