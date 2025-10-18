"""
HTML Utilities
Path: E:/projects/cloud-stack-generator/src/core/utils/html_utils.py

Description:
HTML manipulation and formatting utilities for content processing and iframe handling.
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


def format_content_body(content: str) -> str:
    """
    Format content body text with basic HTML formatting.

    Converts plain text with paragraph breaks into HTML paragraphs.

    Args:
        content: Plain text content with double newlines as paragraph separators

    Returns:
        HTML formatted content with <p> tags

    Examples:
        >>> format_content_body("First paragraph.\\n\\nSecond paragraph.")
        '<p>First paragraph.</p>\\n<p>Second paragraph.</p>'
        >>> format_content_body("")
        ''
    """
    if not content:
        return ""

    # Split into paragraphs and wrap in <p> tags
    paragraphs = content.split('\n\n')
    formatted_paragraphs = []

    for paragraph in paragraphs:
        if paragraph.strip():
            formatted_paragraphs.append(f"<p>{paragraph.strip()}</p>")

    return '\n'.join(formatted_paragraphs)


def modify_iframe_size(iframe_code: str, width: int, height: int) -> str:
    """
    Modify iframe dimensions to specified size.

    Updates both attribute-based and style-based width/height specifications.

    Args:
        iframe_code: HTML iframe code
        width: Desired width in pixels
        height: Desired height in pixels

    Returns:
        Modified iframe HTML with new dimensions

    Examples:
        >>> modify_iframe_size('<iframe width="600" height="450"></iframe>', 800, 600)
        '<iframe width="800" height="600"></iframe>'
        >>> modify_iframe_size('<iframe style="width: 600px; height: 450px;"></iframe>', 800, 600)
        '<iframe style="width: 800px; height: 600px;"></iframe>'
    """
    # Replace width and height attributes
    iframe_code = re.sub(r'width="[^"]*"', f'width="{width}"', iframe_code)
    iframe_code = re.sub(r'height="[^"]*"', f'height="{height}"', iframe_code)

    # Also replace in style attribute if present
    iframe_code = re.sub(r"width:\s*\d+px", f"width: {width}px", iframe_code)
    iframe_code = re.sub(r"height:\s*\d+px", f"height: {height}px", iframe_code)

    return iframe_code
