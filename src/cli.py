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
@click.version_option(version="3.13.0", prog_name="awg")
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


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
