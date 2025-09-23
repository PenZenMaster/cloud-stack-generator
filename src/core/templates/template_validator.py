"""
Template Validator - Comprehensive template validation system
Path: E:/projects/cloud-stack-generator/src/core/templates/template_validator.py

Description:
Provides comprehensive validation for HTML templates including syntax checking,
Jinja2 template validation, data field validation, and best practices enforcement.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-22

Last Modified Date:
2025-09-22

Comments:
* v1.00 - Initial template validation system
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import re
import html
from pathlib import Path

try:
    from jinja2 import Environment, Template, TemplateSyntaxError, meta, DictLoader
    from jinja2.exceptions import UndefinedError
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

try:
    from bs4 import BeautifulSoup, Comment
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class ValidationLevel(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationCategory(Enum):
    """Validation categories"""
    SYNTAX = "syntax"
    STRUCTURE = "structure"
    SEO = "seo"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BEST_PRACTICES = "best_practices"
    DATA_BINDING = "data_binding"


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    level: ValidationLevel
    category: ValidationCategory
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    code: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Template validation result"""
    is_valid: bool
    issues: List[ValidationIssue]
    warnings_count: int
    errors_count: int
    template_variables: Set[str]
    required_data: Set[str]
    optional_data: Set[str]

    def get_issues_by_level(self, level: ValidationLevel) -> List[ValidationIssue]:
        """Get issues by severity level"""
        return [issue for issue in self.issues if issue.level == level]

    def get_issues_by_category(self, category: ValidationCategory) -> List[ValidationIssue]:
        """Get issues by category"""
        return [issue for issue in self.issues if issue.category == category]


