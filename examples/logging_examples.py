"""
Logging System Usage Examples
Demonstrates how to use the centralized logging system

Run this file to see logging in action:
    python examples/logging_examples.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.utils.logger import (
    get_logger,
    log_execution_time,
    log_exception,
    LogContext,
    info, warning, error, debug
)


# Example 1: Basic logging
def example_basic_logging():
    """Basic logging usage"""
    print("\n=== Example 1: Basic Logging ===\n")

    logger = get_logger(__name__)

    logger.debug("This is a debug message (verbose)")
    logger.info("Application started successfully")
    logger.warning("Configuration file not found, using defaults")
    logger.error("Failed to connect to database")
    logger.critical("System out of memory!")


# Example 2: Logging with context
def example_context_logging():
    """Logging with additional context"""
    print("\n=== Example 2: Context Logging ===\n")

    logger = get_logger(__name__)

    logger.info(
        "Deploying website",
        extra={"extra_fields": {
            "client": "salvo-metal-works",
            "bucket": "salvo-website",
            "files_count": 45
        }}
    )


# Example 3: Performance timing decorator
@log_execution_time
def example_slow_operation():
    """Function with execution time logging"""
    print("\n=== Example 3: Performance Timing ===\n")
    import time
    time.sleep(0.5)  # Simulate work
    return "Operation complete"


# Example 4: Exception logging decorator
def example_exception_logging():
    """Exception logging with context"""
    print("\n=== Example 4: Exception Logging ===\n")

    logger = get_logger(__name__)

    @log_exception(logger, "processing user input")
    def process_data(value):
        if value < 0:
            raise ValueError("Value must be positive")
        return value * 2

    try:
        result = process_data(-5)
    except ValueError:
        print("Exception was logged (check logs)")


# Example 5: Context manager for operations
def example_context_manager():
    """Using LogContext for operation tracking"""
    print("\n=== Example 5: Operation Context ===\n")

    logger = get_logger(__name__)

    with LogContext(logger, "uploading files to S3", bucket="my-bucket", region="us-east-1"):
        logger.info("Uploading file 1/10")
        logger.info("Uploading file 5/10")
        logger.info("Uploading file 10/10")


# Example 6: Simple convenience functions
def example_convenience_functions():
    """Using simple logging functions"""
    print("\n=== Example 6: Convenience Functions ===\n")

    info("Using simple info() function", operation="test")
    warning("Using simple warning() function")
    error("Using simple error() function")
    debug("Using simple debug() function")


# Example 7: Real-world deployment scenario
def example_deployment_scenario():
    """Real-world deployment logging example"""
    print("\n=== Example 7: Deployment Scenario ===\n")

    logger = get_logger("deployment")

    with LogContext(logger, "deploying website", client="test-client", mode="cloudfront"):
        try:
            logger.info("Validating configuration")
            logger.info("Generating HTML pages", extra={"extra_fields": {"page_count": 25}})
            logger.info("Uploading to S3", extra={"extra_fields": {"bucket": "test-bucket"}})
            logger.info("Configuring CloudFront distribution")
            logger.info("Deployment successful!", extra={"extra_fields": {"url": "https://d1234.cloudfront.net"}})

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("Cloud Stack Generator - Logging System Examples")
    print("=" * 60)

    example_basic_logging()
    example_context_logging()
    example_slow_operation()
    example_exception_logging()
    example_context_manager()
    example_convenience_functions()
    example_deployment_scenario()

    print("\n" + "=" * 60)
    print("Check logs at: ~/.cloud-stack-generator/logs/")
    print("  - cloud_stack_generator.log (all logs, JSON format)")
    print("  - errors.log (errors only, JSON format)")
    print("=" * 60)
