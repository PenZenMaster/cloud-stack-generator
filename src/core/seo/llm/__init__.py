"""
Module/Script Name: LLM Provider Package
Path: src/core/seo/llm/__init__.py

Description:
LLM provider abstraction for SEO analysis.
Supports multiple LLM providers (Claude, OpenAI) with model selection.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2026-02-17

Last Modified Date:
2026-02-17

Comments:
* v1.00 - Initial LLM provider abstraction
"""

from .provider import LLMProvider, LLMResponse, ModelPreset
from .claude_provider import ClaudeProvider
# OpenAI provider deferred to Phase 2.1
# from .openai_provider import OpenAIProvider

__all__ = [
    "LLMProvider",
    "LLMResponse",
    "ModelPreset",
    "ClaudeProvider",
    # "OpenAIProvider",  # Phase 2.1
]
