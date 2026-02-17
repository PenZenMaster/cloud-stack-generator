"""
Module/Script Name: AWG CLI Entry Point
Path: src/cli.py

Description:
Command-line interface for the AWG (Automated Website Generator) project.
Provides subcommands for website generation, deployment, validation, and provider management.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-02-16

Last Modified Date:
2026-02-16

Version: 1.00

Comments:
* v1.00 - Initial CLI implementation with click framework for Phase 0
"""

import click
import sys
from pathlib import Path
from typing import Optional

from .core.config.parser import load_config_from_file
from .core.orchestration.website_orchestrator import WebsiteOrchestrator
from .core.deployment.providers.provider_factory import ProviderFactory, get_provider_factory
from .core.deployment.providers.abstract_provider import ProviderType
from .core.utils.logger import get_logger

logger = get_logger(__name__)


@click.group()
@click.version_option(version="3.15.0", prog_name="awg")
def cli():
    """
    AWG - Automated Website Generator

    Generate SEO-optimized static websites and deploy them to cloud storage.
    """
    pass


@cli.command()
@click.option(
    '--config',
    '-c',
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help='Path to YAML configuration file'
)
@click.option(
    '--output',
    '-o',
    default='output/websites',
    type=click.Path(path_type=Path),
    help='Output directory for generated website'
)
@click.option(
    '--ai/--no-ai',
    default=True,
    help='Enable/disable AI-powered content generation'
)
def generate(config: Path, output: Path, ai: bool):
    """Generate a website from a configuration file."""
    try:
        logger.info(f"Loading config from: {config}")
        click.echo(f"Loading config from: {config}")

        # Load configuration
        client_config = load_config_from_file(str(config))
        if not client_config:
            click.echo(click.style("ERROR: Could not load config file", fg='red'))
            sys.exit(1)

        # Ensure output directory exists
        output.mkdir(parents=True, exist_ok=True)

        logger.info(f"Generating website to: {output}")
        click.echo(f"Generating website to: {output}")
        click.echo(f"AI content generation: {'enabled' if ai else 'disabled'}")

        # Initialize orchestrator
        orchestrator = WebsiteOrchestrator(use_ai=ai)

        # Generate website
        with click.progressbar(length=100, label='Generating website') as bar:
            result = orchestrator.generate(client_config, str(output))
            bar.update(100)

        if result.success:
            click.echo(click.style("\n[SUCCESS] Website generated successfully!", fg='green'))
            click.echo(f"Files created: {len(result.generated_files)}")
            click.echo(f"Output directory: {output}")

            # Show first 5 files
            if result.generated_files:
                click.echo("\nGenerated files (showing first 5):")
                for file_path in result.generated_files[:5]:
                    click.echo(f"  - {Path(file_path).name}")
                if len(result.generated_files) > 5:
                    click.echo(f"  ... and {len(result.generated_files) - 5} more files")
        else:
            click.echo(click.style("\n[FAILED] Generation failed!", fg='red'))
            if result.errors:
                click.echo(f"Errors: {result.errors}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        click.echo(click.style(f"ERROR: {str(e)}", fg='red'))
        sys.exit(1)


@cli.command()
@click.option(
    '--config',
    '-c',
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help='Path to YAML configuration file'
)
@click.option(
    '--provider',
    '-p',
    required=True,
    type=click.Choice(['aws_s3', 'google_gcs', 'wasabi', 'backblaze_b2'], case_sensitive=False),
    help='Cloud storage provider'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Simulate deployment without actually uploading files'
)
def deploy(config: Path, provider: str, dry_run: bool):
    """Deploy a website to cloud storage."""
    try:
        logger.info(f"Deploying website with config: {config}")
        click.echo(f"Loading config from: {config}")

        # Load configuration
        client_config = load_config_from_file(str(config))
        if not client_config:
            click.echo(click.style("ERROR: Could not load config file", fg='red'))
            sys.exit(1)

        if dry_run:
            click.echo(click.style("[DRY RUN MODE]", fg='yellow'))

        click.echo(f"Provider: {provider}")

        # TODO: Implement deployment logic in Phase 1
        # This is a placeholder for Phase 0
        click.echo(click.style("\nDeployment functionality will be available in Phase 1", fg='yellow'))
        click.echo("This command will:")
        click.echo(f"  1. Authenticate with {provider}")
        click.echo("  2. Create/verify bucket")
        click.echo("  3. Upload website files")
        click.echo("  4. Configure website hosting")
        click.echo("  5. Return website URL")

    except Exception as e:
        logger.error(f"Deployment failed: {e}", exc_info=True)
        click.echo(click.style(f"ERROR: {str(e)}", fg='red'))
        sys.exit(1)


@cli.command()
@click.option(
    '--config',
    '-c',
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help='Path to YAML configuration file'
)
def validate(config: Path):
    """Validate a configuration file."""
    try:
        logger.info(f"Validating config: {config}")
        click.echo(f"Validating: {config}")

        # Load and validate configuration
        client_config = load_config_from_file(str(config))

        if client_config:
            click.echo(click.style("[VALID] Configuration is valid", fg='green'))
            click.echo(f"\nBusiness: {client_config.business.business_name}")
            click.echo(f"Industry: {client_config.business.industry}")
            click.echo(f"Services: {len(client_config.services)}")
            click.echo(f"Products: {len(client_config.products)}")
            if hasattr(client_config, 'city_pages'):
                click.echo(f"City pages: {len(client_config.city_pages)}")
        else:
            click.echo(click.style("[INVALID] Configuration validation failed", fg='red'))
            sys.exit(1)

    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        click.echo(click.style(f"[ERROR] Validation error: {str(e)}", fg='red'))
        sys.exit(1)


@cli.group()
def providers():
    """Manage cloud storage providers."""
    pass


@providers.command(name='list')
def list_providers():
    """List all available cloud storage providers."""
    try:
        factory = get_provider_factory()
        available = factory.get_available_providers()

        click.echo("Available cloud storage providers:\n")

        for provider_type in available:
            status = click.style("[+]", fg='green')
            click.echo(f"  {status} {provider_type.value} - {provider_type.name}")

        if not available:
            click.echo(click.style("No providers currently available", fg='yellow'))
            click.echo("\nProviders will be added in Phase 1:")
            click.echo("  - AWS S3")
            click.echo("  - Google Cloud Storage")
            click.echo("  - Wasabi")
            click.echo("  - Backblaze B2")

    except Exception as e:
        logger.error(f"Failed to list providers: {e}", exc_info=True)
        click.echo(click.style(f"ERROR: {str(e)}", fg='red'))
        sys.exit(1)


@cli.group()
def analyze():
    """SEO analysis tools for generated websites."""
    pass


@analyze.command(name='content')
@click.argument(
    'html_file',
    type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    '--keywords',
    '-k',
    multiple=True,
    help='Target keywords for analysis (can specify multiple)'
)
@click.option(
    '--api-key',
    envvar='CLAUDE_API_KEY',
    help='Claude API key (or set CLAUDE_API_KEY env var)'
)
@click.option(
    '--model',
    type=click.Choice(['fast', 'balanced', 'thorough'], case_sensitive=False),
    default='balanced',
    help='Analysis model preset (cost vs quality)'
)
def analyze_content(html_file: Path, keywords: tuple, api_key: Optional[str], model: str):
    """
    Analyze HTML content for SEO quality.

    Example:
        awg analyze content output/clients/my-site/index.html -k "plumbing services" -k "emergency plumber"
    """
    try:
        if not api_key:
            click.echo(click.style("ERROR: Claude API key required. Set CLAUDE_API_KEY env var or use --api-key", fg='red'))
            sys.exit(1)

        from .core.seo.analyzer import SEOAnalyzer
        from .core.seo.llm.provider import ModelPreset

        # Map model preset
        preset_map = {
            'fast': ModelPreset.FAST,
            'balanced': ModelPreset.BALANCED,
            'thorough': ModelPreset.THOROUGH
        }

        click.echo(f"Analyzing: {html_file}")
        click.echo(f"Model: {model}\n")

        # Create analyzer
        analyzer = SEOAnalyzer(claude_api_key=api_key, model_preset=preset_map[model])

        # Run analysis
        result = analyzer.analyze_file(html_file, list(keywords) if keywords else None)

        # Display results
        score = result.overall_score
        click.echo(click.style(f"SEO Score: {score.overall}/100 (Grade: {score.get_grade()})", fg='green', bold=True))
        click.echo()

        # Category scores
        click.echo("Category Scores:")
        click.echo(f"  Content Quality:    {score.content_quality}/100")
        click.echo(f"  Heading Structure:  {score.heading_structure}/100")
        click.echo(f"  Meta Tags:          {score.meta_tags}/100")
        click.echo(f"  Internal Linking:   {score.internal_linking}/100")
        click.echo()

        # Recommendations
        if score.recommendations:
            high_priority = [r for r in score.recommendations if r.priority.value == 'high']
            if high_priority:
                click.echo(click.style(f"High Priority Recommendations ({len(high_priority)}):", fg='red', bold=True))
                for i, rec in enumerate(high_priority[:5], 1):
                    click.echo(f"  {i}. {rec.issue}")
                    click.echo(f"     Recommendation: {rec.recommendation}")
                    click.echo()

        # Stats
        content = result.content_analysis
        click.echo("Content Stats:")
        click.echo(f"  Word Count: {content.word_count}")
        click.echo(f"  Internal Links: {content.link_count.get('internal', 0)}")
        click.echo(f"  External Links: {content.link_count.get('external', 0)}")
        click.echo()

        click.echo(f"Model used: {result.model_used}")
        click.echo(f"Estimated cost: ${result.cost_estimate:.4f}")

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        click.echo(click.style(f"ERROR: {str(e)}", fg='red'))
        sys.exit(1)


@analyze.command(name='meta')
@click.argument(
    'html_file',
    type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    '--keywords',
    '-k',
    multiple=True,
    help='Target keywords for optimization'
)
@click.option(
    '--api-key',
    envvar='CLAUDE_API_KEY',
    help='Claude API key (or set CLAUDE_API_KEY env var)'
)
def analyze_meta(html_file: Path, keywords: tuple, api_key: Optional[str]):
    """
    Analyze meta tags for SEO optimization.

    Example:
        awg analyze meta output/clients/my-site/index.html -k "plumbing services"
    """
    try:
        if not api_key:
            click.echo(click.style("ERROR: Claude API key required", fg='red'))
            sys.exit(1)

        from .core.seo.analyzer import SEOAnalyzer
        from .core.seo.llm.provider import ModelPreset

        click.echo(f"Analyzing meta tags: {html_file}\n")

        # Create analyzer
        analyzer = SEOAnalyzer(claude_api_key=api_key, model_preset=ModelPreset.BALANCED)

        # Run analysis
        result = analyzer.analyze_file(html_file, list(keywords) if keywords else None)
        meta = result.meta_analysis

        # Display results
        click.echo(click.style(f"Meta Tags Score: {meta.overall_score}/100", fg='green', bold=True))
        click.echo()

        click.echo(f"Title: {meta.title}")
        click.echo(f"  Length: {meta.title_length} chars (optimal: 50-60)")
        click.echo(f"  Score: {meta.title_score}/100")
        click.echo()

        click.echo(f"Description: {meta.description[:80]}...")
        click.echo(f"  Length: {meta.description_length} chars (optimal: 150-160)")
        click.echo(f"  Score: {meta.description_score}/100")
        click.echo()

        # Recommendations
        if meta.recommendations:
            click.echo(click.style("Recommendations:", fg='yellow', bold=True))
            for i, rec in enumerate(meta.recommendations, 1):
                click.echo(f"  {i}. [{rec.priority.value.upper()}] {rec.issue}")
                click.echo(f"     {rec.recommendation}")
                click.echo()

    except Exception as e:
        logger.error(f"Meta analysis failed: {e}", exc_info=True)
        click.echo(click.style(f"ERROR: {str(e)}", fg='red'))
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
