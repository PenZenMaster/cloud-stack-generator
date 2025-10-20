"""
String Utilities
Path: E:/projects/cloud-stack-generator/src/core/utils/string_utils.py

Description:
String manipulation utilities for URL slugs, formatting, and text processing.
Extracted from website_generator.py to improve separation of concerns and reusability.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-17

Last Modified Date:
2025-10-17

Comments:
* v1.00 - Initial extraction from website_generator.py
"""

import re


def create_slug(city_name: str) -> str:
    """
    Create URL-friendly slug from city name.

    This version removes all special characters and converts spaces to hyphens.

    Args:
        city_name: City name string (may include state, special chars)

    Returns:
        URL-friendly slug with only lowercase letters, numbers, and hyphens

    Examples:
        >>> create_slug("Chicago, IL")
        'chicago-il'
        >>> create_slug("Oak Brook")
        'oak-brook'
        >>> create_slug("St. Charles")
        'st-charles'
    """
    # Remove all non-alphanumeric characters except spaces
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', city_name.lower())
    # Convert multiple spaces to single hyphen
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug


def generate_city_slug(city_name: str) -> str:
    """
    Generate URL slug from city name (matches location_page_generator pattern).

    This version preserves some punctuation during transformation for compatibility
    with the navigation builder pattern.

    Args:
        city_name: City name string (may include state)

    Returns:
        URL-friendly slug for the city

    Examples:
        >>> generate_city_slug("Chicago, IL")
        'chicago-il'
        >>> generate_city_slug("Oak Brook")
        'oak-brook'
        >>> generate_city_slug("Aurora IL")
        'aurora-il'
    """
    slug = city_name.lower()
    slug = slug.replace(' ', '-')      # Spaces to hyphens
    slug = slug.replace(',', '')       # Remove commas
    slug = slug.replace(' illinois', '')  # Remove state suffix
    slug = slug.replace(' il', '')     # Remove abbreviated state
    slug = slug.strip('-')            # Clean up trailing hyphens
    return slug


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number for tel: links (remove all non-digits).

    Args:
        phone: Phone number string in any format

    Returns:
        Phone number with only digits (suitable for tel: link)

    Examples:
        >>> normalize_phone("(555) 123-4567")
        '5551234567'
        >>> normalize_phone("555-123-4567")
        '5551234567'
        >>> normalize_phone("5551234567")
        '5551234567'
    """
    if not phone:
        return ""
    # Remove all non-digit characters for tel: link
    return "".join(filter(str.isdigit, phone))


def format_phone_display(phone: str) -> str:
    """
    Get proper display format for phone number.

    Args:
        phone: Phone number string in any format

    Returns:
        Formatted phone number for display (xxx) xxx-xxxx

    Examples:
        >>> format_phone_display("5551234567")
        '(555) 123-4567'
        >>> format_phone_display("(555) 123-4567")
        '(555) 123-4567'
        >>> format_phone_display("15551234567")
        '(555) 123-4567'
    """
    if not phone:
        return ""

    # If phone looks like it's already formatted nicely, keep it
    if "(" in phone and ")" in phone and "-" in phone:
        return phone

    # Extract digits and format for display
    digits = "".join(filter(str.isdigit, phone))

    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits.startswith("1"):
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

    return phone  # Return original if can't parse
