"""
Module/Script Name: Anchor Text Selector
Path: src/core/generators/content/anchor_selector.py

Description:
Selects anchor text for outbound links to the money site, drawn from a
weighted pool of categories (branded, naked_url, generic, partial_match,
exact_match) instead of a hardcoded literal. A uniform anchor profile
across every page of every client's buffer network is an unnatural link
signal and a cross-client fingerprint - see issue #37.

Selection is deterministic under a fixed seed, corrects drift toward the
configured target distribution as more anchors are realized, never repeats
an anchor within the same page, and is slot-aware (footer/CTA anchors skew
branded+generic, in-body contextual anchors skew partial-match).

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-08-07

Last Modified Date:
2026-08-07

Comments:
* v1.00 - Initial implementation for issue #37 (core engine only - no UI,
  no distribution report artifact; see issue for deferred scope)
"""

import random
from typing import Any, Dict, List, Optional, Set

DEFAULT_DISTRIBUTION: Dict[str, int] = {
    "branded": 40,
    "naked_url": 15,
    "generic": 20,
    "partial_match": 20,
    "exact_match": 5,
}

# Per-slot weight multipliers layered on top of the target distribution.
# Footer/CTA anchors skew branded+generic (a real footer link is usually
# the brand name or "visit our site"); in-body contextual anchors carry
# more of the partial-match weight (real editorial prose links tend to
# describe what the destination offers, not just name it).
SLOT_WEIGHTS: Dict[str, Dict[str, float]] = {
    "footer": {
        "branded": 1.4,
        "naked_url": 1.2,
        "generic": 1.3,
        "partial_match": 0.6,
        "exact_match": 0.5,
    },
    "body_contextual": {
        "branded": 0.8,
        "naked_url": 0.7,
        "generic": 0.8,
        "partial_match": 1.4,
        "exact_match": 1.1,
    },
}

_DEFICIT_FLOOR = 0.01  # keeps every category reachable even once its target is met


class AnchorSelectionError(Exception):
    """Raised when the configured anchor profile cannot be used safely."""


class AnchorSelector:
    """
    Selects anchor text for a single target URL (the money site) across a
    generation run, tracking realized distribution and correcting drift
    toward the configured targets.

    One instance should be reused across every page rendered in a single
    generator's run so the realized distribution converges over the whole
    site rather than resetting per page.
    """

    def __init__(
        self,
        distribution: Optional[Dict[str, int]] = None,
        pools: Optional[Dict[str, List[str]]] = None,
        seed: int = 0,
        exact_match_ceiling: int = 10,
        business_name: str = "",
        industry: str = "",
        domain: str = "",
        cities: Optional[List[str]] = None,
    ):
        self.distribution = dict(distribution) if distribution else dict(DEFAULT_DISTRIBUTION)

        total = sum(self.distribution.values())
        if total != 100:
            raise AnchorSelectionError(
                f"anchor_profile.distribution must sum to 100, got {total}: {self.distribution}"
            )

        exact_match_share = self.distribution.get("exact_match", 0)
        if exact_match_share > exact_match_ceiling:
            raise AnchorSelectionError(
                f"anchor_profile.distribution.exact_match ({exact_match_share}%) exceeds the "
                f"safety ceiling of {exact_match_ceiling}%. Exact-match anchors are the strongest "
                f"and most easily flagged manipulation signal - keep this share low."
            )

        self.pools = self._build_pools(
            pools or {}, business_name, industry, domain, cities or []
        )
        self._rng = random.Random(seed)
        self._realized: Dict[str, int] = {category: 0 for category in self.distribution}
        self._used_by_page: Dict[str, Set[str]] = {}

    def _build_pools(
        self,
        pools: Dict[str, List[str]],
        business_name: str,
        industry: str,
        domain: str,
        cities: List[str],
    ) -> Dict[str, List[str]]:
        """Auto-generate sane default pools for any category left unconfigured."""
        naked_domain = domain.split("//")[-1].rstrip("/") if domain else ""
        industry_lower = industry.lower() if industry else "services"

        defaults = {
            "branded": [business_name, f"{business_name} {industry}".strip()],
            "naked_url": [naked_domain] if naked_domain else [business_name],
            "generic": [
                "visit their website",
                "learn more",
                "see full details",
                "their main site",
                "find out more",
            ],
            "partial_match": (
                [f"{industry_lower} specialists in {city}" for city in cities[:5]]
                if cities
                else [f"{industry_lower} specialists", f"{industry_lower} experts"]
            ),
            "exact_match": (
                [f"{industry_lower} services {city.lower()}" for city in cities[:3]]
                if cities
                else [f"{industry_lower} services"]
            ),
        }

        resolved = {}
        for category in self.distribution:
            configured = pools.get(category)
            raw = configured if configured is not None else defaults.get(category, [])
            resolved[category] = [a for a in raw if a]

        return resolved

    def select(self, slot: str = "generic", page_id: str = "_default") -> str:
        """
        Select the next anchor text for the given slot on the given page.

        Args:
            slot: "footer" or "body_contextual" (or any key in SLOT_WEIGHTS);
                unrecognized slots use the unweighted target distribution.
            page_id: Identifier for the page this anchor appears on, used to
                guarantee no anchor repeats within the same page.

        Returns:
            Selected anchor text. Falls back to the branded pool if the
            drift-selected category's pool is empty or exhausted for this
            page; falls back to a repeat from the branded pool only as a
            last resort when every pool is exhausted for this page.
        """
        used = self._used_by_page.setdefault(page_id, set())

        category = self._choose_category(slot)
        anchor = self._pick_unused(category, used)

        if anchor is None and category != "branded":
            category = "branded"
            anchor = self._pick_unused("branded", used)

        if anchor is None:
            # Every pool exhausted for this page - last resort, allow a repeat.
            pool = self.pools.get("branded") or [a for p in self.pools.values() for a in p] or [""]
            anchor = self._rng.choice(pool)

        used.add(anchor)
        self._realized[category] = self._realized.get(category, 0) + 1
        return anchor

    def _pick_unused(self, category: str, used: Set[str]) -> Optional[str]:
        pool = self.pools.get(category) or []
        available = [a for a in pool if a not in used]
        if not available:
            return None
        return self._rng.choice(available)

    def _effective_target(self, slot: str) -> Dict[str, float]:
        """
        Re-normalize the configured distribution by this slot's weights, so
        drift correction pulls toward a slot-appropriate mix (e.g. footer
        anchors skewing branded/generic) rather than the raw global target,
        which would otherwise wash out the slot bias entirely once realized
        counts approach the global target.
        """
        weights = SLOT_WEIGHTS.get(slot)
        if not weights:
            return {category: float(pct) for category, pct in self.distribution.items()}

        weighted = {
            category: self.distribution[category] * weights.get(category, 1.0)
            for category in self.distribution
        }
        total = sum(weighted.values()) or 1
        return {category: (v / total) * 100 for category, v in weighted.items()}

    def _choose_category(self, slot: str) -> str:
        effective_target = self._effective_target(slot)
        total_realized = sum(self._realized.values()) or 1

        categories = list(self.distribution.keys())
        scores = []
        for category in categories:
            realized_pct = (self._realized.get(category, 0) / total_realized) * 100
            deficit = max(effective_target[category] - realized_pct, _DEFICIT_FLOOR)
            scores.append(deficit)

        total_score = sum(scores)
        r = self._rng.uniform(0, total_score)
        upto = 0.0
        for category, score in zip(categories, scores):
            upto += score
            if upto >= r:
                return category
        return categories[-1]

    def realized_distribution(self) -> Dict[str, float]:
        """Realized anchor share per category so far, as percentages."""
        total = sum(self._realized.values()) or 1
        return {
            category: round((count / total) * 100, 1)
            for category, count in self._realized.items()
        }

    def realized_counts(self) -> Dict[str, int]:
        """Realized anchor counts per category so far."""
        return dict(self._realized)


