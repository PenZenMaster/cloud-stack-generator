"""
Template Preview System
Path: E:/projects/cloud-stack-generator/src/core/templates/template_preview.py

Description:
Generates preview HTML for templates with sample data to allow users
to see how templates will look before selection.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-18

Last Modified Date:
2025-09-18

Comments:
* v1.00 - Initial template preview system
"""

from typing import Dict, Any, Optional
from pathlib import Path
import base64
from .template_manager import TemplateManager
from src.core.utils.logger import get_logger

logger = get_logger(__name__)


class TemplatePreviewGenerator:
    """Generates preview HTML for templates"""

    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager

    def generate_preview_html(self, template_id: str, custom_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Generate preview HTML for a template

        Args:
            template_id: ID of the template to preview
            custom_data: Optional custom data to use instead of sample data

        Returns:
            Rendered HTML string or None if error
        """
        try:
            # Load the template
            template = self.template_manager.load_template(template_id)
            if not template:
                return None

            # Get preview data
            if custom_data:
                data = custom_data
            else:
                data = self.template_manager.get_template_preview_data(template_id)

            # Add preview-specific styling and indicators
            data.update(self._get_preview_enhancements())

            # Render the template
            rendered_html = template.render(**data)

            # Add preview-specific CSS and overlays
            preview_html = self._enhance_preview_html(rendered_html, template_id)

            return preview_html

        except Exception as e:
            logger.error(f"Error generating preview for template {template_id}: {e}")
            return None

    def _get_preview_enhancements(self) -> Dict[str, Any]:
        """Get additional data for preview enhancement"""
        return {
            "preview_mode": True,
            "page_url": "https://example.com/sample-city",
            "current_year": "2025",
            "timestamp": "2025-09-18",
        }

    def _enhance_preview_html(self, html: str, template_id: str) -> str:
        """Add preview-specific enhancements to the HTML"""
        # Add preview overlay CSS
        preview_css = """
        <style>
        .template-preview-overlay {
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            z-index: 9999;
            font-family: Arial, sans-serif;
            font-size: 14px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }

        .template-preview-overlay h4 {
            margin: 0 0 5px 0;
            font-size: 16px;
        }

        .template-preview-overlay p {
            margin: 0;
            font-size: 12px;
            opacity: 0.8;
        }

        .preview-sample-data {
            border: 2px dashed #3498db;
            background-color: rgba(52, 152, 219, 0.1);
            position: relative;
        }

        .preview-sample-data::before {
            content: "Sample Data";
            position: absolute;
            top: -10px;
            left: 10px;
            background: #3498db;
            color: white;
            padding: 2px 8px;
            font-size: 10px;
            border-radius: 3px;
            z-index: 1000;
        }

        body {
            position: relative;
        }
        </style>
        """

        # Create preview overlay
        metadata = self.template_manager.get_template_by_id(template_id)
        template_name = metadata.name if metadata else template_id

        preview_overlay = f"""
        <div class="template-preview-overlay">
            <h4>Template Preview</h4>
            <p>{template_name}</p>
            <p>This is a preview with sample data</p>
        </div>
        """

        # Insert CSS and overlay into the HTML
        if "</head>" in html:
            html = html.replace("</head>", f"{preview_css}</head>")
        elif "<head>" in html:
            html = html.replace("<head>", f"<head>{preview_css}")
        else:
            html = f"{preview_css}{html}"

        if "</body>" in html:
            html = html.replace("</body>", f"{preview_overlay}</body>")
        else:
            html = f"{html}{preview_overlay}"

        return html

    def generate_preview_thumbnail(self, template_id: str, width: int = 400, height: int = 300) -> Optional[str]:
        """
        Generate a thumbnail image for template preview

        Args:
            template_id: ID of the template
            width: Thumbnail width
            height: Thumbnail height

        Returns:
            Base64 encoded image data or None if error
        """
        try:
            # For now, generate a simple HTML-based thumbnail
            # In a full implementation, this could use a headless browser
            # to capture actual screenshots

            html = self.generate_preview_html(template_id)
            if not html:
                return None

            # Create a simplified version for thumbnail
            self._create_thumbnail_html(template_id, width, height)

            # For now, return a placeholder data URL
            # In production, this would render the HTML to an image
            return self._create_placeholder_thumbnail(template_id, width, height)

        except Exception as e:
            logger.error(f"Error generating thumbnail for template {template_id}: {e}")
            return None

    def _create_thumbnail_html(self, template_id: str, width: int, height: int) -> str:
        """Create HTML specifically for thumbnail generation"""
        metadata = self.template_manager.get_template_by_id(template_id)
        if not metadata:
            return ""

        # Create a simplified preview for thumbnail
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    width: {width}px;
                    height: {height}px;
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    text-align: center;
                }}
                h1 {{ margin: 0 0 10px 0; font-size: 24px; }}
                p {{ margin: 5px 0; font-size: 14px; opacity: 0.9; }}
                .features {{ font-size: 12px; opacity: 0.7; }}
            </style>
        </head>
        <body>
            <h1>{metadata.name}</h1>
            <p>{metadata.variant.value.title()}</p>
            <p class="features">{len(metadata.features)} Features</p>
            <p class="features">v{metadata.version}</p>
        </body>
        </html>
        """

    def _create_placeholder_thumbnail(self, template_id: str, width: int, height: int) -> str:
        """Create a placeholder thumbnail as base64 data URL"""
        # This is a simple SVG placeholder
        # In production, you'd use a proper HTML-to-image converter

        metadata = self.template_manager.get_template_by_id(template_id)
        template_name = metadata.name if metadata else template_id

        svg_content = f"""
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#grad1)" />
            <text x="50%" y="40%" dominant-baseline="middle" text-anchor="middle"
                  fill="white" font-family="Arial" font-size="18" font-weight="bold">
                {template_name}
            </text>
            <text x="50%" y="60%" dominant-baseline="middle" text-anchor="middle"
                  fill="white" font-family="Arial" font-size="12" opacity="0.8">
                Template Preview
            </text>
            <text x="50%" y="75%" dominant-baseline="middle" text-anchor="middle"
                  fill="white" font-family="Arial" font-size="10" opacity="0.6">
                {metadata.variant.value.title() if metadata else 'Custom'}
            </text>
        </svg>
        """

        # Encode SVG as base64 data URL
        svg_bytes = svg_content.encode('utf-8')
        svg_base64 = base64.b64encode(svg_bytes).decode('utf-8')
        return f"data:image/svg+xml;base64,{svg_base64}"

    def save_preview_to_file(self, template_id: str, output_path: Path,
                           custom_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save template preview HTML to a file

        Args:
            template_id: ID of the template
            output_path: Path where to save the preview
            custom_data: Optional custom data for preview

        Returns:
            True if successful, False otherwise
        """
        try:
            html = self.generate_preview_html(template_id, custom_data)
            if not html:
                return False

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

            return True

        except Exception as e:
            logger.error(f"Error saving preview to {output_path}: {e}")
            return False

    def get_template_comparison_html(self, template_ids: list) -> Optional[str]:
        """
        Generate side-by-side comparison of multiple templates

        Args:
            template_ids: List of template IDs to compare

        Returns:
            HTML with side-by-side template previews
        """
        try:
            if not template_ids:
                return None

            comparison_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Template Comparison</title>
                <style>
                    body {
                        margin: 0;
                        padding: 20px;
                        font-family: Arial, sans-serif;
                        background: #f5f5f5;
                    }
                    .comparison-container {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                        gap: 20px;
                        max-width: 1400px;
                        margin: 0 auto;
                    }
                    .template-preview-frame {
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }
                    .template-header {
                        background: #2c3e50;
                        color: white;
                        padding: 15px;
                        text-align: center;
                    }
                    .template-content {
                        height: 600px;
                        overflow: auto;
                        border: 1px solid #ddd;
                    }
                    iframe {
                        width: 100%;
                        height: 100%;
                        border: none;
                    }
                </style>
            </head>
            <body>
                <h1 style="text-align: center; color: #2c3e50;">Template Comparison</h1>
                <div class="comparison-container">
            """

            for template_id in template_ids:
                metadata = self.template_manager.get_template_by_id(template_id)
                template_name = metadata.name if metadata else template_id

                preview_html = self.generate_preview_html(template_id)
                if preview_html:
                    # Encode preview HTML for iframe
                    preview_base64 = base64.b64encode(preview_html.encode('utf-8')).decode('utf-8')
                    data_url = f"data:text/html;base64,{preview_base64}"

                    comparison_html += f"""
                    <div class="template-preview-frame">
                        <div class="template-header">
                            <h3 style="margin: 0;">{template_name}</h3>
                            <p style="margin: 5px 0 0 0; opacity: 0.8; font-size: 14px;">
                                {metadata.variant.value.title() if metadata else 'Custom'} Template
                            </p>
                        </div>
                        <div class="template-content">
                            <iframe src="{data_url}"></iframe>
                        </div>
                    </div>
                    """

            comparison_html += """
                </div>
            </body>
            </html>
            """

            return comparison_html

        except Exception as e:
            logger.error(f"Error generating template comparison: {e}")
            return None

    def generate_preview(self, template_content: str, sample_data: dict) -> 'TemplatePreviewResult':
        """
        Generate preview HTML from template content and sample data

        Args:
            template_content: Jinja2 template content
            sample_data: Data to render template with

        Returns:
            TemplatePreviewResult with success status and rendered HTML or error details
        """
        try:
            import jinja2
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from utils.error_classification import classify_and_handle_error

            # Create Jinja2 environment
            env = jinja2.Environment(
                loader=jinja2.DictLoader({'template': template_content}),
                autoescape=jinja2.select_autoescape(['html', 'xml'])
            )

            # Render template
            template = env.get_template('template')
            rendered_html = template.render(sample_data)

            return TemplatePreviewResult(True, rendered_html)

        except Exception as e:
            # Template rendering error - classify as interface warning
            classification = classify_and_handle_error(
                exception=e,
                context="Preview generation",
                user_action="Generating template preview",
                component="TemplatePreviewGenerator"
            )

            return TemplatePreviewResult(False, "", classification)


class TemplatePreviewResult:
    """Result object for template preview operations"""

    def __init__(self, success: bool, html_content: str = "", error_classification=None):
        self.success = success
        self.html_content = html_content
        self.error_classification = error_classification