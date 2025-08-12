"""
Filename: __init__.py
Path: E:\\projects\\cloud-stack-generator\\src\\ui\\content_tabs\\__init__.py
Description: Content management tabs module initialization and exports
Provides clean imports for ProductsTab, ServicesTab and their data models

Version: 1.0.0
Date: 2025-08-11
Author: Cloud Stack Generator Team
"""

# Import content management tabs
try:
    from .products_tab import (
        ProductsTab,
        Product,
        ValidationResult as ProductsValidationResult,
    )

    __all__ = ["ProductsTab", "Product", "ProductsValidationResult"]
except ImportError:
    print("⚠️ Warning: ProductsTab not available")
    __all__ = []

try:
    from .services_tab import (
        ServicesTab,
        Service,
        FAQ,
        ValidationResult as ServicesValidationResult,
    )

    __all__.extend(["ServicesTab", "Service", "FAQ", "ServicesValidationResult"])
except ImportError:
    print("⚠️ Warning: ServicesTab not available")

# Future content tabs will be added here
# try:
#     from .cities_tab import CitiesTab
#     __all__.append("CitiesTab")
# except ImportError:
#     print("⚠️ Warning: CitiesTab not available")

print(f"📦 Content Tabs loaded: {', '.join(__all__)}")
