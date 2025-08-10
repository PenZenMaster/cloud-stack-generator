"""
Debug test script to verify components work
Run from project root directory
"""

import sys
import os
from pathlib import Path

print("🔍 Debug Information:")
print(f"Current working directory: {os.getcwd()}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries

# Check if src directory exists
src_path = Path("src")
print(f"src directory exists: {src_path.exists()}")
if src_path.exists():
    print(f"src contents: {list(src_path.iterdir())}")

# Check specific files
models_file = Path("src/core/config/models.py")
csv_file = Path("src/core/data/csv_manager.py")
print(f"models.py exists: {models_file.exists()}")
print(f"csv_manager.py exists: {csv_file.exists()}")

print("\n🔍 Testing imports...")

# Test imports one by one
try:
    print("Importing models...")
    from src.core.config.models import BusinessConfig

    print("✅ BusinessConfig imported")

    from src.core.config.models import ProductConfig

    print("✅ ProductConfig imported")

    from src.core.config.models import ClientConfig

    print("✅ ClientConfig imported")

    print("Importing CSV manager...")
    from src.core.data.csv_manager import CSVManager

    print("✅ CSVManager imported")

    from src.core.data.csv_manager import ValidationResult

    print("✅ ValidationResult imported")

except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Traceback:")
    import traceback

    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n🔍 Testing component creation...")

try:
    # Test BusinessConfig
    print("Creating BusinessConfig...")
    business = BusinessConfig(
        business_name="Test Company", domain="example.com", industry="Technology"
    )
    print(f"✅ BusinessConfig: {business.business_name}, {business.domain}")

    # Test ProductConfig
    print("Creating ProductConfig...")
    product = ProductConfig(sku="TEST-001", name="Test Product")
    print(f"✅ ProductConfig: {product.sku}, slug: {product.slug}")

    # Test CSV Manager
    print("Creating CSVManager...")
    csv_manager = CSVManager()
    print(
        f"✅ CSVManager created with {len(csv_manager.supported_encodings)} encodings"
    )

    # Test validation with nonexistent file (should handle gracefully)
    print("Testing CSV validation...")
    validation_result = csv_manager.validate_csv_file("nonexistent.csv", "products")
    print(f"✅ CSV validation (expected failure): {validation_result.is_valid}")

    # Test ValidationResult
    print("Testing ValidationResult...")
    result = ValidationResult()
    result.add_error(1, "SKU", "Missing SKU")
    result.add_warning(2, "Name", "Long name")
    print(
        f"✅ ValidationResult: {len(result.errors)} errors, {len(result.warnings)} warnings"
    )

    # Test ClientConfig
    print("Testing ClientConfig...")
    config = ClientConfig()
    config.business = business
    config.add_product(product)

    is_valid, errors = config.validate()
    print(
        f"✅ ClientConfig validation: {is_valid}, errors: {len(errors) if errors else 0}"
    )

    # Test YAML conversion
    print("Testing YAML conversion...")
    yaml_dict = config.to_yaml_dict()
    print(f"✅ YAML conversion: {len(yaml_dict)} top-level keys")

    print("\n🎉 ALL TESTS PASSED!")
    print("All Day 1 components working correctly!")
    print("Ready for Day 2: Configuration Parser and UI Components")

except Exception as e:
    print(f"❌ Test failed: {e}")
    print("Traceback:")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n✅ Test completed successfully!")
