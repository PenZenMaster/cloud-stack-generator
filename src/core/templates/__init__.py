"""
Template System Module
Path: E:\\projects\\cloud-stack-generator\\src\\core\\templates\\__init__.py

Description:
Core template management system for the website generator.
Provides template discovery, loading, metadata handling, and preview functionality.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-18

Last Modified Date:
2025-09-18

Comments:
* v1.00 - Initial template system module
"""

from .template_manager import (
    TemplateManager,
    TemplateMetadata,
    TemplateType,
    TemplateVariant
)

__all__ = [
    'TemplateManager',
    'TemplateMetadata',
    'TemplateType',
    'TemplateVariant'
]