def build_anchor_selector(config: Any) -> AnchorSelector:
    """
    Build an AnchorSelector from a ClientConfig's anchor_profile, the
    identity of the entity being linked TO, and the city list.

    For backlink_site (and main_site) configs, the outbound link targets
    the client's own business, so config.business is the right identity.
    For resource sites, the outbound link targets resource_site's money
    site - a different business than the resource site's own editorial
    identity in config.business - so default anchor pools must be built
    from resource_site.money_site_name/url instead, or the auto-generated
    "branded" anchors would name the wrong business.

    Args:
        config: ClientConfig

    Returns:
        AnchorSelector ready for use across a generation run.
    """
    # Defensive against incomplete/mock config objects used in tests unrelated
    # to anchors - anything not shaped like the real dataclasses falls back
    # to AnchorSelector's own defaults rather than raising out of __init__.
    cloud = getattr(config, "cloud", None)
    anchor_profile = getattr(cloud, "anchor_profile", None) if cloud else None

    distribution = getattr(anchor_profile, "distribution", None)
    if not isinstance(distribution, dict):
        distribution = None

    pools = getattr(anchor_profile, "pools", None)
    if not isinstance(pools, dict):
        pools = None

    seed = getattr(anchor_profile, "seed", None)
    if not isinstance(seed, int):
        seed = 0

    exact_match_ceiling = getattr(anchor_profile, "exact_match_ceiling", None)
    if not isinstance(exact_match_ceiling, int):
        exact_match_ceiling = 10

    cities = [
        cp.city_name for cp in getattr(config, "city_pages", []) or []
        if isinstance(getattr(cp, "city_name", None), str)
    ] or [c for c in (getattr(config, "target_cities", []) or []) if isinstance(c, str)]

    site_type = getattr(cloud, "site_type", "main_site") if cloud else "main_site"
    resource_site = getattr(config, "resource_site", None)
    business = getattr(config, "business", None)

    business_name = getattr(business, "business_name", "") or ""
    industry = getattr(business, "industry", "") or ""
    domain = getattr(business, "domain", "") or ""

    if (
        site_type == "resource"
        and resource_site
        and callable(getattr(resource_site, "is_configured", None))
        and resource_site.is_configured()
    ):
        business_name = getattr(resource_site, "money_site_name", "") or business_name
        domain = getattr(resource_site, "money_site_url", "") or domain

    return AnchorSelector(
        distribution=distribution,
        pools=pools,
        seed=seed,
        exact_match_ceiling=exact_match_ceiling,
        business_name=business_name,
        industry=industry,
        domain=domain,
        cities=cities,
    )
