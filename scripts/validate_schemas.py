#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate integrated_report.json and production_kpi.json against local schemas if present.")
    ap.add_argument("--integrated", default="integrated_report.json")
    ap.add_argument("--kpi", default="production_kpi.json")
    ap.add_argument("--schema-dir", default="docs/schemas")
    ap.add_argument("--anomalies-summary", default="anomalies_summary.json")
    args = ap.parse_args()
    errors: list[str] = []
    try:
        import jsonschema  # type: ignore
    except Exception:
        print(json.dumps({"ok": False, "reason": "jsonschema not installed"}))
        return
    sdir = Path(args.schema_dir)
    # Integrated
    ischema = sdir / "integrated_report.schema.json"
    if ischema.exists() and Path(args.integrated).exists():
        try:
            js = json.loads(Path(args.integrated).read_text())
            schema = json.loads(ischema.read_text())
            jsonschema.validate(instance=js, schema=schema)
        except Exception as e:
            errors.append(f"integrated_report.json: {e}")
    # KPI
    kschema = sdir / "production_kpi.schema.json"
    if kschema.exists() and Path(args.kpi).exists():
        try:
            js = json.loads(Path(args.kpi).read_text())
            schema = json.loads(kschema.read_text())
            jsonschema.validate(instance=js, schema=schema)
        except Exception as e:
            errors.append(f"production_kpi.json: {e}")
    # Optional anomalies summary validation
    asum = sdir / "anomalies_summary.schema.json"
    if asum.exists() and Path(args.anomalies_summary).exists():
        try:
            js = json.loads(Path(args.anomalies_summary).read_text())
            schema = json.loads(asum.read_text())
            jsonschema.validate(instance=js, schema=schema)
        except Exception as e:
            errors.append(f"anomalies_summary.json: {e}")

    ok = not errors
    print(json.dumps({"ok": ok, "errors": errors}))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
