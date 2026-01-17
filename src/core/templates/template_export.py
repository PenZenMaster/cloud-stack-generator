"""
Template Export/Import System
Path: E:\\projects\\cloud-stack-generator\\src\\core\\templates\\template_export.py

Description:
Handles template import and export functionality for the template system.
Supports packaging templates with metadata and validation.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-18

Last Modified Date:
2026-01-16

Comments:
* v1.00 - Initial template export/import system
* v1.01 - Added progress callbacks, proper logging, enhanced validation
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
from pathlib import Path
import json
import zipfile
import tempfile
import shutil
from datetime import datetime
import sys

from .template_manager import TemplateManager, TemplateMetadata, TemplateType, TemplateVariant

# Import logger
try:
    from core.utils.logger import get_logger
except ImportError:
    # Fallback to basic logging if custom logger not available
    import logging
    def get_logger(name):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)

# Initialize logger
logger = get_logger(__name__)


class TemplatePackageValidator:
    """Validates template packages for import"""

    @staticmethod
    def validate_package_structure(package_path: Path) -> Tuple[bool, str]:
        """
        Validate the basic structure of a template package

        Args:
            package_path: Path to the template package (.zip)

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not package_path.exists():
                return False, "Package file does not exist"

            if not zipfile.is_zipfile(package_path):
                return False, "File is not a valid ZIP archive"

            # Check package contents
            with zipfile.ZipFile(package_path, 'r') as zipf:
                file_list = zipf.namelist()

                # Required files
                if 'metadata.json' not in file_list:
                    return False, "Package missing required file: metadata.json"

                if 'template.html' not in file_list:
                    return False, "Package missing required file: template.html"

                # Check for suspicious files
                suspicious_extensions = ['.exe', '.dll', '.sh', '.bat', '.cmd', '.vbs', '.ps1']
                for filename in file_list:
                    if any(filename.lower().endswith(ext) for ext in suspicious_extensions):
                        return False, f"Package contains potentially unsafe file: {filename}"

            return True, "Package structure valid"

        except Exception as e:
            logger.error(f"Error validating package structure: {e}", exc_info=True)
            return False, f"Validation error: {str(e)}"

    @staticmethod
    def validate_metadata(metadata_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate metadata dictionary

        Args:
            metadata_dict: Metadata dictionary to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        required_fields = {
            "id": str,
            "name": str,
            "type": str,
            "variant": str,
            "template_file": str,
            "version": str
        }

        for field, expected_type in required_fields.items():
            if field not in metadata_dict:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(metadata_dict[field], expected_type):
                errors.append(f"Field '{field}' must be of type {expected_type.__name__}")

        # Validate ID format (alphanumeric, underscores, hyphens only)
        if "id" in metadata_dict:
            template_id = metadata_dict["id"]
            if not template_id or not isinstance(template_id, str):
                errors.append("Template ID must be a non-empty string")
            elif not all(c.isalnum() or c in ['_', '-'] for c in template_id):
                errors.append("Template ID must contain only letters, numbers, underscores, and hyphens")

        # Validate enum values
        if "type" in metadata_dict:
            try:
                TemplateType(metadata_dict["type"])
            except ValueError:
                valid_types = [t.value for t in TemplateType]
                errors.append(f"Invalid template type. Must be one of: {', '.join(valid_types)}")

        if "variant" in metadata_dict:
            try:
                TemplateVariant(metadata_dict["variant"])
            except ValueError:
                valid_variants = [v.value for v in TemplateVariant]
                errors.append(f"Invalid template variant. Must be one of: {', '.join(valid_variants)}")

        # Validate version format (basic semver check)
        if "version" in metadata_dict:
            version = metadata_dict["version"]
            if not version or not isinstance(version, str):
                errors.append("Version must be a non-empty string")

        # Validate optional list fields
        list_fields = ["required_data", "optional_data", "features"]
        for field in list_fields:
            if field in metadata_dict and not isinstance(metadata_dict[field], list):
                errors.append(f"Field '{field}' must be a list")

        # Validate compatibility dict
        if "compatibility" in metadata_dict and not isinstance(metadata_dict["compatibility"], dict):
            errors.append("Field 'compatibility' must be a dictionary")

        return len(errors) == 0, errors

    @staticmethod
    def validate_template_html(template_path: Path) -> Tuple[bool, str]:
        """
        Validate template HTML file

        Args:
            template_path: Path to the template HTML file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not template_path.exists():
                return False, "Template file does not exist"

            # Check file size (max 5MB)
            max_size = 5 * 1024 * 1024
            file_size = template_path.stat().st_size
            if file_size > max_size:
                return False, f"Template file too large ({file_size} bytes). Maximum size is {max_size} bytes"

            if file_size == 0:
                return False, "Template file is empty"

            # Read and validate basic HTML structure
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic HTML validation
            if not content.strip():
                return False, "Template file is empty"

            # Check for basic HTML structure (very basic check)
            if '<html' not in content.lower() and '<!doctype' not in content.lower():
                return False, "Template file does not appear to be valid HTML"

            return True, "Template HTML valid"

        except UnicodeDecodeError:
            return False, "Template file is not valid UTF-8 text"
        except Exception as e:
            logger.error(f"Error validating template HTML: {e}", exc_info=True)
            return False, f"Validation error: {str(e)}"


class TemplateExporter:
    """Handles template export operations"""

    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager

    def export_template_package(
        self,
        template_id: str,
        export_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Tuple[bool, str]:
        """
        Export a template as a complete package with metadata

        Args:
            template_id: ID of the template to export
            export_path: Path where to save the package (.zip)
            progress_callback: Optional callback function(message: str, progress: int)
                             where progress is 0-100

        Returns:
            Tuple of (success: bool, message: str)
        """
        def report_progress(message: str, progress: int):
            """Report progress to callback if provided"""
            if progress_callback:
                progress_callback(message, progress)
            logger.info(f"Export progress ({progress}%): {message}")

        try:
            logger.info(f"Starting template export: {template_id}")
            report_progress("Validating template", 0)

            template_metadata = self.template_manager.get_template_by_id(template_id)
            if not template_metadata:
                error_msg = f"Template {template_id} not found"
                logger.error(error_msg)
                return False, error_msg

            report_progress("Preparing package", 10)

            # Create temporary directory for package
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Copy template file
                template_file_path = self.template_manager.templates_dir / template_metadata.template_file
                if not template_file_path.exists():
                    error_msg = f"Template file not found: {template_file_path}"
                    logger.error(error_msg)
                    return False, error_msg

                report_progress("Creating package structure", 20)

                # Create package structure
                package_dir = temp_path / "template_package"
                package_dir.mkdir(parents=True)

                report_progress("Copying template file", 30)

                # Copy template file
                template_dest = package_dir / "template.html"
                shutil.copy2(template_file_path, template_dest)

                report_progress("Creating metadata", 50)

                # Create metadata file
                metadata_dict = template_metadata.to_dict()
                metadata_dict["exported_at"] = datetime.now().isoformat()
                metadata_dict["exported_by"] = "Cloud Stack Generator"
                metadata_dict["package_version"] = "1.0"

                metadata_file = package_dir / "metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata_dict, f, indent=2, ensure_ascii=False)

                report_progress("Creating README", 70)

                # Create README
                readme_content = self._generate_package_readme(template_metadata)
                readme_file = package_dir / "README.md"
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write(readme_content)

                report_progress("Creating ZIP package", 80)

                # Create zip package
                export_path.parent.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in package_dir.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(package_dir)
                            zipf.write(file_path, arcname)

                report_progress("Export complete", 100)
                success_msg = f"Template '{template_metadata.name}' exported successfully"
                logger.info(success_msg)
                return True, success_msg

        except Exception as e:
            error_msg = f"Error exporting template package: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def export_template_collection(
        self,
        template_ids: List[str],
        export_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Tuple[bool, str]:
        """
        Export multiple templates as a collection

        Args:
            template_ids: List of template IDs to export
            export_path: Path where to save the collection (.zip)
            progress_callback: Optional callback function(message: str, progress: int)

        Returns:
            Tuple of (success: bool, message: str)
        """
        def report_progress(message: str, progress: int):
            """Report progress to callback if provided"""
            if progress_callback:
                progress_callback(message, progress)
            logger.info(f"Collection export progress ({progress}%): {message}")

        try:
            logger.info(f"Starting collection export: {len(template_ids)} templates")
            report_progress("Preparing collection", 0)

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                collection_dir = temp_path / "template_collection"
                collection_dir.mkdir(parents=True)

                exported_templates = []
                total = len(template_ids)

                for idx, template_id in enumerate(template_ids):
                    progress = int((idx / total) * 80)  # 0-80%
                    report_progress(f"Exporting template {idx + 1}/{total}", progress)

                    template_metadata = self.template_manager.get_template_by_id(template_id)
                    if not template_metadata:
                        logger.warning(f"Template {template_id} not found, skipping")
                        continue

                    # Create subdirectory for this template
                    template_dir = collection_dir / template_id
                    template_dir.mkdir(parents=True)

                    # Copy template file
                    template_file_path = self.template_manager.templates_dir / template_metadata.template_file
                    if template_file_path.exists():
                        shutil.copy2(template_file_path, template_dir / "template.html")

                        # Copy metadata
                        metadata_dict = template_metadata.to_dict()
                        with open(template_dir / "metadata.json", 'w', encoding='utf-8') as f:
                            json.dump(metadata_dict, f, indent=2, ensure_ascii=False)

                        exported_templates.append({
                            "id": template_id,
                            "name": template_metadata.name,
                            "version": template_metadata.version
                        })

                report_progress("Creating collection manifest", 85)

                # Create collection manifest
                manifest = {
                    "collection_name": "Template Collection",
                    "exported_at": datetime.now().isoformat(),
                    "exported_by": "Cloud Stack Generator",
                    "collection_version": "1.0",
                    "templates": exported_templates
                }

                with open(collection_dir / "collection.json", 'w', encoding='utf-8') as f:
                    json.dump(manifest, f, indent=2, ensure_ascii=False)

                report_progress("Creating ZIP package", 90)

                # Create zip
                with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in collection_dir.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(collection_dir)
                            zipf.write(file_path, arcname)

                report_progress("Export complete", 100)
                success_msg = f"Collection exported successfully: {len(exported_templates)} templates"
                logger.info(success_msg)
                return True, success_msg

        except Exception as e:
            error_msg = f"Error exporting template collection: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def _generate_package_readme(self, metadata: TemplateMetadata) -> str:
        """Generate README content for template package"""
        return f"""# {metadata.name}

**Version:** {metadata.version}
**Type:** {metadata.type.value.title()}
**Variant:** {metadata.variant.value.title()}
**Author:** {metadata.author}

## Description

{metadata.description}

## Features

{chr(10).join([f"- {feature}" for feature in metadata.features])}

## Requirements

### Required Data Fields
{chr(10).join([f"- {field}" for field in metadata.required_data])}

### Optional Data Fields
{chr(10).join([f"- {field}" for field in metadata.optional_data])}

## Installation

1. Import this template package into Cloud Stack Generator
2. Select the template in the Branding & Style tab
3. Configure your content and generate your website

## Compatibility

{chr(10).join([f"- {key.replace('_', ' ').title()}: {value}" for key, value in metadata.compatibility.items()])}

---

*Exported from Cloud Stack Generator v2.1.0*
"""


class TemplateImporter:
    """Handles template import operations"""

    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager
        self.validator = TemplatePackageValidator()

    def import_template_package(
        self,
        package_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        allow_overwrite: bool = False
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Import a template from a package file

        Args:
            package_path: Path to the template package (.zip)
            progress_callback: Optional callback function(message: str, progress: int)
            allow_overwrite: If True, allow overwriting existing templates with same ID

        Returns:
            Tuple of (success, message, template_id)
        """
        def report_progress(message: str, progress: int):
            """Report progress to callback if provided"""
            if progress_callback:
                progress_callback(message, progress)
            logger.info(f"Import progress ({progress}%): {message}")

        try:
            logger.info(f"Starting template import from: {package_path}")
            report_progress("Validating package", 0)

            # Validate package structure
            is_valid, error_msg = self.validator.validate_package_structure(package_path)
            if not is_valid:
                logger.error(f"Package validation failed: {error_msg}")
                return False, error_msg, None

            report_progress("Extracting package", 10)

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Extract package
                try:
                    with zipfile.ZipFile(package_path, 'r') as zipf:
                        zipf.extractall(temp_path)
                except zipfile.BadZipFile:
                    error_msg = "Invalid or corrupted ZIP file"
                    logger.error(error_msg)
                    return False, error_msg, None

                report_progress("Validating metadata", 25)

                # Look for metadata file
                metadata_file = temp_path / "metadata.json"
                if not metadata_file.exists():
                    error_msg = "Invalid package: metadata.json not found"
                    logger.error(error_msg)
                    return False, error_msg, None

                # Load metadata
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata_dict = json.load(f)
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON in metadata file: {str(e)}"
                    logger.error(error_msg)
                    return False, error_msg, None

                # Validate metadata
                is_valid, validation_errors = self.validator.validate_metadata(metadata_dict)
                if not is_valid:
                    error_msg = "Metadata validation failed:\n" + "\n".join(validation_errors)
                    logger.error(error_msg)
                    return False, error_msg, None

                report_progress("Validating template file", 40)

                # Look for template file
                template_file = temp_path / "template.html"
                if not template_file.exists():
                    error_msg = "Invalid package: template.html not found"
                    logger.error(error_msg)
                    return False, error_msg, None

                # Validate template HTML
                is_valid, error_msg = self.validator.validate_template_html(template_file)
                if not is_valid:
                    logger.error(f"Template HTML validation failed: {error_msg}")
                    return False, error_msg, None

                report_progress("Processing template metadata", 60)

                # Create TemplateMetadata object
                try:
                    template_metadata = TemplateMetadata.from_dict(metadata_dict)
                except Exception as e:
                    error_msg = f"Error parsing metadata: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    return False, error_msg, None

                report_progress("Checking for conflicts", 70)

                # Check for conflicts
                existing_template = self.template_manager.get_template_by_id(template_metadata.id)
                if existing_template:
                    if not allow_overwrite:
                        error_msg = (
                            f"Template with ID '{template_metadata.id}' already exists.\n"
                            f"Existing: {existing_template.name} v{existing_template.version}\n"
                            f"Import: {template_metadata.name} v{template_metadata.version}\n\n"
                            f"To replace the existing template, enable 'Allow Overwrite'."
                        )
                        logger.warning(error_msg)
                        return False, error_msg, None
                    else:
                        logger.info(f"Overwriting existing template: {template_metadata.id}")

                report_progress("Importing template", 85)

                # Import the template
                success = self.template_manager.import_template(template_file, template_metadata)
                if success:
                    report_progress("Import complete", 100)
                    success_msg = f"Template '{template_metadata.name}' v{template_metadata.version} imported successfully"
                    logger.info(success_msg)
                    return True, success_msg, template_metadata.id
                else:
                    error_msg = "Failed to import template to template manager"
                    logger.error(error_msg)
                    return False, error_msg, None

        except Exception as e:
            error_msg = f"Import error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, None

    def import_template_collection(
        self,
        collection_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        allow_overwrite: bool = False
    ) -> Tuple[bool, str, List[str]]:
        """
        Import multiple templates from a collection file

        Args:
            collection_path: Path to the template collection (.zip)
            progress_callback: Optional callback function(message: str, progress: int)
            allow_overwrite: If True, allow overwriting existing templates

        Returns:
            Tuple of (success, message, list_of_imported_template_ids)
        """
        def report_progress(message: str, progress: int):
            """Report progress to callback if provided"""
            if progress_callback:
                progress_callback(message, progress)
            logger.info(f"Collection import progress ({progress}%): {message}")

        try:
            logger.info(f"Starting collection import from: {collection_path}")
            report_progress("Validating collection", 0)

            imported_templates = []
            errors = []

            if not collection_path.exists():
                error_msg = "Collection file not found"
                logger.error(error_msg)
                return False, error_msg, []

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                report_progress("Extracting collection", 5)

                # Extract collection
                try:
                    with zipfile.ZipFile(collection_path, 'r') as zipf:
                        zipf.extractall(temp_path)
                except zipfile.BadZipFile:
                    error_msg = "Invalid or corrupted ZIP file"
                    logger.error(error_msg)
                    return False, error_msg, []

                # Look for collection manifest
                manifest_file = temp_path / "collection.json"
                if not manifest_file.exists():
                    error_msg = "Invalid collection: collection.json not found"
                    logger.error(error_msg)
                    return False, error_msg, []

                # Load manifest
                try:
                    with open(manifest_file, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON in collection manifest: {str(e)}"
                    logger.error(error_msg)
                    return False, error_msg, []

                templates_list = manifest.get("templates", [])
                total = len(templates_list)

                if total == 0:
                    error_msg = "Collection contains no templates"
                    logger.warning(error_msg)
                    return False, error_msg, []

                # Import each template
                for idx, template_info in enumerate(templates_list):
                    template_id = template_info["id"]
                    progress = int(10 + (idx / total) * 85)  # 10-95%
                    report_progress(f"Importing template {idx + 1}/{total}: {template_id}", progress)

                    template_dir = temp_path / template_id

                    if not template_dir.exists():
                        errors.append(f"Template directory not found: {template_id}")
                        logger.warning(f"Template directory not found: {template_id}")
                        continue

                    metadata_file = template_dir / "metadata.json"
                    template_file = template_dir / "template.html"

                    if not metadata_file.exists() or not template_file.exists():
                        errors.append(f"Incomplete template: {template_id}")
                        logger.warning(f"Incomplete template: {template_id}")
                        continue

                    # Load and import template
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata_dict = json.load(f)

                        # Validate metadata
                        is_valid, validation_errors = self.validator.validate_metadata(metadata_dict)
                        if not is_valid:
                            error_detail = f"Invalid metadata for {template_id}: {'; '.join(validation_errors)}"
                            errors.append(error_detail)
                            logger.warning(error_detail)
                            continue

                        template_metadata = TemplateMetadata.from_dict(metadata_dict)

                        # Check for conflicts
                        if self.template_manager.get_template_by_id(template_metadata.id):
                            if not allow_overwrite:
                                errors.append(f"Template already exists: {template_id}")
                                logger.warning(f"Template already exists, skipping: {template_id}")
                                continue
                            else:
                                logger.info(f"Overwriting existing template: {template_id}")

                        # Import
                        if self.template_manager.import_template(template_file, template_metadata):
                            imported_templates.append(template_id)
                            logger.info(f"Successfully imported: {template_id}")
                        else:
                            errors.append(f"Failed to import: {template_id}")
                            logger.error(f"Failed to import: {template_id}")

                    except Exception as e:
                        error_detail = f"Error importing {template_id}: {str(e)}"
                        errors.append(error_detail)
                        logger.error(error_detail, exc_info=True)

            # Prepare result message
            report_progress("Finalizing import", 100)

            if imported_templates and not errors:
                message = f"Successfully imported {len(imported_templates)} templates"
                logger.info(message)
            elif imported_templates and errors:
                message = (
                    f"Imported {len(imported_templates)} templates with {len(errors)} errors:\n"
                    + "\n".join(errors[:5])  # Show first 5 errors
                )
                if len(errors) > 5:
                    message += f"\n... and {len(errors) - 5} more errors"
                logger.warning(message)
            else:
                message = f"Import failed. Errors:\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    message += f"\n... and {len(errors) - 5} more errors"
                logger.error(message)

            return len(imported_templates) > 0, message, imported_templates

        except Exception as e:
            error_msg = f"Collection import error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, []