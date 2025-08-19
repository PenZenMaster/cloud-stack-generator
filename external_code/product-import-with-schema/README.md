# Salvo Schema Import Kit (v1.00)

## Contents
- `import_salvo_schema.py` — Python 3.10+ script to import JSON-LD from CSV and write per-item files.
- `product-catagory-with-schema.csv` — Sample CSV with minified JSON-LD in `Schema_JSONLD` column.
- `schema_out/` — Sample run output (one `.json` and `.html` per product + bundle files).

## Requirements
- Python 3.10+
- `pandas` installed (`pip install pandas`)

## Usage
Windows:
```
python import_salvo_schema.py --csv ".\product-catagory-with-schema.csv" --out ".\schema_out" --emit-html
```

macOS/Linux:
```
python3 import_salvo_schema.py --csv "./product-catagory-with-schema.csv" --out "./schema_out" --emit-html
```

## Notes
- CSV must be UTF-8, RFC 4180. Minified JSON-LD only (single line) in `Schema_JSONLD`.
- Avoid opening/saving in Excel after schema insertion.
- Outputs:
  - Per-item: `custom-cupolas.json`, `custom-cupolas.html`, etc.
  - Bundles: `all-products.json`, `all-products.html`.