class TemplateValidator:
    """Comprehensive template validator"""

    def __init__(self):
        component_templates = self._load_component_templates() if JINJA2_AVAILABLE else {}
        self.jinja_env = Environment(loader=DictLoader(component_templates)) if JINJA2_AVAILABLE else None

        # Add custom filters if Jinja2 is available
        if self.jinja_env:
            self.jinja_env.filters['slugify'] = self._slugify_filter
            self.jinja_env.filters['date'] = self._date_filter
            self.jinja_env.filters['urlencode'] = self._urlencode_filter
            self.jinja_env.filters['markdown_basic'] = self._markdown_basic_filter
        self.html_tags = self._load_html_tags()
        self.seo_meta_tags = {
            'title', 'description', 'keywords', 'author', 'viewport',
            'og:title', 'og:description', 'og:type', 'og:url', 'og:image',
            'twitter:card', 'twitter:title', 'twitter:description', 'twitter:image'
        }

    def _load_component_templates(self) -> Dict[str, str]:
        """Load component templates for includes"""
        component_templates = {}
        try:
            # Get templates directory
            templates_dir = Path(__file__).parent.parent.parent / "templates"
            components_dir = templates_dir / "components"

            if components_dir.exists():
                # Load all .html files from components directory
                for component_file in components_dir.glob("*.html"):
                    try:
                        with open(component_file, 'r', encoding='utf-8') as f:
                            # Use relative path as key (e.g., 'components/header.html')
                            key = f"components/{component_file.name}"
                            component_templates[key] = f.read()
                    except Exception as e:
                        print(f"Error loading component {component_file}: {e}")

                # Also add common component names without the 'components/' prefix for compatibility
                for key, content in list(component_templates.items()):
                    if key.startswith('components/'):
                        simple_key = key.replace('components/', '')
                        component_templates[simple_key] = content

        except Exception as e:
            print(f"Error loading component templates: {e}")

        return component_templates

    def _slugify_filter(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        import re
        if not text:
            return ""
        slug = re.sub(r"[^\w\s-]", "", str(text).lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")

    def _date_filter(self, date_input, format_str="%Y-%m-%d"):
        """Format date string - supports 'now' keyword for current date"""
        from datetime import datetime

        if isinstance(date_input, str) and date_input.lower() == "now":
            return datetime.now().strftime(format_str)
        elif isinstance(date_input, datetime):
            return date_input.strftime(format_str)
        else:
            try:
                date_obj = datetime.fromisoformat(str(date_input))
                return date_obj.strftime(format_str)
            except:
                return str(date_input)

    def _urlencode_filter(self, text: str) -> str:
        """URL encode text"""
        from urllib.parse import quote
        if not text:
            return ""
        return quote(str(text))

    def _markdown_basic_filter(self, text: str) -> str:
        """Basic markdown to HTML conversion"""
        if not text:
            return ""
        # Simple markdown conversion for common cases
        text = str(text)
        text = text.replace('\n\n', '</p><p>')
        text = text.replace('\n', '<br>')
        if not text.startswith('<p>'):
            text = '<p>' + text
        if not text.endswith('</p>'):
            text = text + '</p>'
        return text

    def validate_template(self, template_content: str, template_metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Perform comprehensive template validation

        Args:
            template_content: The template HTML content
            template_metadata: Optional template metadata for additional validation

        Returns:
            ValidationResult with all validation issues
        """
        issues = []
        template_variables = set()
        required_data = set()
        optional_data = set()

        # Basic syntax validation
        syntax_issues, jinja_vars = self._validate_syntax(template_content)
        issues.extend(syntax_issues)
        template_variables.update(jinja_vars)

        # HTML structure validation
        structure_issues = self._validate_html_structure(template_content)
        issues.extend(structure_issues)

        # SEO validation
        seo_issues = self._validate_seo(template_content)
        issues.extend(seo_issues)

        # Accessibility validation
        accessibility_issues = self._validate_accessibility(template_content)
        issues.extend(accessibility_issues)

        # Performance validation
        performance_issues = self._validate_performance(template_content)
        issues.extend(performance_issues)

        # Security validation
        security_issues = self._validate_security(template_content)
        issues.extend(security_issues)

        # Best practices validation
        best_practices_issues = self._validate_best_practices(template_content)
        issues.extend(best_practices_issues)

        # Data binding validation
        data_issues, req_data, opt_data = self._validate_data_binding(template_content, template_metadata)
        issues.extend(data_issues)
        required_data.update(req_data)
        optional_data.update(opt_data)

        # Count issues by severity
        errors_count = len([i for i in issues if i.level == ValidationLevel.ERROR])
        warnings_count = len([i for i in issues if i.level == ValidationLevel.WARNING])

        return ValidationResult(
            is_valid=errors_count == 0,
            issues=issues,
            warnings_count=warnings_count,
            errors_count=errors_count,
            template_variables=template_variables,
            required_data=required_data,
            optional_data=optional_data
        )

    def _validate_syntax(self, template_content: str) -> Tuple[List[ValidationIssue], Set[str]]:
        """Validate HTML and Jinja2 syntax"""
        issues = []
        variables = set()

        if not JINJA2_AVAILABLE:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.SYNTAX,
                message="Jinja2 not available - skipping template syntax validation"
            ))
            return issues, variables

        try:
            # Parse Jinja2 template
            ast = self.jinja_env.parse(template_content)
            variables = meta.find_undeclared_variables(ast)

            # Try to compile template
            template = self.jinja_env.from_string(template_content)

        except TemplateSyntaxError as e:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category=ValidationCategory.SYNTAX,
                message=f"Jinja2 syntax error: {e.message}",
                line_number=e.lineno,
                code="JINJA_SYNTAX_ERROR",
                suggestion="Check template syntax for missing brackets, filters, or tags"
            ))

        except Exception as e:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category=ValidationCategory.SYNTAX,
                message=f"Template parsing error: {str(e)}",
                code="TEMPLATE_PARSE_ERROR"
            ))

        # Basic HTML syntax validation
        if not template_content.strip():
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category=ValidationCategory.SYNTAX,
                message="Template is empty",
                code="EMPTY_TEMPLATE"
            ))

        # Check for unclosed tags (basic check)
        unclosed_tags = self._find_unclosed_html_tags(template_content)
        for tag in unclosed_tags:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category=ValidationCategory.SYNTAX,
                message=f"Unclosed HTML tag: <{tag}>",
                code="UNCLOSED_TAG",
                suggestion=f"Add closing tag </{tag}>"
            ))

        return issues, variables

    def _validate_html_structure(self, template_content: str) -> List[ValidationIssue]:
        """Validate HTML document structure"""
        issues = []

        # Check for DOCTYPE
        if '<!DOCTYPE' not in template_content.upper():
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.STRUCTURE,
                message="Missing DOCTYPE declaration",
                code="NO_DOCTYPE",
                suggestion="Add '<!DOCTYPE html>' at the beginning of the template"
            ))

        # Check for basic HTML structure
        required_elements = {
            '<html': 'HTML root element',
            '<head': 'HEAD section',
            '<body': 'BODY section'
        }

        for element, description in required_elements.items():
            if element not in template_content.lower():
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category=ValidationCategory.STRUCTURE,
                    message=f"Missing {description}",
                    code="MISSING_ELEMENT",
                    suggestion=f"Add {element}> element to template"
                ))

        # Check for charset declaration
        if 'charset=' not in template_content.lower():
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.STRUCTURE,
                message="Missing charset declaration",
                code="NO_CHARSET",
                suggestion="Add <meta charset='UTF-8'> in the head section"
            ))

        # Check for viewport meta tag (responsive design)
        if 'viewport' not in template_content.lower():
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.STRUCTURE,
                message="Missing viewport meta tag for responsive design",
                code="NO_VIEWPORT",
                suggestion="Add <meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            ))

        return issues

    def _validate_seo(self, template_content: str) -> List[ValidationIssue]:
        """Validate SEO-related elements"""
        issues = []

        # Check for title tag
        if not re.search(r'<title[^>]*>.*?</title>', template_content, re.IGNORECASE | re.DOTALL):
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category=ValidationCategory.SEO,
                message="Missing title tag",
                code="NO_TITLE",
                suggestion="Add <title> tag in the head section"
            ))

        # Check for meta description
        if not re.search(r'<meta[^>]*name=["\']description["\'][^>]*>', template_content, re.IGNORECASE):
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.SEO,
                message="Missing meta description",
                code="NO_META_DESCRIPTION",
                suggestion="Add <meta name='description' content='...'> for SEO"
            ))

        # Check for heading structure
        h1_count = len(re.findall(r'<h1[^>]*>', template_content, re.IGNORECASE))
        if h1_count == 0:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.SEO,
                message="No H1 heading found",
                code="NO_H1",
                suggestion="Add an H1 heading for better SEO structure"
            ))
        elif h1_count > 1:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.SEO,
                message=f"Multiple H1 headings found ({h1_count})",
                code="MULTIPLE_H1",
                suggestion="Use only one H1 heading per page"
            ))

        # Check for alt attributes on images
        img_tags = re.findall(r'<img[^>]*>', template_content, re.IGNORECASE)
        for img_tag in img_tags:
            if 'alt=' not in img_tag.lower():
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category=ValidationCategory.SEO,
                    message="Image missing alt attribute",
                    code="IMG_NO_ALT",
                    suggestion="Add alt attribute to all images for accessibility and SEO"
                ))

        return issues

    def _validate_accessibility(self, template_content: str) -> List[ValidationIssue]:
        """Validate accessibility features"""
        issues = []

        # Check for lang attribute on html element
        if not re.search(r'<html[^>]*lang=["\'][^"\']*["\']', template_content, re.IGNORECASE):
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.ACCESSIBILITY,
                message="Missing lang attribute on html element",
                code="NO_LANG",
                suggestion="Add lang='en' (or appropriate language) to html element"
            ))

        # Check for form labels
        input_tags = re.findall(r'<input[^>]*>', template_content, re.IGNORECASE)
        for input_tag in input_tags:
            if 'type=' in input_tag.lower() and 'type="hidden"' not in input_tag.lower():
                # Check if input has id and corresponding label
                input_id_match = re.search(r'id=["\']([^"\']*)["\']', input_tag, re.IGNORECASE)
                if input_id_match:
                    input_id = input_id_match.group(1)
                    label_pattern = f'<label[^>]*for=["\']?{re.escape(input_id)}["\']?[^>]*>'
                    if not re.search(label_pattern, template_content, re.IGNORECASE):
                        issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            category=ValidationCategory.ACCESSIBILITY,
                            message=f"Input field missing associated label (id: {input_id})",
                            code="INPUT_NO_LABEL",
                            suggestion=f"Add <label for='{input_id}'>...</label> for the input field"
                        ))

        # Check for heading hierarchy
        headings = re.findall(r'<h([1-6])[^>]*>', template_content, re.IGNORECASE)
        if headings:
            heading_levels = [int(h) for h in headings]
            for i in range(1, len(heading_levels)):
                if heading_levels[i] - heading_levels[i-1] > 1:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category=ValidationCategory.ACCESSIBILITY,
                        message="Heading hierarchy skips levels",
                        code="HEADING_SKIP",
                        suggestion="Use headings in sequential order (h1, h2, h3, etc.)"
                    ))

        return issues

    def _validate_performance(self, template_content: str) -> List[ValidationIssue]:
        """Validate performance-related aspects"""
        issues = []

        # Check for inline styles (should be minimal)
        inline_styles = re.findall(r'style=["\'][^"\']*["\']', template_content, re.IGNORECASE)
        if len(inline_styles) > 5:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.PERFORMANCE,
                message=f"Many inline styles found ({len(inline_styles)})",
                code="MANY_INLINE_STYLES",
                suggestion="Consider moving styles to external CSS file or <style> block"
            ))

        # Check for large embedded CSS
        style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', template_content, re.IGNORECASE | re.DOTALL)
        for style_block in style_blocks:
            if len(style_block) > 5000:  # 5KB threshold
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category=ValidationCategory.PERFORMANCE,
                    message="Large embedded CSS block",
                    code="LARGE_CSS_BLOCK",
                    suggestion="Consider moving large CSS to external file"
                ))

        # Check for unoptimized images (basic check)
        img_tags = re.findall(r'<img[^>]*src=["\']([^"\']*)["\'][^>]*>', template_content, re.IGNORECASE)
        for img_src in img_tags:
            if any(ext in img_src.lower() for ext in ['.bmp', '.tiff', '.tif']):
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category=ValidationCategory.PERFORMANCE,
                    message=f"Unoptimized image format: {img_src}",
                    code="UNOPTIMIZED_IMAGE",
                    suggestion="Use optimized formats like WebP, JPEG, or PNG"
                ))

        return issues

    def _validate_security(self, template_content: str) -> List[ValidationIssue]:
        """Validate security aspects"""
        issues = []

        # Check for potential XSS vulnerabilities in Jinja2 templates
        unsafe_patterns = [
            r'\{\{\s*[^|]*\s*\|\s*safe\s*\}\}',  # |safe filter
            r'\{\{\s*[^|]*\s*\|\s*raw\s*\}\}',   # |raw filter
        ]

        for pattern in unsafe_patterns:
            matches = re.findall(pattern, template_content, re.IGNORECASE)
            for match in matches:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category=ValidationCategory.SECURITY,
                    message=f"Potential XSS risk with unsafe filter: {match}",
                    code="UNSAFE_FILTER",
                    suggestion="Ensure user input is properly sanitized before using |safe or |raw filters"
                ))

        # Check for inline JavaScript (potential security risk)
        inline_js = re.findall(r'on\w+\s*=\s*["\'][^"\']*["\']', template_content, re.IGNORECASE)
        if inline_js:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.SECURITY,
                message=f"Inline JavaScript event handlers found ({len(inline_js)})",
                code="INLINE_JS",
                suggestion="Consider using external JavaScript files and CSP-safe event handling"
            ))

        return issues

    def _validate_best_practices(self, template_content: str) -> List[ValidationIssue]:
        """Validate coding best practices"""
        issues = []

        # Check for TODO/FIXME comments
        todo_patterns = [r'TODO', r'FIXME', r'HACK', r'XXX']
        for pattern in todo_patterns:
            matches = re.findall(pattern, template_content, re.IGNORECASE)
            if matches:
                issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    category=ValidationCategory.BEST_PRACTICES,
                    message=f"{pattern} comments found in template",
                    code="TODO_COMMENTS",
                    suggestion="Address TODO/FIXME comments before production use"
                ))

        # Check for hardcoded values that should be templated
        hardcoded_patterns = [
            (r'href=["\']mailto:[^"\']*["\']', "Email addresses should be templated"),
            (r'href=["\']tel:[^"\']*["\']', "Phone numbers should be templated"),
            (r'<title>[^{]*</title>', "Page titles should be templated"),
        ]

        for pattern, message in hardcoded_patterns:
            if re.search(pattern, template_content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    category=ValidationCategory.BEST_PRACTICES,
                    message=message,
                    code="HARDCODED_VALUE",
                    suggestion="Use template variables for dynamic content"
                ))

        return issues

    def _validate_data_binding(self, template_content: str, template_metadata: Optional[Dict[str, Any]] = None) -> Tuple[List[ValidationIssue], Set[str], Set[str]]:
        """Validate data binding and template variables"""
        issues = []
        required_data = set()
        optional_data = set()

        if not JINJA2_AVAILABLE:
            return issues, required_data, optional_data

        try:
            # Extract all template variables
            ast = self.jinja_env.parse(template_content)
            all_variables = meta.find_undeclared_variables(ast)

            # If metadata is provided, validate against declared fields
            if template_metadata:
                declared_required = set(template_metadata.get('required_data', []))
                declared_optional = set(template_metadata.get('optional_data', []))

                # Check for variables not declared in metadata
                undeclared_vars = all_variables - declared_required - declared_optional
                for var in undeclared_vars:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category=ValidationCategory.DATA_BINDING,
                        message=f"Template variable '{var}' not declared in metadata",
                        code="UNDECLARED_VARIABLE",
                        suggestion=f"Add '{var}' to required_data or optional_data in template metadata"
                    ))

                # Check for declared variables not used in template
                unused_required = declared_required - all_variables
                for var in unused_required:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category=ValidationCategory.DATA_BINDING,
                        message=f"Required data field '{var}' not used in template",
                        code="UNUSED_REQUIRED",
                        suggestion=f"Either use '{var}' in template or move to optional_data"
                    ))

                unused_optional = declared_optional - all_variables
                for var in unused_optional:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.INFO,
                        category=ValidationCategory.DATA_BINDING,
                        message=f"Optional data field '{var}' not used in template",
                        code="UNUSED_OPTIONAL",
                        suggestion=f"Consider removing '{var}' from optional_data if not needed"
                    ))

                required_data = declared_required
                optional_data = declared_optional
            else:
                # Without metadata, all variables are considered optional
                optional_data = all_variables

        except Exception as e:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category=ValidationCategory.DATA_BINDING,
                message=f"Error analyzing template variables: {str(e)}",
                code="VARIABLE_ANALYSIS_ERROR"
            ))

        return issues, required_data, optional_data

    def _find_unclosed_html_tags(self, content: str) -> List[str]:
        """Find unclosed HTML tags (basic implementation)"""
        # This is a simplified check - a full parser would be more accurate
        open_tags = []
        tag_pattern = r'<(/?)(\w+)[^>]*/?>'

        for match in re.finditer(tag_pattern, content, re.IGNORECASE):
            is_closing = match.group(1) == '/'
            tag_name = match.group(2).lower()
            is_self_closing = match.group(0).endswith('/>')

            # Skip self-closing tags and void elements
            void_elements = {
                'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                'link', 'meta', 'param', 'source', 'track', 'wbr'
            }

            if tag_name in void_elements or is_self_closing:
                continue

            if is_closing:
                if open_tags and open_tags[-1] == tag_name:
                    open_tags.pop()
            else:
                open_tags.append(tag_name)

        return open_tags

    def _load_html_tags(self) -> Set[str]:
        """Load standard HTML tags"""
        return {
            'a', 'abbr', 'acronym', 'address', 'applet', 'area', 'article', 'aside', 'audio',
            'b', 'base', 'basefont', 'bdo', 'big', 'blockquote', 'body', 'br', 'button',
            'canvas', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'command',
            'datalist', 'dd', 'del', 'details', 'dfn', 'dir', 'div', 'dl', 'dt',
            'em', 'embed', 'fieldset', 'figcaption', 'figure', 'font', 'footer', 'form', 'frame', 'frameset',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hgroup', 'hr', 'html',
            'i', 'iframe', 'img', 'input', 'ins', 'isindex', 'kbd', 'keygen', 'label', 'legend', 'li', 'link',
            'map', 'mark', 'menu', 'meta', 'meter', 'nav', 'noframes', 'noscript',
            'object', 'ol', 'optgroup', 'option', 'output', 'p', 'param', 'pre', 'progress',
            'q', 'rp', 'rt', 'ruby', 's', 'samp', 'script', 'section', 'select', 'small',
            'source', 'span', 'strike', 'strong', 'style', 'sub', 'summary', 'sup',
            'table', 'tbody', 'td', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'track', 'tt',
            'u', 'ul', 'var', 'video', 'wbr'
        }

    def validate_template_file(self, file_path: Path, metadata_path: Optional[Path] = None) -> ValidationResult:
        """
        Validate a template file

        Args:
            file_path: Path to the template file
            metadata_path: Optional path to metadata file

        Returns:
            ValidationResult
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            metadata = None
            if metadata_path and metadata_path.exists():
                import json
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

            return self.validate_template(template_content, metadata)

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category=ValidationCategory.SYNTAX,
                    message=f"Error reading template file: {str(e)}",
                    code="FILE_READ_ERROR"
                )],
                warnings_count=0,
                errors_count=1,
                template_variables=set(),
                required_data=set(),
                optional_data=set()
            )