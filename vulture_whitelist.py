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

# ============================================================================
# Intentional Public API Methods
# These are part of the public API but may not be used internally yet
# ============================================================================

# Version management utilities (version.py:169-176)
def update_version_for_feature(description):
    """Update version for new feature"""
    pass

def update_version_for_bugfix(description):
    """Update version for bug fix"""
    pass

# Progress widget API (progress_widget.py:128-142)
def set_progress_range(min_value, max_value):
    """Set progress bar range"""
    pass

def get_progress_value():
    """Get current progress value"""
    pass

def is_indeterminate():
    """Check if progress bar is in indeterminate mode"""
    pass

def clear_status():
    """Clear status text"""
    pass

# Base tab API methods (base_tab.py)
def has_warnings():
    """Check if tab has warnings"""
    pass

def has_unsaved_changes():
    """Check if tab has unsaved changes"""
    pass

# FAQ manager API (faq_manager.py)
def get_by_category():
    """Get FAQs by category"""
    pass

def get_categories():
    """Get all FAQ categories"""
    pass

# API key manager (api_key_manager.py)
def clear_all_keys():
    """Clear all stored API keys"""
    pass

def has_aws_credentials():
    """Check if AWS credentials exist"""
    pass

# Backup manager API (backup_manager.py)
def get_all_backups():
    """Get all available backups"""
    pass

# Template validator API (template_validator.py)
def get_issues_by_level():
    """Get validation issues by severity level"""
    pass

def get_issues_by_category():
    """Get validation issues by category"""
    pass

# Enhanced error handler (enhanced_error_handler.py)
def log_info():
    """Log info message"""
    pass

# AWS config validation (client_aws_config.py)
def is_valid_for_deployment():
    """Check if config is valid for deployment"""
    pass
