"""
Filename: __init__.py
Path: E:\\projects\\cloud-stack-generator\\src\\ui\\content_tabs\\__init__.py
Description: Content management tabs module initialization and exports
Provides clean imports for ProductsTab, ServicesTab and their data models

Version: 1.0.0
Date: 2025-08-11
Author: Cloud Stack Generator Team
"""

from src.core.utils.logger import get_logger

logger = get_logger(__name__)

# Import content management tabs
try:
    from .products_tab import (
        ProductsTab,
        Product,
        ValidationResult as ProductsValidationResult,
    )

    __all__ = ["ProductsTab", "Product", "ProductsValidationResult"]
except ImportError:
    logger.warning("ProductsTab not available")
    __all__ = []

try:
    from .services_tab import (  # noqa: F401
        ServicesTab,
        Service,
        ValidationResult as ServicesValidationResult,
    )

    __all__.extend(["ServicesTab", "Service", "ServicesValidationResult"])
except ImportError as e:
    logger.warning(f"ServicesTab not available - {e}")

try:
    from .faq_tab import FAQTab  # noqa: F401

    __all__.append("FAQTab")
except ImportError:
    logger.warning("FAQTab not available")

logger.debug(f"Content Tabs loaded: {', '.join(__all__)}")
