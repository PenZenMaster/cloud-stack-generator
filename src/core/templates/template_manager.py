"""
Template Manager - Core template system for website generation
Path: E:\\projects\\cloud-stack-generator\\src\\core\\templates\\template_manager.py

Description:
Manages template discovery, loading, validation, and metadata handling
for the website generator. Supports multiple template types and variants.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-18

Last Modified Date:
2025-09-18

Comments:
* v1.00 - Initial template management system implementation
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json
import yaml
from dataclasses import dataclass, asdict
from enum import Enum
import jinja2


class TemplateType(Enum):
    """Template type categories"""
    CITY_PAGE = "city_page"
    LANDING_PAGE = "landing_page"
    PRODUCT_PAGE = "product_page"
    SERVICE_PAGE = "service_page"
    CONTACT_PAGE = "contact_page"


class TemplateVariant(Enum):
    """Template style variants"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    SEO_AUTHORITY = "seo_authority"
    CUSTOM = "custom"


@dataclass
class TemplateMetadata:
    """Template metadata configuration"""
    id: str
    name: str
    description: str
    type: TemplateType
    variant: TemplateVariant
    version: str
    author: str
    created_date: str
    last_modified: str
    preview_image: str
    template_file: str
    required_data: List[str]
    optional_data: List[str]
    features: List[str]
    compatibility: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateMetadata':
        """Create TemplateMetadata from dictionary"""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            type=TemplateType(data.get('type', 'city_page')),
            variant=TemplateVariant(data.get('variant', 'basic')),
            version=data.get('version', '1.0.0'),
            author=data.get('author', ''),
            created_date=data.get('created_date', ''),
            last_modified=data.get('last_modified', ''),
            preview_image=data.get('preview_image', ''),
            template_file=data.get('template_file', ''),
            required_data=data.get('required_data', []),
            optional_data=data.get('optional_data', []),
            features=data.get('features', []),
            compatibility=data.get('compatibility', {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['type'] = self.type.value
        data['variant'] = self.variant.value
        return data


class TemplateManager:
    """Manages template discovery, loading, and metadata"""

    def __init__(self, templates_dir: Optional[Path] = None):
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent.parent / "templates"

        self.templates_dir = Path(templates_dir)
        self.templates_registry: Dict[str, TemplateMetadata] = {}
        self.jinja_env: Optional[jinja2.Environment] = None

        self._initialize_jinja_environment()
        self._discover_templates()

    def _initialize_jinja_environment(self):
        """Initialize Jinja2 environment for template rendering"""
        try:
            loader = jinja2.FileSystemLoader(str(self.templates_dir))
            self.jinja_env = jinja2.Environment(
                loader=loader,
                autoescape=jinja2.select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
        except Exception as e:
            print(f"Error initializing Jinja environment: {e}")
            self.jinja_env = None

    def _discover_templates(self):
        """Discover all available templates and load their metadata"""
        if not self.templates_dir.exists():
            print(f"Templates directory not found: {self.templates_dir}")
            return

        # Look for template metadata files
        for metadata_file in self.templates_dir.rglob("*.template.json"):
            try:
                metadata = self._load_template_metadata(metadata_file)
                if metadata:
                    self.templates_registry[metadata.id] = metadata
            except Exception as e:
                print(f"Error loading template metadata from {metadata_file}: {e}")

        # If no metadata found, create default metadata for existing templates
        if not self.templates_registry:
            self._create_default_metadata()

    def _load_template_metadata(self, metadata_file: Path) -> Optional[TemplateMetadata]:
        """Load template metadata from JSON file"""
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return TemplateMetadata.from_dict(data)
        except Exception as e:
            print(f"Error loading metadata from {metadata_file}: {e}")
            return None

    def _create_default_metadata(self):
        """Create default metadata for existing templates"""
        # Check for the existing SEO Authority template
        seo_template = self.templates_dir / "pages" / "seo_authority_city_page.html"
        if seo_template.exists():
            metadata = TemplateMetadata(
                id="seo_authority_city",
                name="SEO Authority City Page",
                description="Comprehensive SEO-optimized city page template with rich content features, schema markup, and local business optimization.",
                type=TemplateType.CITY_PAGE,
                variant=TemplateVariant.SEO_AUTHORITY,
                version="2.1.0",
                author="Cloud Stack Generator Team",
                created_date="2025-08-15",
                last_modified="2025-09-18",
                preview_image="previews/seo_authority_city_preview.png",
                template_file="pages/seo_authority_city_page.html",
                required_data=[
                    "city_page.city_name",
                    "city_page.title",
                    "business.business_name",
                    "contact.phone",
                    "contact.email"
                ],
                optional_data=[
                    "city_page.city_image",
                    "city_page.places_of_interest",
                    "city_page.city_faq",
                    "city_page.seo_content_body"
                ],
                features=[
                    "Advanced SEO optimization",
                    "Schema.org markup",
                    "Local business data",
                    "Places of interest integration",
                    "FAQ sections",
                    "Wikipedia image embeds",
                    "Responsive design",
                    "Social media meta tags"
                ],
                compatibility={
                    "min_version": "2.0.0",
                    "supports_city_pages": True,
                    "supports_wikipedia": True,
                    "supports_google_maps": True
                }
            )
            self.templates_registry[metadata.id] = metadata

    def get_available_templates(self, template_type: Optional[TemplateType] = None) -> List[TemplateMetadata]:
        """Get list of available templates, optionally filtered by type"""
        templates = list(self.templates_registry.values())
        if template_type:
            templates = [t for t in templates if t.type == template_type]
        return sorted(templates, key=lambda t: (t.variant.value, t.name))

    def get_template_by_id(self, template_id: str) -> Optional[TemplateMetadata]:
        """Get template metadata by ID"""
        return self.templates_registry.get(template_id)

    def get_template_variants(self, template_type: TemplateType) -> List[TemplateVariant]:
        """Get available variants for a template type"""
        variants = set()
        for template in self.templates_registry.values():
            if template.type == template_type:
                variants.add(template.variant)
        return sorted(list(variants), key=lambda v: v.value)

    def load_template(self, template_id: str) -> Optional[jinja2.Template]:
        """Load and return a Jinja2 template object"""
        if not self.jinja_env:
            return None

        metadata = self.get_template_by_id(template_id)
        if not metadata:
            return None

        try:
            return self.jinja_env.get_template(metadata.template_file)
        except Exception as e:
            print(f"Error loading template {template_id}: {e}")
            return None

    def validate_template_data(self, template_id: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate that provided data meets template requirements"""
        metadata = self.get_template_by_id(template_id)
        if not metadata:
            return False, [f"Template {template_id} not found"]

        errors = []

        # Check required data fields
        for required_field in metadata.required_data:
            if not self._check_nested_field(data, required_field):
                errors.append(f"Required field missing: {required_field}")

        return len(errors) == 0, errors

    def _check_nested_field(self, data: Dict[str, Any], field_path: str) -> bool:
        """Check if a nested field exists in the data (e.g., 'city_page.city_name')"""
        parts = field_path.split('.')
        current = data

        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return False
            current = current[part]

        return current is not None and str(current).strip() != ""

    def create_template_metadata_file(self, metadata: TemplateMetadata, output_dir: Optional[Path] = None):
        """Create a metadata file for a template"""
        if output_dir is None:
            output_dir = self.templates_dir

        filename = f"{metadata.id}.template.json"
        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)

    def import_template(self, template_path: Path, metadata: Optional[TemplateMetadata] = None) -> bool:
        """Import a template file and optionally its metadata"""
        try:
            if not template_path.exists():
                return False

            # Generate metadata if not provided
            if metadata is None:
                metadata = self._generate_metadata_from_template(template_path)

            # Copy template file to templates directory
            target_dir = self.templates_dir / "pages"
            target_dir.mkdir(parents=True, exist_ok=True)

            target_file = target_dir / template_path.name
            with open(template_path, 'r', encoding='utf-8') as src:
                content = src.read()

            with open(target_file, 'w', encoding='utf-8') as dst:
                dst.write(content)

            # Update metadata with correct file path
            metadata.template_file = f"pages/{template_path.name}"

            # Create metadata file
            self.create_template_metadata_file(metadata)

            # Add to registry
            self.templates_registry[metadata.id] = metadata

            return True
        except Exception as e:
            print(f"Error importing template: {e}")
            return False

    def _generate_metadata_from_template(self, template_path: Path) -> TemplateMetadata:
        """Generate basic metadata from a template file"""
        name = template_path.stem.replace('_', ' ').title()
        template_id = template_path.stem.lower()

        return TemplateMetadata(
            id=template_id,
            name=name,
            description=f"Imported template: {name}",
            type=TemplateType.CITY_PAGE,
            variant=TemplateVariant.CUSTOM,
            version="1.0.0",
            author="Imported",
            created_date="2025-09-18",
            last_modified="2025-09-18",
            preview_image="",
            template_file=f"pages/{template_path.name}",
            required_data=[],
            optional_data=[],
            features=["Custom template"],
            compatibility={}
        )

    def export_template(self, template_id: str, export_dir: Path) -> bool:
        """Export a template and its metadata"""
        try:
            metadata = self.get_template_by_id(template_id)
            if not metadata:
                return False

            # Copy template file
            source_file = self.templates_dir / metadata.template_file
            if not source_file.exists():
                return False

            export_dir.mkdir(parents=True, exist_ok=True)

            # Copy template
            target_file = export_dir / source_file.name
            with open(source_file, 'r', encoding='utf-8') as src:
                content = src.read()

            with open(target_file, 'w', encoding='utf-8') as dst:
                dst.write(content)

            # Export metadata
            metadata_file = export_dir / f"{template_id}.template.json"
            self.create_template_metadata_file(metadata, export_dir.parent)

            return True
        except Exception as e:
            print(f"Error exporting template: {e}")
            return False

    def get_template_preview_data(self, template_id: str) -> Dict[str, Any]:
        """Get sample data for template preview"""
        metadata = self.get_template_by_id(template_id)
        if not metadata:
            return {}

        # Return sample data based on template type
        if metadata.type == TemplateType.CITY_PAGE:
            return self._get_city_page_preview_data()

        return {}

    def _get_city_page_preview_data(self) -> Dict[str, Any]:
        """Get sample data for city page template preview"""
        return {
            "city_page": {
                "city_name": "Sample City",
                "state": "Illinois",
                "title": "Sample City Services | Your Business Name",
                "meta_description": "Professional services in Sample City, Illinois. Quality work and customer satisfaction guaranteed.",
                "hero_title": "Trusted Sample City Services",
                "about_city": "Sample City is a vibrant community known for its commitment to quality and excellence.",
                "city_image": {
                    "image_url": "/images/sample-city.jpg",
                    "alt_text": "View of Sample City",
                    "caption": "Sample City - A great place for business"
                }
            },
            "business": {
                "business_name": "Your Business Name",
                "industry": "Professional Services"
            },
            "contact": {
                "phone": "(555) 123-4567",
                "email": "info@yourbusiness.com",
                "address": {
                    "street": "123 Main St",
                    "city": "Sample City",
                    "state": "IL",
                    "zip_code": "60601"
                }
            },
            "services": [
                {"name": "Service 1", "description": "Professional service description"},
                {"name": "Service 2", "description": "Quality service offering"}
            ]
        }