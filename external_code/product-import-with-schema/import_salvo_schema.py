"""
Module/Script Name: import_salvo_schema.py

Description:
Imports Salvo Metal Works product category schema from a CSV and writes per-item JSON-LD
files (and optional HTML-wrapped script tags). Also emits combined bundle files.

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
2025-08-19

Last Modified Date:
2025-08-19

Comments:
- v1.00 initial import utility for schema-in-CSV
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REQUIRED_JSON_KEYS = ["@context", "@type", "@id", "name", "url", "offers"]

def _slug_from_name(name: str) -> str:
    return (
        name.strip().lower()
        .replace(" & ", " and ")
        .replace("/", "-")
        .replace(",", "")
        .replace(".", "")
        .replace("  ", " ")
        .replace(" ", "-")
    )

def load_csv(csv_path: Path) -> pd.DataFrame:
    # Robust read: auto-detect delimiter, treat everything as string to avoid NaN surprises
    df = pd.read_csv(csv_path, engine="python", sep=None, dtype=str, encoding="utf-8")
    # Normalize expected columns
    for col in ["SKU", "Name", "Description", "Category", "Price", "Image URL",
                "Schema", "Schema_JSONLD", "Schema_HTML"]:
        if col not in df.columns:
            df[col] = ""
    # Strip whitespace
    df = df.applymap(lambda v: v.strip() if isinstance(v, str) else v)
    return df

def validate_jsonld(js: dict, row_idx: int) -> list[str]:
    errs = []
    for k in REQUIRED_JSON_KEYS:
        if k not in js or js[k] in ("", None):
            errs.append(f"Row {row_idx}: missing required key '{k}'")
    if js.get("@type") != "Product":
        errs.append(f"Row {row_idx}: @type should be 'Product' (got {js.get('@type')})")
    return errs

def main():
    ap = argparse.ArgumentParser(description="Import Salvo schema from CSV and write JSON-LD files.")
    ap.add_argument("--csv", required=True, help="Path to product-catagory-with-schema.csv")
    ap.add_argument("--out", required=True, help="Output directory for JSON/HTML files")
    ap.add_argument("--emit-html", action="store_true", help="Also write per-item HTML <script> files")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        df = load_csv(csv_path)
    except Exception as e:
        print(f"ERROR: Failed to read CSV: {e}", file=sys.stderr)
        sys.exit(1)

    all_json = []
    all_html_blocks = []
    errors = []

    for idx, row in df.iterrows():
        name = (row.get("Name") or "").strip()
        if not name:
            errors.append(f"Row {idx}: missing Name")
            continue

        schema_raw = (row.get("Schema_JSONLD") or "").strip()
        if not schema_raw:
            errors.append(f"Row {idx} ({name}): missing Schema_JSONLD")
            continue

        try:
            js = json.loads(schema_raw)
        except json.JSONDecodeError as je:
            errors.append(f"Row {idx} ({name}): invalid JSON-LD ({je})")
            continue

        v_errs = validate_jsonld(js, idx)
        if v_errs:
            errors.extend(v_errs)

        # Derive filename from @id if present, else from name
        base = js.get("@id") or js.get("url") or name
        slug = _slug_from_name(base.split("#")[0].rsplit("/", 1)[-1])
        if not slug:
            slug = _slug_from_name(name)

        # Write JSON file
        json_path = out_dir / f"{slug}.json"
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(js, f, ensure_ascii=False, separators=(",", ":"))

        all_json.append(js)

        # Optionally emit per-item HTML
        script_block = f'<script type="application/ld+json">{json.dumps(js, separators=(",", ":"))}</script>'
        if args.emit_html:
            html_path = out_dir / f"{slug}.html"
            with html_path.open("w", encoding="utf-8") as f:
                f.write(script_block)
        all_html_blocks.append(script_block)

    # Bundles
    bundle_json = out_dir / "all-products.json"
    with bundle_json.open("w", encoding="utf-8") as f:
        json.dump(all_json, f, ensure_ascii=False, separators=(",", ":"))

    bundle_html = out_dir / "all-products.html"
    with bundle_html.open("w", encoding="utf-8") as f:
        f.write("\n".join(all_html_blocks))

    # Report
    if errors:
        print("Completed with warnings/errors:")
        for e in errors:
            print(" -", e)
    else:
        print("Import complete with no validation errors.")
    print(f"Wrote: {bundle_json}")
    print(f"Wrote: {bundle_html}")

if __name__ == "__main__":
    main()
