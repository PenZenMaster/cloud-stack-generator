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
2025-09-18

Comments:
* v1.00 - Initial template export/import system
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import zipfile
import tempfile
import shutil
from datetime import datetime

from .template_manager import TemplateManager, TemplateMetadata, TemplateType, TemplateVariant


class TemplateExporter:
    """Handles template export operations"""

    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager

    def export_template_package(self, template_id: str, export_path: Path) -> bool:
        """
        Export a template as a complete package with metadata

        Args:
            template_id: ID of the template to export
            export_path: Path where to save the package (.zip)

        Returns:
            True if successful, False otherwise
        """
        try:
            template_metadata = self.template_manager.get_template_by_id(template_id)
            if not template_metadata:
                print(f"Template {template_id} not found")
                return False

            # Create temporary directory for package
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Copy template file
                template_file_path = self.template_manager.templates_dir / template_metadata.template_file
                if not template_file_path.exists():
                    print(f"Template file not found: {template_file_path}")
                    return False

                # Create package structure
                package_dir = temp_path / "template_package"
                package_dir.mkdir(parents=True)

                # Copy template file
                template_dest = package_dir / "template.html"
                shutil.copy2(template_file_path, template_dest)

                # Create metadata file
                metadata_dict = template_metadata.to_dict()
                metadata_dict["exported_at"] = datetime.now().isoformat()
                metadata_dict["exported_by"] = "Cloud Stack Generator"
                metadata_dict["package_version"] = "1.0"

                metadata_file = package_dir / "metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata_dict, f, indent=2, ensure_ascii=False)

                # Create README
                readme_content = self._generate_package_readme(template_metadata)
                readme_file = package_dir / "README.md"
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write(readme_content)

                # Create zip package
                export_path.parent.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in package_dir.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(package_dir)
                            zipf.write(file_path, arcname)

                return True

        except Exception as e:
            print(f"Error exporting template package: {e}")
            return False

    def export_template_collection(self, template_ids: List[str], export_path: Path) -> bool:
        """
        Export multiple templates as a collection

        Args:
            template_ids: List of template IDs to export
            export_path: Path where to save the collection (.zip)

        Returns:
            True if successful, False otherwise
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                collection_dir = temp_path / "template_collection"
                collection_dir.mkdir(parents=True)

                exported_templates = []

                for template_id in template_ids:
                    template_metadata = self.template_manager.get_template_by_id(template_id)
                    if not template_metadata:
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

                # Create zip
                with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in collection_dir.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(collection_dir)
                            zipf.write(file_path, arcname)

                return True

        except Exception as e:
            print(f"Error exporting template collection: {e}")
            return False

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

    def import_template_package(self, package_path: Path) -> tuple[bool, str, Optional[str]]:
        """
        Import a template from a package file

        Args:
            package_path: Path to the template package (.zip)

        Returns:
            Tuple of (success, message, template_id)
        """
        try:
            if not package_path.exists():
                return False, "Package file not found", None

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Extract package
                with zipfile.ZipFile(package_path, 'r') as zipf:
                    zipf.extractall(temp_path)

                # Look for metadata file
                metadata_file = temp_path / "metadata.json"
                if not metadata_file.exists():
                    return False, "Invalid package: metadata.json not found", None

                # Load metadata
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata_dict = json.load(f)

                # Validate metadata
                if not self._validate_import_metadata(metadata_dict):
                    return False, "Invalid metadata format", None

                # Look for template file
                template_file = temp_path / "template.html"
                if not template_file.exists():
                    return False, "Invalid package: template.html not found", None

                # Create TemplateMetadata object
                try:
                    template_metadata = TemplateMetadata.from_dict(metadata_dict)
                except Exception as e:
                    return False, f"Error parsing metadata: {e}", None

                # Check for conflicts
                existing_template = self.template_manager.get_template_by_id(template_metadata.id)
                if existing_template:
                    return False, f"Template with ID '{template_metadata.id}' already exists", None

                # Import the template
                success = self.template_manager.import_template(template_file, template_metadata)
                if success:
                    return True, f"Template '{template_metadata.name}' imported successfully", template_metadata.id
                else:
                    return False, "Failed to import template", None

        except Exception as e:
            return False, f"Import error: {str(e)}", None

    def import_template_collection(self, collection_path: Path) -> tuple[bool, str, List[str]]:
        """
        Import multiple templates from a collection file

        Args:
            collection_path: Path to the template collection (.zip)

        Returns:
            Tuple of (success, message, list_of_imported_template_ids)
        """
        try:
            imported_templates = []
            errors = []

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Extract collection
                with zipfile.ZipFile(collection_path, 'r') as zipf:
                    zipf.extractall(temp_path)

                # Look for collection manifest
                manifest_file = temp_path / "collection.json"
                if not manifest_file.exists():
                    return False, "Invalid collection: collection.json not found", []

                # Load manifest
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)

                # Import each template
                for template_info in manifest.get("templates", []):
                    template_id = template_info["id"]
                    template_dir = temp_path / template_id

                    if not template_dir.exists():
                        errors.append(f"Template directory not found: {template_id}")
                        continue

                    metadata_file = template_dir / "metadata.json"
                    template_file = template_dir / "template.html"

                    if not metadata_file.exists() or not template_file.exists():
                        errors.append(f"Incomplete template: {template_id}")
                        continue

                    # Load and import template
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata_dict = json.load(f)

                        template_metadata = TemplateMetadata.from_dict(metadata_dict)

                        # Check for conflicts
                        if self.template_manager.get_template_by_id(template_metadata.id):
                            errors.append(f"Template already exists: {template_id}")
                            continue

                        # Import
                        if self.template_manager.import_template(template_file, template_metadata):
                            imported_templates.append(template_id)
                        else:
                            errors.append(f"Failed to import: {template_id}")

                    except Exception as e:
                        errors.append(f"Error importing {template_id}: {str(e)}")

            # Prepare result message
            if imported_templates and not errors:
                message = f"Successfully imported {len(imported_templates)} templates"
            elif imported_templates and errors:
                message = f"Imported {len(imported_templates)} templates with {len(errors)} errors"
            else:
                message = f"Import failed: {'; '.join(errors)}"

            return len(imported_templates) > 0, message, imported_templates

        except Exception as e:
            return False, f"Collection import error: {str(e)}", []

    def _validate_import_metadata(self, metadata_dict: Dict[str, Any]) -> bool:
        """Validate imported metadata structure"""
        required_fields = ["id", "name", "type", "variant", "template_file"]

        for field in required_fields:
            if field not in metadata_dict:
                return False

        # Validate enum values
        try:
            TemplateType(metadata_dict["type"])
            TemplateVariant(metadata_dict["variant"])
        except ValueError:
            return False

        return True