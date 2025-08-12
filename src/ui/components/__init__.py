"""
Filename: __init__.py
Path: E:\\projects\\cloud-stack-generator\\src\\ui\\components\\__init__.py
Description: UI components module initialization and exports
Provides clean imports for BaseTab, BusinessTab, ContactTab and future components

Version: 1.0.2
Date: 2025-08-11
Author: Cloud Stack Generator Team
Add Branding Component
"""

# Import base components
try:
    from .base_tab import BaseTab

    __all__ = ["BaseTab"]
except ImportError:
    print("⚠️ Warning: BaseTab not available")
    __all__ = []

# Import specialized tab components
try:
    from .business_tab import BusinessTab

    __all__.append("BusinessTab")
except ImportError:
    print("⚠️ Warning: BusinessTab not available")

try:
    from .contact_tab import ContactTab, ValidationResult

    __all__.extend(["ContactTab", "ValidationResult"])
except ImportError:
    print("⚠️ Warning: ContactTab not available")

# Future tab components will be added here
# try:
#     from .branding_tab import BrandingTab
#     __all__.append("BrandingTab")
# except ImportError:
#     print("⚠️ Warning: BrandingTab not available")

print(f"📦 UI Components loaded: {', '.join(__all__)}")
