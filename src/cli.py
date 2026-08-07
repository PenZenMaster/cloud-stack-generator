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
2026-03-21

Version: 1.03

Comments:
* v1.03 - Bumped app version to 4.1.0 (BACK-007 + GBP v1.07 milestone)
* v1.02 - Added awg onboard command; bumped app version to 4.0.0
* v1.01 - Implemented aws_s3 deploy command with sync_to_s3() and --source option
* v1.00 - Initial CLI implementation with click framework for Phase 0
"""

import boto3
import click
import sys
from pathlib import Path
from typing import Optional

from .core.config.parser import load_config_from_file
from .core.deployment.s3_deployer import sync_to_s3
from .core.orchestration.website_orchestrator import WebsiteOrchestrator
from .core.deployment.providers.provider_factory import get_provider_factory
from .core.utils.logger import get_logger

logger = get_logger(__name__)


@click.group()
@click.version_option(version="4.1.0", prog_name="awg")
def cli():
    """
    AWG - Automated Website Generator

    Generate SEO-optimized static websites and deploy them to cloud storage.
    """
    pass


@cli.command()
@click.option(
    "--config",
    "-c",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to YAML configuration file",
)
@click.option(
    "--output",
    "-o",
    default="output/websites",
    type=click.Path(path_type=Path),
    help="Output directory for generated website",
)
@click.option(
    "--ai/--no-ai", default=True, help="Enable/disable AI-powered content generation"
)
@click.option(
    "--allow-template-fallback",
    is_flag=True,
    default=False,
    help=(
        "Allow generating more than the template-fallback page limit of city pages "
        "that lack real content (about_city/seo_content_body) and would otherwise "
        "render scaled boilerplate. Off by default; requires deliberate opt-in."
    ),
)
def generate(config: Path, output: Path, ai: bool, allow_template_fallback: bool):
    """Generate a website from a configuration file."""
    try:
        logger.info(f"Loading config from: {config}")
        click.echo(f"Loading config from: {config}")

        # Load configuration
        client_config = load_config_from_file(str(config))
        if not client_config:
            click.echo(click.style("ERROR: Could not load config file", fg="red"))
            sys.exit(1)

        # Ensure output directory exists
        output.mkdir(parents=True, exist_ok=True)

        logger.info(f"Generating website to: {output}")
        click.echo(f"Generating website to: {output}")
        click.echo(f"AI content generation: {'enabled' if ai else 'disabled'}")

        # Initialize orchestrator
        orchestrator = WebsiteOrchestrator(
            use_ai=ai, allow_template_fallback=allow_template_fallback
        )

        # Generate website
        with click.progressbar(length=100, label="Generating website") as bar:
            result = orchestrator.generate(client_config, str(output))
            bar.update(100)

        if result.success:
            click.echo(
                click.style("\n[SUCCESS] Website generated successfully!", fg="green")
            )
            click.echo(f"Files created: {len(result.generated_files)}")
            click.echo(f"Output directory: {output}")

            # Show first 5 files
            if result.generated_files:
                click.echo("\nGenerated files (showing first 5):")
                for file_path in result.generated_files[:5]:
                    click.echo(f"  - {Path(file_path).name}")
                if len(result.generated_files) > 5:
                    click.echo(
                        f"  ... and {len(result.generated_files) - 5} more files"
                    )
        else:
            click.echo(click.style("\n[FAILED] Generation failed!", fg="red"))
            if result.errors:
                click.echo(f"Errors: {result.errors}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        click.echo(click.style(f"ERROR: {str(e)}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option(
    "--config",
    "-c",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to YAML configuration file",
)
@click.option(
    "--source",
    "-s",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Local directory containing the built website to deploy",
)
@click.option(
    "--provider",
    "-p",
    required=True,
    type=click.Choice(
        ["aws_s3", "google_gcs", "wasabi", "backblaze_b2"], case_sensitive=False
    ),
    help="Cloud storage provider",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Simulate deployment without actually uploading files",
)
def deploy(config: Path, source: Path, provider: str, dry_run: bool):
    """Deploy a built website directory to cloud storage."""
    try:
        logger.info(f"Deploying website with config: {config}")
        click.echo(f"Loading config from: {config}")

        # Load configuration
        client_config = load_config_from_file(str(config))
        if not client_config:
            click.echo(click.style("ERROR: Could not load config file", fg="red"))
            sys.exit(1)

        if dry_run:
            click.echo(
                click.style("[DRY RUN MODE] No files will be uploaded", fg="yellow")
            )

        click.echo(f"Provider: {provider}")
        click.echo(f"Source:   {source}")

        # Only aws_s3 is implemented; others remain stubs
        if provider != "aws_s3":
            click.echo(
                click.style(
                    f"\nProvider '{provider}' is not yet implemented. Only 'aws_s3' is supported.",
                    fg="yellow",
                )
            )
            sys.exit(0)

        # Validate cloud configuration
        cloud = client_config.cloud
        if not cloud.is_configured():
            click.echo(
                click.style(
                    "ERROR: Cloud deployment is not configured. "
                    "Set aws_profile and bucket_name in the YAML cloud section.",
                    fg="red",
                )
            )
            sys.exit(1)

        click.echo(f"Bucket:   {cloud.bucket_name}")
        click.echo(f"Region:   {cloud.aws_region}")
        click.echo(f"Profile:  {cloud.aws_profile}")
        if cloud.distribution_id:
            click.echo(f"CloudFront distribution: {cloud.distribution_id}")

        # Create authenticated boto3 session
        session = boto3.Session(
            profile_name=cloud.aws_profile,
            region_name=cloud.aws_region,
        )

        # Progress reporter
        def _progress(msg: str) -> None:
            click.echo(f"  {msg}")

        click.echo("\nStarting sync...")
        result = sync_to_s3(
            source_dir=source,
            bucket_name=cloud.bucket_name,
            session=session,
            cloud_config=cloud,
            dry_run=dry_run,
            progress_callback=_progress,
        )

        if dry_run:
            plan = result.get("plan", {})
            click.echo(click.style("\n[DRY RUN] Deployment plan:", fg="yellow"))
            click.echo(f"  Files to upload: {plan.get('total_upload', 0)}")
            click.echo(f"  Files to delete: {plan.get('total_delete', 0)}")
            if plan.get("files_to_upload"):
                click.echo("\n  Upload list (first 10):")
                for key in plan["files_to_upload"][:10]:
                    click.echo(f"    + {key}")
                if plan["total_upload"] > 10:
                    click.echo(f"    ... and {plan['total_upload'] - 10} more")
            if plan.get("files_to_delete"):
                click.echo("\n  Delete list:")
                for key in plan["files_to_delete"]:
                    click.echo(f"    - {key}")
            click.echo(click.style("\n[DRY RUN] No changes were made.", fg="yellow"))
            return

        # Report results
        if result["success"]:
            click.echo(click.style("\n[SUCCESS] Deployment complete!", fg="green"))
        else:
            click.echo(
                click.style("\n[PARTIAL] Deployment finished with errors.", fg="yellow")
            )

        click.echo(f"  Files uploaded: {result['files_uploaded']}")
        click.echo(f"  Files deleted:  {result['files_deleted']}")

        if result.get("invalidation_id"):
            click.echo(f"  CloudFront invalidation ID: {result['invalidation_id']}")

        if result["errors"]:
            click.echo(click.style(f"\n  Errors ({len(result['errors'])}):", fg="red"))
            for err in result["errors"]:
                click.echo(f"    - {err}")

        deployment_url = cloud.get_website_url()
        if deployment_url:
            click.echo(f"\n  URL: {deployment_url}")

        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Deployment failed: {e}", exc_info=True)
        click.echo(click.style(f"ERROR: {str(e)}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option(
    "--config",
    "-c",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to YAML configuration file",
)
def validate(config: Path):
    """Validate a configuration file."""
    try:
        logger.info(f"Validating config: {config}")
        click.echo(f"Validating: {config}")

        # Load and validate configuration
        client_config = load_config_from_file(str(config))

        if client_config:
            click.echo(click.style("[VALID] Configuration is valid", fg="green"))
            click.echo(f"\nBusiness: {client_config.business.business_name}")
            click.echo(f"Industry: {client_config.business.industry}")
            click.echo(f"Services: {len(client_config.services)}")
            click.echo(f"Products: {len(client_config.products)}")
            if hasattr(client_config, "city_pages"):
                click.echo(f"City pages: {len(client_config.city_pages)}")
        else:
            click.echo(
                click.style("[INVALID] Configuration validation failed", fg="red")
            )
            sys.exit(1)

    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        click.echo(click.style(f"[ERROR] Validation error: {str(e)}", fg="red"))
        sys.exit(1)


@cli.group()
def providers():
    """Manage cloud storage providers."""
    pass


@providers.command(name="list")
def list_providers():
    """List all available cloud storage providers."""
    try:
        factory = get_provider_factory()
        available = factory.get_available_providers()

        click.echo("Available cloud storage providers:\n")

        for provider_type in available:
            status = click.style("[+]", fg="green")
            click.echo(f"  {status} {provider_type.value} - {provider_type.name}")

        if not available:
            click.echo(click.style("No providers currently available", fg="yellow"))
            click.echo("\nProviders will be added in Phase 1:")
            click.echo("  - AWS S3")
            click.echo("  - Google Cloud Storage")
            click.echo("  - Wasabi")
            click.echo("  - Backblaze B2")

    except Exception as e:
        logger.error(f"Failed to list providers: {e}", exc_info=True)
        click.echo(click.style(f"ERROR: {str(e)}", fg="red"))
        sys.exit(1)


@cli.group()
def analyze():
    """SEO analysis tools for generated websites."""
    pass


@analyze.command(name="content")
@click.argument(
    "html_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--keywords",
    "-k",
    multiple=True,
    help="Target keywords for analysis (can specify multiple)",
)
@click.option(
    "--api-key",
    envvar="CLAUDE_API_KEY",
    help="Claude API key (or set CLAUDE_API_KEY env var)",
)
@click.option(
    "--model",
    type=click.Choice(["fast", "balanced", "thorough"], case_sensitive=False),
    default="balanced",
    help="Analysis model preset (cost vs quality)",
)
def analyze_content(
    html_file: Path, keywords: tuple, api_key: Optional[str], model: str
):
    """
    Analyze HTML content for SEO quality.

    Example:
        awg analyze content output/clients/my-site/index.html -k "plumbing services" -k "emergency plumber"
    """
    try:
        if not api_key:
            click.echo(
                click.style(
                    "ERROR: Claude API key required. Set CLAUDE_API_KEY env var or use --api-key",
                    fg="red",
                )
            )
            sys.exit(1)

        from .core.seo.analyzer import SEOAnalyzer
        from .core.seo.llm.provider import ModelPreset

        # Map model preset
        preset_map = {
            "fast": ModelPreset.FAST,
            "balanced": ModelPreset.BALANCED,
            "thorough": ModelPreset.THOROUGH,
        }

        click.echo(f"Analyzing: {html_file}")
        click.echo(f"Model: {model}\n")

        # Create analyzer
        analyzer = SEOAnalyzer(claude_api_key=api_key, model_preset=preset_map[model])

        # Run analysis
        result = analyzer.analyze_file(html_file, list(keywords) if keywords else None)

        # Display results
        score = result.overall_score
        click.echo(
            click.style(
                f"SEO Score: {score.overall}/100 (Grade: {score.get_grade()})",
                fg="green",
                bold=True,
            )
        )
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
            high_priority = [
                r for r in score.recommendations if r.priority.value == "high"
            ]
            if high_priority:
                click.echo(
                    click.style(
                        f"High Priority Recommendations ({len(high_priority)}):",
                        fg="red",
                        bold=True,
                    )
                )
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
        click.echo(click.style(f"ERROR: {str(e)}", fg="red"))
        sys.exit(1)


@analyze.command(name="meta")
@click.argument(
    "html_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--keywords", "-k", multiple=True, help="Target keywords for optimization"
)
@click.option(
    "--api-key",
    envvar="CLAUDE_API_KEY",
    help="Claude API key (or set CLAUDE_API_KEY env var)",
)
def analyze_meta(html_file: Path, keywords: tuple, api_key: Optional[str]):
    """
    Analyze meta tags for SEO optimization.

    Example:
        awg analyze meta output/clients/my-site/index.html -k "plumbing services"
    """
    try:
        if not api_key:
            click.echo(click.style("ERROR: Claude API key required", fg="red"))
            sys.exit(1)

        from .core.seo.analyzer import SEOAnalyzer
        from .core.seo.llm.provider import ModelPreset

        click.echo(f"Analyzing meta tags: {html_file}\n")

        # Create analyzer
        analyzer = SEOAnalyzer(
            claude_api_key=api_key, model_preset=ModelPreset.BALANCED
        )

        # Run analysis
        result = analyzer.analyze_file(html_file, list(keywords) if keywords else None)
        meta = result.meta_analysis

        # Display results
        click.echo(
            click.style(
                f"Meta Tags Score: {meta.overall_score}/100", fg="green", bold=True
            )
        )
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
            click.echo(click.style("Recommendations:", fg="yellow", bold=True))
            for i, rec in enumerate(meta.recommendations, 1):
                click.echo(f"  {i}. [{rec.priority.value.upper()}] {rec.issue}")
                click.echo(f"     {rec.recommendation}")
                click.echo()

    except Exception as e:
        logger.error(f"Meta analysis failed: {e}", exc_info=True)
        click.echo(click.style(f"ERROR: {str(e)}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option(
    "--url", "-u", required=True, help="Client website URL (e.g. https://example.com)"
)
@click.option(
    "--gbp", "-g", default="", help="Google Business Profile share link (optional)"
)
@click.option(
    "--industry",
    "-i",
    required=True,
    help='Business industry (e.g. "plumbing", "portable restroom rental")',
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(),
    help="Output YAML file path (auto-generated if omitted)",
)
@click.option(
    "--api-key",
    envvar="CLAUDE_API_KEY",
    help="Claude API key (or set CLAUDE_API_KEY env var)",
)
@click.option(
    "--google-api-key",
    envvar="GOOGLE_MAPS_API_KEY",
    help="Google Places API key (or set GOOGLE_MAPS_API_KEY env var)",
)
@click.option(
    "--model",
    type=click.Choice(["fast", "balanced", "thorough"], case_sensitive=False),
    default="balanced",
    help="LLM model preset (cost vs quality)",
)
def onboard(
    url: str,
    gbp: str,
    industry: str,
    output: Optional[str],
    api_key: Optional[str],
    google_api_key: Optional[str],
    model: str,
):
    """
    Auto-populate a client config from a website and Google Business Profile.

    Scrapes the client website, extracts business data via Claude, fetches
    Google Business Profile details, and writes a pre-populated YAML config
    that can be used immediately with 'awg generate'.

    Example:
        awg onboard -u https://acmeplumbing.com -i "plumbing" -g "https://maps.app.goo.gl/abc123"
    """
    try:
        if not api_key:
            click.echo(
                click.style(
                    "ERROR: Claude API key required. Set CLAUDE_API_KEY env var or use --api-key",
                    fg="red",
                )
            )
            sys.exit(1)

        from .core.onboarding import Onboarder

        click.echo(f"Onboarding: {url}")
        click.echo(f"Industry: {industry}")
        click.echo(f"Model: {model}")
        if gbp:
            click.echo(f"GBP: {gbp}")
        click.echo()

        def progress(msg: str) -> None:
            click.echo(msg)

        onboarder = Onboarder(
            url=url,
            gbp_link=gbp,
            industry=industry,
            claude_api_key=api_key,
            google_api_key=google_api_key or "",
            model=model,
        )

        result = onboarder.run(
            output_path=output or None,
            progress_callback=progress,
        )
        click.echo()

        if result.success:
            click.echo(
                click.style("[SUCCESS] Client config saved to:", fg="green", bold=True)
            )
            click.echo(f"  {result.output_path}")
            click.echo()
            click.echo(f"  Business:  {result.business_name}")
            click.echo(f"  Services:  {result.services_found}")
            click.echo(f"  Products:  {result.products_found}")
        else:
            click.echo(click.style("[FAILED] Config generation failed.", fg="red"))

        if result.warnings:
            click.echo()
            click.echo(click.style("Warnings:", fg="yellow"))
            for w in result.warnings:
                click.echo(f"  - {w}")

        if result.errors:
            click.echo()
            click.echo(click.style("Errors:", fg="red"))
            for e in result.errors:
                click.echo(f"  - {e}")

        if not result.success:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Onboarding failed: {e}", exc_info=True)
        click.echo(click.style(f"ERROR: {str(e)}", fg="red"))
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
