#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path


def strip_control_chars(s: str) -> str:
    # Remove all Cc (Other, Control) except standard whitespace we keep explicitly
    return "".join(
        ch for ch in s
        if ch in ("\n", "\r", "\t") or unicodedata.category(ch) != "Cc"
    )


def sanitize_file(src: Path, dst: Path | None, in_place: bool) -> None:
    text = src.read_text(encoding="utf-8", errors="replace")
    cleaned = strip_control_chars(text)
    target = src if in_place or dst is None else dst
    target.write_text(cleaned, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Sanitize NDJSON: remove stray control characters")
    ap.add_argument("path", help="Input NDJSON/JSONL file path")
    ap.add_argument("--out", default=None, help="Optional output path; defaults to in-place if not set and --in-place is given")
    ap.add_argument("--in-place", action="store_true", help="Overwrite the input file")
    args = ap.parse_args()

    src = Path(args.path)
    if not src.exists():
        print(f"Missing file: {src}")
        sys.exit(2)
    dst = Path(args.out) if args.out else None
    sanitize_file(src, dst, in_place=bool(args.in_place))
    print({"sanitized": str(dst or src)})


if __name__ == "__main__":
    main()
