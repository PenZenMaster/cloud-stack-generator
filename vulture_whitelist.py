"""
Vulture Whitelist for Cloud Stack Generator

This file contains intentional code that vulture flags as unused but is actually
part of the API, planned features, or necessary for framework operation.

Category breakdown:
- FAQ Categories: Enum values for FAQ categorization (planned feature)
- Template Types: Enum values for template management
- Deployment Modes: Multi-cloud deployment configurations
- Build Pipeline Stages: Pipeline stage definitions
- Template Variants: Template variant classifications
- Error Classifications: Error type enumerations
- Custom Exceptions: Exception classes used in error paths
"""

# ============================================================================
# FAQ Manager Enums (faq_manager.py:39-47)
# Intentional API for FAQ categorization - planned feature
# ============================================================================
PRODUCTS = None
SERVICES = None
PRICING = None
SHIPPING = None
RETURNS = None
TECHNICAL = None
ACCOUNT = None
LOCATION = None
OTHER = None

# ============================================================================
# Template Types (template_manager.py:34-37)
# Enum values for template type classification
# ============================================================================
LANDING_PAGE = None
PRODUCT_PAGE = None
SERVICE_PAGE = None
CONTACT_PAGE = None

# ============================================================================
# Deployment Modes (abstract_provider.py:49)
# Planned feature for multi-cloud CDN integration
# ============================================================================
CDN_INTEGRATED = None

# ============================================================================
# Build Pipeline Stages (build_pipeline.py:31)
# Pipeline stage enum for build orchestration
# ============================================================================
FINALIZE = None

# ============================================================================
# Template Variants (template_manager.py:43-44)
# Template variant classification enum
# ============================================================================
BASIC = None
ENHANCED = None

# ============================================================================
# Error Classifications (error_classification.py:42-45)
# Error type enumerations for error handling
# ============================================================================
NETWORK = None
DATA_INTEGRITY = None

# ============================================================================
# Custom Exceptions (abstract_provider.py:125)
# Exception classes are often unused until needed in error paths
# ============================================================================
class PermissionError:
    """Custom permission error for deployment providers"""
    pass


# ============================================================================
# Properties potentially used in Jinja2 templates
# These may appear unused in Python but are accessed in template rendering
# ============================================================================
# url_path (models.py:412)
# has_enhanced_content (models.py:263)
