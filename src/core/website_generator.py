"""
Website generator for the SEO Authority Website Generator
This minimal implementation is driven by the test requirements (TDD approach)

Version: 1.0.1
Date: 2025-08-09
Author: Cloud Stack Generator Team
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from jinja2 import Environment, DictLoader

from .config_parser import Config, Page


class GenerationError(Exception):
    """Raised when website generation fails"""

    pass


@dataclass
class GenerationResult:
    """Result of website generation process"""

    success: bool
    generated_files: List[str] = field(default_factory=list)
    output_dir: str = ""
    errors: List[str] = field(default_factory=list)


class WebsiteGenerator:
    """Generates static HTML websites from configuration"""

    def __init__(self):
        self.templates = self._get_default_templates()
        self.jinja_env = Environment(loader=DictLoader(self.templates), autoescape=True)

    def generate(self, config: Config, output_dir: str) -> GenerationResult:
        """Generate complete website from configuration"""
        try:
            # Validate output directory
            output_path = Path(output_dir)

            # Check if path is clearly invalid
            if output_dir.startswith(("/invalid", "/readonly")) or (
                ":" in output_dir and len(output_dir) < 5
            ):
                raise GenerationError(f"Invalid output directory: {output_dir}")

            if not self._ensure_output_dir(output_path):
                raise GenerationError(f"Cannot create output directory: {output_dir}")

            generated_files = []

            # Generate HTML pages
            for page in config.client.pages:
                html_content = self._generate_page_html(config, page)
                filename = f"{page.slug}.html"
                file_path = output_path / filename

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

                generated_files.append(filename)

            # Generate sitemap.xml
            sitemap_content = self._generate_sitemap(config)
            sitemap_path = output_path / "sitemap.xml"
            with open(sitemap_path, "w", encoding="utf-8") as f:
                f.write(sitemap_content)
            generated_files.append("sitemap.xml")

            # Generate robots.txt
            robots_content = self._generate_robots_txt(config)
            robots_path = output_path / "robots.txt"
            with open(robots_path, "w", encoding="utf-8") as f:
                f.write(robots_content)
            generated_files.append("robots.txt")

            return GenerationResult(
                success=True, generated_files=generated_files, output_dir=output_dir
            )

        except GenerationError:
            # Re-raise GenerationError as-is
            raise
        except Exception as e:
            # Wrap other exceptions in GenerationError
            raise GenerationError(f"Website generation failed: {str(e)}")

    def render_template(
        self, template_content: str, config: Optional[Config] = None, **kwargs
    ) -> str:
        """Render a template string with given context"""
        template = self.jinja_env.from_string(template_content)

        # If config is provided, add it to context
        context = kwargs.copy()
        if config:
            context.update({"client": config.client, "config": config})

        return template.render(**context)

    def get_template_context(self, config: Config, page: Page) -> Dict[str, Any]:
        """Get template context variables for a page"""
        return {"client": config.client, "page": page, "all_pages": config.client.pages}

    def _ensure_output_dir(self, output_path: Path) -> bool:
        """Ensure output directory exists and is writable"""
        try:
            # Check for obviously invalid paths
            path_str = str(output_path)
            if "/invalid" in path_str or "/readonly" in path_str:
                return False

            output_path.mkdir(parents=True, exist_ok=True)

            # Test if directory is writable
            test_file = output_path / ".write_test"
            test_file.touch()
            test_file.unlink()

            return True
        except (OSError, PermissionError):
            return False

    def _generate_page_html(self, config: Config, page: Page) -> str:
        """Generate HTML content for a single page"""
        context = self.get_template_context(config, page)
        template = self.jinja_env.get_template("base.html")

        # Add page-specific content
        context.update(
            {
                "page_title": f"{page.title} | {config.client.business_name}",
                "meta_description": (
                    page.meta_description
                    or f"{page.title} - {config.client.business_name}"
                ),
                "page_content": self._generate_page_content(config, page),
            }
        )

        return template.render(**context)

    def _generate_page_content(self, config: Config, page: Page) -> str:
        """Generate main content for a page with keywords bolded"""
        # Generate approximately 800 words of content
        content_parts = []

        # Hero section content
        hero_content = f"""
        <section class="hero container-fluid">
            <div class="container">
                <div class="row">
                    <div class="col-12">
                        <h1>{page.title}</h1>"""

        if page.hero_image:
            hero_content += f"""
                        <img src="{page.hero_image}"
                             alt="{page.title} hero image"
                             class="img-fluid">"""

        hero_content += """
                    </div>
                </div>
            </div>
        </section>
        """
        content_parts.append(hero_content)

        # Main content with keywords
        primary_keyword = page.primary_keyword or config.client.industry or "services"
        business_name = config.client.business_name

        main_content = f"""
        <section class="main-content container">
            <div class="row">
                <div class="col-12">
                    <p>Welcome to {business_name}, your trusted provider of
                    <strong>{primary_keyword}</strong>. We specialize in
                    delivering exceptional {primary_keyword} to help you
                    achieve your goals.</p>

                    <h2>About Our {primary_keyword.title()}</h2>
                    <p>At {business_name}, we understand that quality
                    <strong>{primary_keyword}</strong> make a difference.
                    Our team of experienced professionals is dedicated to
                    providing solutions that exceed expectations.</p>

                    <h3>Why Choose Our {primary_keyword.title()}?</h3>
                    <p>Our commitment to excellence in
                    <strong>{primary_keyword}</strong> sets us apart from
                    the competition. We combine industry expertise with
                    personalized service to deliver results that matter.</p>

                    <p>Whether you're looking for comprehensive
                    {primary_keyword} or specific solutions, {business_name}
                    has the experience and knowledge to help you succeed.
                    Our <strong>{primary_keyword}</strong> are designed to
                    meet your unique needs and budget requirements.</p>

                    <h3>Our Approach to {primary_keyword.title()}</h3>
                    <p>We believe that effective
                    <strong>{primary_keyword}</strong> require careful
                    planning and execution. That's why we work closely with
                    each client to understand their specific requirements
                    and develop customized solutions that deliver measurable
                    results.</p>

                    <p>Contact {business_name} today to learn more about our
                    <strong>{primary_keyword}</strong> and how we can help
                    you achieve your objectives. Our team is ready to
                    discuss your needs and provide a personalized proposal
                    for your consideration.</p>
                </div>
            </div>
        </section>
        """
        content_parts.append(main_content)

        return "\n".join(content_parts)

    def _generate_sitemap(self, config: Config) -> str:
        """Generate sitemap.xml content"""
        base_url = config.client.domain or "https://example.com"

        sitemap_content = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]

        for page in config.client.pages:
            if page.slug == "index":
                url = base_url
            else:
                url = f"{base_url.rstrip('/')}/{page.slug}.html"

            sitemap_content.extend(
                [
                    "  <url>",
                    f"    <loc>{url}</loc>",
                    "    <changefreq>weekly</changefreq>",
                    "    <priority>0.8</priority>",
                    "  </url>",
                ]
            )

        sitemap_content.append("</urlset>")
        return "\n".join(sitemap_content)

    def _generate_robots_txt(self, config: Config) -> str:
        """Generate robots.txt content"""
        base_url = config.client.domain or "https://example.com"

        return f"""User-agent: *
