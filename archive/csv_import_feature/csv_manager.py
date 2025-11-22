"""
CSV data management and validation

This module handles CSV file upload, validation, and parsing for products and services.
Provides robust error handling and data validation.

Version: 1.0.1
Author: Cloud Stack Generator Team
"""

import pandas as pd
import os
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from ..config.models import ProductConfig, ServiceConfig


@dataclass
class ValidationError:
    """Represents a validation error with context"""

    row: int
    column: str
    message: str
    severity: str = "error"  # "error", "warning", "info"


@dataclass
class ValidationResult:
    """Result of CSV validation process"""

    is_valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    total_rows: int = 0
    valid_rows: int = 0

    def add_error(self, row: int, column: str, message: str):
        """Add a validation error"""
        self.errors.append(ValidationError(row, column, message, "error"))
        self.is_valid = False

    def add_warning(self, row: int, column: str, message: str):
        """Add a validation warning"""
        self.warnings.append(ValidationError(row, column, message, "warning"))

    def get_error_summary(self) -> str:
        """Get a summary of all errors and warnings"""
        summary = []

        if self.errors:
            summary.append(f"ERRORS ({len(self.errors)}):")
            for error in self.errors[:10]:  # Show first 10 errors
                summary.append(f"  Row {error.row}, {error.column}: {error.message}")
            if len(self.errors) > 10:
                summary.append(f"  ... and {len(self.errors) - 10} more errors")

        if self.warnings:
            summary.append(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:5]:  # Show first 5 warnings
                summary.append(
                    f"  Row {warning.row}, {warning.column}: {warning.message}"
                )
            if len(self.warnings) > 5:
                summary.append(f"  ... and {len(self.warnings) - 5} more warnings")

        return "\n".join(summary)


