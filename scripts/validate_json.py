#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate JSON against a JSON Schema (optional jsonschema)")
    ap.add_argument("--schema", required=True)
    ap.add_argument("--json", required=True)
    args = ap.parse_args()
    try:
        import jsonschema  # type: ignore
        with open(args.schema, "r", encoding="utf-8") as f:
            schema = json.load(f)
        with open(args.json, "r", encoding="utf-8") as f:
            payload = json.load(f)
        jsonschema.validate(instance=payload, schema=schema)
        print(json.dumps({"valid": True, "json": args.json, "schema": args.schema}))
    except Exception as e:
        print(json.dumps({"valid": False, "error": str(e)}))
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
