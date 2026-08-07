"""
Module/Script Name: Entity Schema Resolver
Path: src/core/generators/content/entity_schema.py

Description:
Determines the schema.org entity type for a page and whether NAP data
(address/telephone/email/geo) may be included in its structured data.

LocalBusiness + NAP is reserved for main_site properties only. Asserting
the client's real-world entity from a buffer or resource property
fragments the NAP signals Google uses for local pack ranking, and
undermines the independent-entity story the buffer network depends on.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-08-07

Last Modified Date:
2026-08-07

Comments:
* v1.00 - Initial implementation for issue #36
"""

from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ...config.models import ClientConfig


def resolve_entity_schema(config: "ClientConfig") -> Dict[str, Any]:
    """
    Determine the schema.org entity type and NAP inclusion for a page.

    Args:
        config: Client configuration

    Returns:
        Dict with:
            entity_additional_type: None, "Organization", or "LocalBusiness" -
                the second @type alongside "WebPage", or None for resource
                sites which get "WebPage" alone.
            include_nap_schema: bool - whether address/telephone/email/geo
                may be included.
    """
    site_type = getattr(config.cloud, "site_type", "main_site")

    if site_type == "resource":
        return {"entity_additional_type": None, "include_nap_schema": False}

    if site_type != "main_site":
        return {"entity_additional_type": "Organization", "include_nap_schema": False}

    gbp = getattr(config, "google_business_profile", None)
    gbp_expose = getattr(gbp, "expose_address", False) if gbp else False

    address = getattr(config.contact, "address", None)
    address_publish = getattr(address, "publish_on_website", True) if address else False

    has_public_address = gbp_expose or address_publish
    if has_public_address:
        return {"entity_additional_type": "LocalBusiness", "include_nap_schema": True}

    return {"entity_additional_type": "Organization", "include_nap_schema": False}
