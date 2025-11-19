# FAQ Import/Export Documentation

Complete guide for bulk importing and exporting FAQs using CSV and JSON formats.

## Table of Contents

- [Overview](#overview)
- [CSV Format](#csv-format)
- [JSON Format](#json-format)
- [Field Descriptions](#field-descriptions)
- [Import Examples](#import-examples)
- [Export Examples](#export-examples)
- [Templates](#templates)

---

## Overview

The FAQ system supports bulk operations via two formats:
- **CSV** - Best for spreadsheet editing (Excel, Google Sheets)
- **JSON** - Best for programmatic data exchange

Both formats support all enhanced FAQ features including categories, tags, priority, and city-specific FAQs.

---

## CSV Format

### Header Row (Required)

```csv
question,answer,category,tags,priority,active,city_name,state,created_date,modified_date
```

### Field Order

| Position | Field Name | Required | Type | Example |
|----------|------------|----------|------|---------|
| 1 | question | Yes | Text | "What are your hours?" |
| 2 | answer | Yes | Text | "We're open Monday-Friday 9AM-5PM" |
| 3 | category | No | Text | "general" |
| 4 | tags | No | Text | "hours,contact,availability" |
| 5 | priority | No | Integer | "10" |
| 6 | active | No | Boolean | "true" |
| 7 | city_name | No | Text | "Orlando" |
| 8 | state | No | Text | "FL" |
| 9 | created_date | No | ISO Date | "2025-11-18T10:30:00" |
| 10 | modified_date | No | ISO Date | "2025-11-18T10:30:00" |

### CSV Example

```csv
question,answer,category,tags,priority,active,city_name,state
"What are your business hours?","We are open Monday-Friday 9AM-5PM EST.",general,"hours,contact,availability",10,true,,
"Do you offer free shipping?","Yes, we offer free shipping on orders over $50.",shipping,"shipping,delivery,cost",8,true,,
"What is your return policy?","We accept returns within 30 days of purchase.",returns,"returns,refund,policy",9,true,,
"Do you serve Orlando?","Yes, we provide services throughout Orlando and surrounding areas.",location,"location,service area",7,true,Orlando,FL
```

### CSV Notes

- **Quotes**: Use double quotes for fields containing commas or line breaks
- **Tags**: Comma-separated within the field (e.g., `"tag1,tag2,tag3"`)
- **Boolean**: Use `true`, `false`, `1`, `0`, `yes`, `no` (case-insensitive)
- **Empty Fields**: Leave blank or use empty quotes `""`
- **Line Breaks in Text**: Supported within quoted fields
- **Encoding**: UTF-8 recommended

---

## JSON Format

### Structure

JSON must be an **array of FAQ objects**:

```json
[
  {
    "question": "FAQ question text",
    "answer": "FAQ answer text",
    "category": "category_name",
    "tags": ["tag1", "tag2"],
    "priority": 0,
    "active": true,
    "city_name": "City Name",
    "state": "ST",
    "created_date": "2025-11-18T10:30:00",
    "modified_date": "2025-11-18T10:30:00",
    "schema_type": "Question"
  }
]
```

### Complete JSON Example

```json
[
  {
    "question": "What are your business hours?",
    "answer": "We are open Monday-Friday 9AM-5PM EST.",
    "category": "general",
    "tags": ["hours", "contact", "availability"],
    "priority": 10,
    "active": true,
    "city_name": null,
    "state": null,
    "created_date": "2025-11-18T10:30:00.123456",
    "modified_date": "2025-11-18T10:30:00.123456",
    "schema_type": "Question"
  },
  {
    "question": "Do you offer free shipping?",
    "answer": "Yes, we offer free shipping on orders over $50.",
    "category": "shipping",
    "tags": ["shipping", "delivery", "cost"],
    "priority": 8,
    "active": true,
    "city_name": null,
    "state": null,
    "created_date": "2025-11-18T10:35:00.123456",
    "modified_date": "2025-11-18T10:35:00.123456",
    "schema_type": "Question"
  },
  {
    "question": "Do you serve Orlando, FL?",
    "answer": "Yes, we provide services throughout Orlando and surrounding areas.",
    "category": "location",
    "tags": ["location", "service area"],
    "priority": 7,
    "active": true,
    "city_name": "Orlando",
    "state": "FL",
    "created_date": "2025-11-18T10:40:00.123456",
    "modified_date": "2025-11-18T10:40:00.123456",
    "schema_type": "Question"
  }
]
```

### JSON Notes

- **Array Required**: Top-level must be `[...]` array
- **Tags**: JSON array `["tag1", "tag2"]`, not comma-separated string
- **Boolean**: Use JSON boolean `true`/`false` (lowercase, no quotes)
- **Null Values**: Use `null` for empty optional fields
- **Dates**: ISO 8601 format recommended
- **Pretty Print**: Use indentation for readability (optional)

---

## Field Descriptions

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| **question** | Text | The FAQ question (cannot be empty) |
| **answer** | Text | The FAQ answer (cannot be empty) |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| **category** | Text | "general" | FAQ category (see Categories below) |
| **tags** | List | [] | Keywords for search and filtering |
| **priority** | Integer | 0 | Display priority (0-100, higher = more important) |
| **active** | Boolean | true | Whether FAQ is visible on website |
| **city_name** | Text | null | City name for location-specific FAQs |
| **state** | Text | null | State code (2 letters, e.g., "FL") |
| **created_date** | ISO Date | auto | Timestamp when FAQ was created |
| **modified_date** | ISO Date | auto | Timestamp when FAQ was last modified |
| **schema_type** | Text | "Question" | Schema.org type (usually "Question") |

### Categories

Valid category values (case-insensitive):

- `general` - General questions
- `products` - Product-related FAQs
- `services` - Service-related FAQs
- `pricing` - Pricing and payment FAQs
- `shipping` - Shipping and delivery FAQs
- `returns` - Return and refund FAQs
- `technical` - Technical support FAQs
- `account` - Account management FAQs
- `location` - Location and service area FAQs
- `other` - Other/miscellaneous FAQs

### Tags

- **Purpose**: Enable flexible filtering and search
- **Format**:
  - CSV: Comma-separated string `"tag1,tag2,tag3"`
  - JSON: Array of strings `["tag1", "tag2", "tag3"]`
- **Best Practices**:
  - Use lowercase
  - Keep short (1-2 words)
  - Be consistent
  - Examples: `pricing`, `hours`, `delivery`, `refund`, `locations`

### Priority

- **Range**: 0 to 100
- **Default**: 0
- **Usage**: Control display order (higher priority shows first)
- **Examples**:
  - 0-3: Low priority / rarely asked
  - 4-7: Medium priority / commonly asked
  - 8-10: High priority / frequently asked / important

### Active Status

- **true**: FAQ is visible on website
- **false**: FAQ is hidden but not deleted
- **Use Cases**:
  - Seasonal FAQs (activate/deactivate as needed)
  - Draft FAQs (inactive until ready)
  - Deprecated FAQs (keep for reference but hide)

---

## Import Examples

### From CSV File

**Step 1**: Create/edit CSV file in Excel or text editor

```csv
question,answer,category,tags,priority,active
"What payment methods do you accept?","We accept Visa, Mastercard, Amex, and PayPal.",general,"payment,billing",8,true
"How long does shipping take?","Standard shipping takes 5-7 business days.",shipping,"shipping,delivery",7,true
```

**Step 2**: In the UI, click **Import CSV** button

**Step 3**: Select your CSV file

**Result**: FAQs are imported and displayed in the table

### From JSON File

**Step 1**: Create JSON file

```json
[
  {
    "question": "What is your refund policy?",
    "answer": "Full refunds within 30 days with original packaging.",
    "category": "returns",
    "tags": ["refund", "returns", "policy"],
    "priority": 9,
    "active": true
  }
]
```

**Step 2**: In the UI, click **Import JSON** button

**Step 3**: Select your JSON file

**Result**: FAQs are imported and merged with existing FAQs

### Import Behavior

- **Duplicate Detection**: Not automatic - duplicates will be imported
- **Validation**: Invalid FAQs are skipped with warning in logs
- **Merge**: Imported FAQs are added to existing FAQs
- **Timestamps**: Auto-generated if not provided
- **Error Handling**: Invalid rows/objects are skipped, valid ones imported

---

## Export Examples

### Export to CSV

**Active FAQs Only** (default):
1. Check "Active Only" checkbox
2. Click **Export CSV**
3. Save file (e.g., `active_faqs.csv`)

**All FAQs** (including inactive):
1. Uncheck "Active Only" checkbox
2. Click **Export CSV**
3. Save file (e.g., `all_faqs.csv`)

**Empty Template Export**:
- If **no FAQs exist**, export creates a template CSV with headers only
- Use this template to create your first batch of FAQs

### Export to JSON

**Active FAQs Only**:
1. Check "Active Only" checkbox
2. Click **Export JSON**
3. Save file (e.g., `faqs.json`)

**All FAQs**:
1. Uncheck "Active Only" checkbox
2. Click **Export JSON**
3. Save file with all metadata

**JSON Features**:
- Pretty-printed (indented) by default
- Includes all fields (timestamps, priority, etc.)
- Ready for programmatic processing

---

## Templates

### Empty CSV Template

When no FAQs exist, export creates:

```csv
question,answer,category,tags,priority,active,city_name,state,created_date,modified_date
```

You can then add rows with your FAQ data.

### Empty JSON Template

When no FAQs exist, export creates:

```json
[
  {
    "question": "",
    "answer": "",
    "category": "general",
    "tags": [],
    "priority": 0,
    "active": true,
    "city_name": null,
    "state": null,
    "created_date": "",
    "modified_date": "",
    "schema_type": "Question"
  }
]
```

Replace the empty example with your FAQ data.

### Pre-filled Templates

See `examples/` folder for:
- `faq_template.csv` - CSV template with sample FAQs
- `faq_template.json` - JSON template with sample FAQs

---

## Common Use Cases

### Bulk Initial Import

1. Create CSV in Excel with all your FAQs
2. Include categories and tags for organization
3. Set priority for important FAQs
4. Import via **Import CSV** button

### Export for Editing

1. Export current FAQs to CSV
2. Edit in Excel (add/remove/modify)
3. Import updated CSV
4. Review in UI and save configuration

### Backup FAQs

1. Export all FAQs to JSON (uncheck "Active Only")
2. Save file to backup location
3. Import later if needed to restore

### Share FAQs Between Projects

1. Export FAQs from Project A (JSON)
2. Import into Project B
3. Edit as needed for new project

---

## Tips and Best Practices

### CSV Editing

- **Excel**: Best for bulk editing and data entry
- **Google Sheets**: Good for collaboration
- **Text Editor**: Works but harder to manage columns

### Data Quality

- **Test Small**: Import 2-3 FAQs first to test format
- **Validate**: Check for empty questions/answers
- **Consistent Categories**: Use standard categories
- **Tag Strategy**: Define tag naming convention
- **Priority Plan**: Decide priority scale upfront

### Version Control

- **Export Regularly**: Backup FAQs after major changes
- **Name Files**: Use descriptive names (`faqs_2025-11-18.json`)
- **Track Changes**: Keep exported versions for rollback

### Performance

- **Large Imports**: 100+ FAQs should import in < 2 seconds
- **File Size**: CSV is smaller than JSON for same data
- **Encoding**: Always use UTF-8 to avoid character issues

---

## Troubleshooting

### Import Fails

**Problem**: "Failed to import CSV"
- **Check**: File encoding is UTF-8
- **Check**: CSV has header row
- **Check**: Required fields (question, answer) are not empty

**Problem**: "Skipping invalid rows"
- **Check**: Logs for specific error messages
- **Fix**: Correct invalid data in those rows
- **Retry**: Import after fixing

### Export Issues

**Problem**: Export file is empty
- **Check**: At least one FAQ exists
- **Check**: "Active Only" not filtering all FAQs

**Problem**: Exported data looks wrong
- **Check**: File encoding when opening (use UTF-8)
- **Check**: Excel might modify dates - use text editor to verify

### Encoding Problems

**Problem**: Special characters display incorrectly
- **Solution**: Ensure file is UTF-8 encoded
- **Excel**: Use "Import Data" instead of double-click
- **Text Editor**: Set encoding to UTF-8 when saving

---

## API Reference

### Python Code Examples

```python
from pathlib import Path
from src.core.content.faq_manager import FAQManager, EnhancedFAQItem, FAQCategory

# Initialize manager
manager = FAQManager()

# Add FAQ programmatically
faq = EnhancedFAQItem(
    question="What are your hours?",
    answer="We're open Monday-Friday 9AM-5PM EST",
    category=FAQCategory.GENERAL.value,
    tags=["hours", "contact"],
    priority=10,
    active=True
)
manager.add_faq(faq)

# Import from CSV
count = manager.import_from_csv(Path("faqs.csv"))
print(f"Imported {count} FAQs")

# Export to JSON
count = manager.export_to_json(Path("faqs.json"), active_only=True, pretty=True)
print(f"Exported {count} FAQs")

# Search FAQs
results = manager.search(search_term="shipping", category="shipping")
print(f"Found {len(results)} shipping FAQs")

# Get statistics
stats = manager.get_statistics()
print(f"Total: {stats['total_faqs']}, Active: {stats['active_faqs']}")
```

---

## Version History

- **v1.0** (2025-11-18) - Initial documentation
  - CSV and JSON import/export
  - Enhanced FAQ model with categories, tags, priority
  - City-specific FAQ support
  - Template export for empty FAQ lists

---

## Support

For issues or questions:
1. Check this documentation
2. Review example files in `examples/` folder
3. Check logs for detailed error messages
4. Refer to unit tests in `tests/unit/test_faq_manager.py`