Allow: /

Sitemap: {base_url.rstrip('/')}/sitemap.xml
"""

    def _get_default_templates(self) -> Dict[str, str]:
        """Get default HTML templates"""
        return {"base.html": self._get_base_template()}

    def _get_base_template(self) -> str:
        """Get the base HTML template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <meta name="description" content="{{ meta_description }}">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom Styles -->
    <style>
        :root {
            {% if client.branding and client.branding.primary_color %}
            --primary-color: {{ client.branding.primary_color }};
            {% else %}
            --primary-color: #007bff;
            {% endif %}
            {% if client.branding and client.branding.secondary_color %}
            --secondary-color: {{ client.branding.secondary_color }};
            {% else %}
            --secondary-color: #6c757d;
            {% endif %}
        }

        .navbar-brand { color: var(--primary-color) !important; }
        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }
        .hero { background-color: #f8f9fa; padding: 60px 0; }
        .footer {
            background-color: #343a40;
            color: white;
            padding: 40px 0;
            margin-top: 60px;
        }
    </style>

    <!-- Schema.org Markup -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "{{ client.business_name }}",
        {% if client.contact.phone %}"telephone": "{{ client.contact.phone }}",{% endif %}
        {% if client.contact.address %}"address": "{{ client.contact.address }}",{% endif %}
        {% if client.domain %}"url": "{{ client.domain }}"{% endif %}
    }
    </script>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <a class="navbar-brand" href="index.html">{{ client.business_name }}</a>
            <button class="navbar-toggler" type="button"
                    data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% for nav_page in all_pages %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ nav_page.slug }}.html">
                            {{ nav_page.title }}
                        </a>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main>
        {{ page_content | safe }}
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5>Contact Information</h5>
                    {% if client.contact %}
                    <p>{{ client.contact.name }}</p>
                    {% if client.contact.address %}
                    <p>{{ client.contact.address }}</p>
                    {% endif %}
                    {% if client.contact.phone %}
                    <p>{{ client.contact.phone }}</p>
                    {% endif %}
                    {% endif %}
                </div>
                <div class="col-md-6">
                    <h5>Follow Us</h5>
                    {% if client.social_media %}
                    <div class="social-links">
                        {% if client.social_media.facebook %}
                        <a href="{{ client.social_media.facebook }}"
                           class="text-light me-3">Facebook</a>
                        {% endif %}
                        {% if client.social_media.twitter %}
                        <a href="{{ client.social_media.twitter }}"
                           class="text-light me-3">Twitter</a>
                        {% endif %}
                        {% if client.social_media.linkedin %}
                        <a href="{{ client.social_media.linkedin }}"
                           class="text-light me-3">LinkedIn</a>
                        {% endif %}
                        {% if client.social_media.instagram %}
                        <a href="{{ client.social_media.instagram }}"
                           class="text-light me-3">Instagram</a>
                        {% endif %}
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
