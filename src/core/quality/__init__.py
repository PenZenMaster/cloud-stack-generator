"""
Content Quality Package
Path: src/core/quality/__init__.py

Description:
Pre-publish content quality gates - currently the content uniqueness gate
(pairwise similarity scoring across generated pages). See issue #38.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-08-08

Last Modified Date:
2026-08-08

Comments:
* v1.00 - Initial package creation for the content uniqueness gate
"""

from .uniqueness_gate import (
    UniquenessGate,
    UniquenessGateError,
    UniquenessReport,
    PageSimilarity,
)

__all__ = [
    "UniquenessGate",
    "UniquenessGateError",
    "UniquenessReport",
    "PageSimilarity",
]