class CSVManager:
    """Handles CSV upload, validation, and parsing for products and services"""

    # Required columns for different CSV types
    PRODUCT_REQUIRED_COLUMNS = ["SKU", "Name"]
    PRODUCT_OPTIONAL_COLUMNS = ["Image URL", "Description", "Category", "Price"]

    SERVICE_REQUIRED_COLUMNS = ["Name"]
    SERVICE_OPTIONAL_COLUMNS = ["Description", "Category"]

    def __init__(self):
        self.last_validation_result: Optional[ValidationResult] = None
        self.supported_encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

    def detect_csv_encoding(self, file_path: str) -> str:
        """Detect the encoding of a CSV file"""
        # First check if file exists
        if not os.path.exists(file_path):
            return "utf-8"  # Return default if file doesn't exist

        try:
            # Try chardet if available
            try:
                import chardet

                with open(file_path, "rb") as f:
                    raw_data = f.read()
                    result = chardet.detect(raw_data)
                    detected_encoding = result.get("encoding") or "utf-8"

                    # Verify the detected encoding works
                    try:
                        pd.read_csv(file_path, encoding=detected_encoding, nrows=1)
                        return detected_encoding
                    except UnicodeDecodeError:
                        pass
            except ImportError:
                # chardet not available, fall back to manual detection
                pass
        except Exception:
            pass

        # Fall back to trying common encodings
        for encoding in self.supported_encodings:
            try:
                pd.read_csv(file_path, encoding=encoding, nrows=1)
                return encoding
            except (UnicodeDecodeError, FileNotFoundError):
                continue

        return "utf-8"  # Last resort

    def validate_csv_file(
        self, file_path: str, csv_type: str = "products"
    ) -> ValidationResult:
        """
        Validate CSV file structure and basic data quality

        Args:
            file_path: Path to the CSV file
            csv_type: Type of CSV ("products" or "services")

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult()

        # Check if file exists
        if not os.path.exists(file_path):
            result.add_error(0, "File", "CSV file does not exist")
            return result

        # Check file size (warn if > 10MB)
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            result.add_warning(
                0, "File", f"Large file size: {file_size / 1024 / 1024:.1f}MB"
            )

        try:
            # Detect encoding
            encoding = self.detect_csv_encoding(file_path)

            # Read CSV file
            df = pd.read_csv(file_path, encoding=encoding)
            result.total_rows = len(df)

            # Check if file is empty
            if df.empty:
                result.add_error(0, "File", "CSV file is empty")
                return result

            # Get required columns based on CSV type
            required_cols = (
                self.PRODUCT_REQUIRED_COLUMNS
                if csv_type == "products"
                else self.SERVICE_REQUIRED_COLUMNS
            )

            # Check for required columns
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                result.add_error(
                    0,
                    "Structure",
                    f"Missing required columns: {', '.join(missing_cols)}",
                )
                return result

            # Validate data quality
            self._validate_data_quality(df, result, csv_type)

        except pd.errors.EmptyDataError:
            result.add_error(0, "File", "CSV file is empty or corrupted")
        except pd.errors.ParserError as e:
            result.add_error(0, "Structure", f"CSV parsing error: {str(e)}")
        except Exception as e:
            result.add_error(0, "File", f"Error reading CSV file: {str(e)}")

        self.last_validation_result = result
        return result

    def _validate_data_quality(
        self, df: pd.DataFrame, result: ValidationResult, csv_type: str
    ):
        """Validate the quality of data in the CSV"""
        valid_rows = 0

        for index in range(len(df)):
            row = df.iloc[index]
            row_valid = True
            row_number = index + 2  # +2 because CSV rows start at 1 and we skip header

            if csv_type == "products":
                # Validate SKU
                sku = str(row.get("SKU", "")).strip()
                if not sku or sku.lower() == "nan":
                    result.add_error(row_number, "SKU", "SKU is required")
                    row_valid = False

                # Validate Name
                name = str(row.get("Name", "")).strip()
                if not name or name.lower() == "nan":
                    result.add_error(row_number, "Name", "Product name is required")
                    row_valid = False

                # Check for duplicate SKUs within the file
                if sku and not sku.lower() == "nan":
                    duplicate_count = (df["SKU"].astype(str).str.strip() == sku).sum()
                    if duplicate_count > 1:
                        result.add_warning(row_number, "SKU", f"Duplicate SKU: {sku}")

                # Validate Image URL if provided
                image_url = str(row.get("Image URL", "")).strip()
                if image_url and image_url.lower() != "nan":
                    if not self._is_valid_url(image_url):
                        result.add_warning(
                            row_number, "Image URL", "Invalid URL format"
                        )

            elif csv_type == "services":
                # Validate Service Name
                name = str(row.get("Name", "")).strip()
                if not name or name.lower() == "nan":
                    result.add_error(row_number, "Name", "Service name is required")
                    row_valid = False

            if row_valid:
                valid_rows += 1

        result.valid_rows = valid_rows

    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation"""
        import re

        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return url_pattern.match(url) is not None

    def parse_products_csv(
        self, file_path: str
    ) -> Tuple[List[ProductConfig], ValidationResult]:
        """
        Parse products from CSV file into ProductConfig objects

        Args:
            file_path: Path to the products CSV file

        Returns:
            Tuple of (products_list, validation_result)
        """
        result = ValidationResult()
        products = []

        try:
            # Detect encoding and read CSV
            encoding = self.detect_csv_encoding(file_path)
            df = pd.read_csv(file_path, encoding=encoding)
            result.total_rows = len(df)

            for index in range(len(df)):
                row = df.iloc[index]
                row_number = (
                    index + 2
                )  # +2 because CSV rows start at 1 and we skip header

                try:
                    # Extract and clean data
                    sku = str(row.get("SKU", "")).strip()
                    name = str(row.get("Name", "")).strip()
                    image_url = str(row.get("Image URL", "")).strip()
                    description = str(row.get("Description", "")).strip()
                    category = str(row.get("Category", "")).strip()
                    price = str(row.get("Price", "")).strip()

                    # Clean up 'nan' values
                    if image_url.lower() == "nan":
                        image_url = ""
                    if description.lower() == "nan":
                        description = ""
                    if category.lower() == "nan":
                        category = ""
                    if price.lower() == "nan":
                        price = ""

                    # Skip rows with missing required data
                    if (
                        not sku
                        or not name
                        or sku.lower() == "nan"
                        or name.lower() == "nan"
                    ):
                        result.add_error(
                            row_number, "Data", "Missing required SKU or Name"
                        )
                        continue

                    # Create ProductConfig object
                    product = ProductConfig(
                        sku=sku,
                        name=name,
                        image_url=image_url,
                        description=description,
                        category=category,
                        price=price,
                    )

                    products.append(product)

                except ValueError as e:
                    result.add_error(row_number, "Data", str(e))
                except Exception as e:
                    result.add_error(row_number, "Data", f"Unexpected error: {str(e)}")

            result.valid_rows = len(products)

        except Exception as e:
            result.add_error(0, "File", f"Error parsing CSV: {str(e)}")

        return products, result

    def parse_services_csv(
        self, file_path: str
    ) -> Tuple[List[ServiceConfig], ValidationResult]:
        """
        Parse services from CSV file into ServiceConfig objects

        Args:
            file_path: Path to the services CSV file

        Returns:
            Tuple of (services_list, validation_result)
        """
        result = ValidationResult()
        services = []

        try:
            # Detect encoding and read CSV
            encoding = self.detect_csv_encoding(file_path)
            df = pd.read_csv(file_path, encoding=encoding)
            result.total_rows = len(df)

            for index in range(len(df)):
                row = df.iloc[index]
                row_number = (
                    index + 2
                )  # +2 because CSV rows start at 1 and we skip header

                try:
                    # Extract and clean data
                    name = str(row.get("Name", "")).strip()
                    description = str(row.get("Description", "")).strip()
                    category = str(row.get("Category", "")).strip()

                    # Clean up 'nan' values
                    if description.lower() == "nan":
                        description = ""
                    if category.lower() == "nan":
                        category = ""

                    # Skip rows with missing required data
                    if not name or name.lower() == "nan":
                        result.add_error(row_number, "Name", "Service name is required")
                        continue

                    # Create ServiceConfig object
                    service = ServiceConfig(
                        name=name, description=description, category=category
                    )

                    services.append(service)

                except ValueError as e:
                    result.add_error(row_number, "Data", str(e))
                except Exception as e:
                    result.add_error(row_number, "Data", f"Unexpected error: {str(e)}")

            result.valid_rows = len(services)

        except Exception as e:
            result.add_error(0, "File", f"Error parsing CSV: {str(e)}")

        return services, result

    def export_products_to_csv(
        self, products: List[ProductConfig], file_path: str
    ) -> bool:
        """
        Export products to CSV file

        Args:
            products: List of ProductConfig objects
            file_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            data = []
            for product in products:
                data.append(
                    {
                        "SKU": product.sku,
                        "Name": product.name,
                        "Image URL": product.image_url,
                        "Description": product.description,
                        "Category": product.category,
                        "Price": product.price,
                    }
                )

            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, encoding="utf-8")
            return True

        except Exception as e:
            print(f"Error exporting products to CSV: {e}")
            return False

    def export_services_to_csv(
        self, services: List[ServiceConfig], file_path: str
    ) -> bool:
        """
        Export services to CSV file

        Args:
            services: List of ServiceConfig objects
            file_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            data = []
            for service in services:
                data.append(
                    {
                        "Name": service.name,
                        "Description": service.description,
                        "Category": service.category,
                    }
                )

            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, encoding="utf-8")
            return True

        except Exception as e:
            print(f"Error exporting services to CSV: {e}")
            return False

    def get_csv_preview(
        self, file_path: str, max_rows: int = 10
    ) -> Tuple[pd.DataFrame, str]:
        """
        Get a preview of the CSV file data

        Args:
            file_path: Path to CSV file
            max_rows: Maximum number of rows to preview

        Returns:
            Tuple of (preview_dataframe, encoding_used)
        """
        try:
            encoding = self.detect_csv_encoding(file_path)
            df = pd.read_csv(file_path, encoding=encoding, nrows=max_rows)
            return df, encoding
        except Exception:
            # Return empty dataframe on error
            return pd.DataFrame(), "utf-8"
