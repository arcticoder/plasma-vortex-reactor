#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import struct

MAGIC = b"TLNB"  # Timeline Binary magic
VERSION = 1


def encode_record(obj: dict) -> bytes:
    data = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    return struct.pack(">4sBI", MAGIC, VERSION, len(data)) + data


def decode_stream(fp) -> list[dict]:
    out = []
    while True:
        header = fp.read(4 + 1 + 4)
        if not header:
            break
        magic, ver, n = struct.unpack(">4sBI", header)
        if magic != MAGIC or ver != VERSION:
            raise ValueError("invalid header")
        payload = fp.read(n)
        out.append(json.loads(payload.decode("utf-8")))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert NDJSON timeline to a simple binary format and back")
    ap.add_argument("--ndjson", default=None, help="Input NDJSON path (for encode)")
    ap.add_argument("--bin", default=None, help="Binary output path")
    ap.add_argument("--decode", default=None, help="Binary input path to decode back to JSONL")
    args = ap.parse_args()
    if args.ndjson and args.bin:
        with open(args.ndjson, "r", encoding="utf-8") as fi, open(args.bin, "wb") as fo:
            for line in fi:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                fo.write(encode_record(obj))
        print(json.dumps({"wrote": args.bin}))
        return
    if args.decode:
        with open(args.decode, "rb") as fi:
            obj_list = decode_stream(fi)
        out = (args.decode + ".jsonl")
        with open(out, "w", encoding="utf-8") as fo:
            for obj in obj_list:
                fo.write(json.dumps(obj) + "\n")
        print(json.dumps({"wrote": out}))
        return
    ap.print_help()


if __name__ == "__main__":
    main()
