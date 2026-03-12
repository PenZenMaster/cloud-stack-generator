"""
Module/Script Name: Auto Onboarding Package
Path: src/core/onboarding/__init__.py

Description:
Auto-onboarding engine for the AWG project. Given a client website URL,
Google Business Profile share link, and industry, scrapes and extracts
data to generate a pre-populated YAML client config file.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-03-11

Last Modified Date:
2026-03-11

Comments:
* v1.00 - Initial auto-onboarding implementation
"""

from .onboarder import Onboarder, OnboardResult

__all__ = ["Onboarder", "OnboardResult"]
