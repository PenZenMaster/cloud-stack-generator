"""
Module/Script Name: Content Uniqueness Gate
Path: src/core/quality/uniqueness_gate.py

Description:
Scores generated pages for pairwise content similarity and blocks publish
when pages are too similar to each other - the definition of scaled content
abuse when a config carries 100+ near-identical city pages. See issue #38.

Uses 5-word shingling + MinHash signatures + LSH banding so scoring stays
near-linear rather than O(n^2) as page counts grow: pages are only compared
directly when they land in the same LSH bucket for at least one band, and
truly dissimilar pages typically share no bucket at all. Pure standard
library - no new dependencies.

Deferred (see issue #38 for full scope): embedding-based scoring, live
money-site comparison, and the AI regeneration retry loop are not
implemented here - this module is the shingle-based core gate only.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-08-08

Last Modified Date:
2026-08-08

Comments:
* v1.00 - Initial implementation for issue #38 (core engine only)
"""

import hashlib
import logging
import random
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)

DEFAULT_SHINGLE_SIZE = 5
DEFAULT_NUM_HASHES = 64
DEFAULT_LSH_BANDS = 16
DEFAULT_WARN_THRESHOLD = 0.75
DEFAULT_BLOCK_THRESHOLD = 0.85
_WORST_PAIRS_LIMIT = 20

# 2^61 - 1, a Mersenne prime - large enough to keep hash collisions
# negligible for realistic page counts, small enough for fast modular math.
_HASH_PRIME = (1 << 61) - 1

_WORD_RE = re.compile(r"[a-z0-9']+")
_TAG_STRIP_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


class UniquenessGateError(Exception):
    """Raised when generated pages are too similar to publish."""


def strip_html(html: str) -> str:
    """Extract visible text from an HTML page for shingling."""
    text = _TAG_STRIP_RE.sub(" ", html)
    text = _TAG_RE.sub(" ", text)
    return _WHITESPACE_RE.sub(" ", text).strip()


def extract_shingles(text: str, shingle_size: int = DEFAULT_SHINGLE_SIZE) -> Set[str]:
    """Tokenize text into words and build a set of word-level shingles."""
    words = _WORD_RE.findall(text.lower())
    if not words:
        return set()
    if len(words) < shingle_size:
        return {" ".join(words)}
    return {
        " ".join(words[i:i + shingle_size])
        for i in range(len(words) - shingle_size + 1)
    }


class MinHasher:
    """Deterministic MinHash signature generator using universal hashing."""

    def __init__(self, num_hashes: int = DEFAULT_NUM_HASHES, seed: int = 1):
        rng = random.Random(seed)
        self.num_hashes = num_hashes
        self._coeffs: List[Tuple[int, int]] = [
            (rng.randrange(1, _HASH_PRIME), rng.randrange(0, _HASH_PRIME))
            for _ in range(num_hashes)
        ]

    def signature(self, shingles: Set[str]) -> Tuple[int, ...]:
        """Compute a fixed-size MinHash signature for a shingle set."""
        if not shingles:
            return tuple([_HASH_PRIME] * self.num_hashes)

        hashed = [
            int.from_bytes(hashlib.sha1(s.encode("utf-8")).digest()[:8], "big")
            for s in shingles
        ]
        return tuple(
            min((a * h + b) % _HASH_PRIME for h in hashed)
            for a, b in self._coeffs
        )


def estimated_jaccard(sig_a: Tuple[int, ...], sig_b: Tuple[int, ...]) -> float:
    """Estimate Jaccard similarity from two MinHash signatures."""
    if not sig_a or not sig_b:
        return 0.0
    matches = sum(1 for x, y in zip(sig_a, sig_b) if x == y)
    return matches / len(sig_a)


def lsh_bucket_keys(
    signature: Tuple[int, ...], bands: int = DEFAULT_LSH_BANDS
) -> List[Tuple[int, Tuple[int, ...]]]:
    """Split a MinHash signature into banded bucket keys for LSH candidate lookup."""
    n = len(signature)
    bands = max(1, min(bands, n))
    rows = max(1, n // bands)
    keys = []
    for b in range(bands):
        start = b * rows
        end = start + rows if b < bands - 1 else n
        keys.append((b, signature[start:end]))
    return keys


@dataclass
class PageSimilarity:
    """A single pairwise similarity score between two pages."""

    page_id: str
    other_page_id: str
    similarity: float


@dataclass
class UniquenessReport:
    """Result of scoring a batch of pages for pairwise similarity."""

    max_similarity: Dict[str, float] = field(default_factory=dict)
    worst_pairs: List[PageSimilarity] = field(default_factory=list)
    mean_pairwise_similarity: float = 0.0

    def blocked_pages(self, block_threshold: float) -> Set[str]:
        """Pages whose max similarity to another page meets/exceeds block_threshold."""
        return {p for p, s in self.max_similarity.items() if s >= block_threshold}

    def warned_pages(self, warn_threshold: float) -> Set[str]:
        """Pages whose max similarity to another page meets/exceeds warn_threshold."""
        return {p for p, s in self.max_similarity.items() if s >= warn_threshold}


class UniquenessGate:
    """
    Scores a batch of generated pages for pairwise content similarity and
    blocks publish when any pair is too similar, using MinHash/LSH shingle
    comparison to stay near-linear as page counts grow.

    One instance should be used for a single generation run: call
    add_page() for every generated page, then check() once at the end,
    before deployment.
    """

    def __init__(
        self,
        warn_threshold: float = DEFAULT_WARN_THRESHOLD,
        block_threshold: float = DEFAULT_BLOCK_THRESHOLD,
        shingle_size: int = DEFAULT_SHINGLE_SIZE,
        num_hashes: int = DEFAULT_NUM_HASHES,
        lsh_bands: int = DEFAULT_LSH_BANDS,
    ):
        if not (0.0 <= warn_threshold <= 1.0):
            raise ValueError(f"warn_threshold must be between 0.0 and 1.0, got {warn_threshold}")
        if not (0.0 <= block_threshold <= 1.0):
            raise ValueError(f"block_threshold must be between 0.0 and 1.0, got {block_threshold}")
        if block_threshold < warn_threshold:
            raise ValueError(
                f"block_threshold ({block_threshold}) must be >= warn_threshold ({warn_threshold})"
            )

        self.warn_threshold = warn_threshold
        self.block_threshold = block_threshold
        self.shingle_size = shingle_size
        self.lsh_bands = lsh_bands
        self._hasher = MinHasher(num_hashes=num_hashes)
        self._signatures: Dict[str, Tuple[int, ...]] = {}

    def add_page(self, page_id: str, content: str, is_html: bool = True) -> None:
        """
        Add a generated page to the batch to be scored.

        Args:
            page_id: Unique identifier for the page (e.g. output file path
                or slug) - used to report which pages are too similar.
            content: The page's HTML (or plain text if is_html=False).
            is_html: Whether content is HTML that needs tag-stripping first.
        """
        text = strip_html(content) if is_html else content
        shingles = extract_shingles(text, self.shingle_size)
        self._signatures[page_id] = self._hasher.signature(shingles)

    def score(self) -> UniquenessReport:
        """
        Score all added pages for pairwise similarity.

        Uses LSH banding to find candidate pairs (pages sharing at least one
        band bucket) rather than comparing every page against every other
        page directly.
        """
        page_ids = list(self._signatures.keys())
        max_similarity = {pid: 0.0 for pid in page_ids}

        if len(page_ids) < 2:
            return UniquenessReport(max_similarity=max_similarity)

        buckets: Dict[Tuple[int, Tuple[int, ...]], List[str]] = {}
        for pid in page_ids:
            for key in lsh_bucket_keys(self._signatures[pid], self.lsh_bands):
                buckets.setdefault(key, []).append(pid)

        candidate_pairs: Set[Tuple[str, str]] = set()
        for bucket_pages in buckets.values():
            if len(bucket_pages) < 2:
                continue
            for i in range(len(bucket_pages)):
                for j in range(i + 1, len(bucket_pages)):
                    a, b = sorted((bucket_pages[i], bucket_pages[j]))
                    candidate_pairs.add((a, b))

        pair_scores: List[PageSimilarity] = []
        for a, b in candidate_pairs:
            similarity = estimated_jaccard(self._signatures[a], self._signatures[b])
            pair_scores.append(PageSimilarity(a, b, similarity))
            max_similarity[a] = max(max_similarity[a], similarity)
            max_similarity[b] = max(max_similarity[b], similarity)

        mean_pairwise = (
            sum(p.similarity for p in pair_scores) / len(pair_scores) if pair_scores else 0.0
        )
        worst_pairs = sorted(pair_scores, key=lambda p: p.similarity, reverse=True)[:_WORST_PAIRS_LIMIT]

        return UniquenessReport(
            max_similarity=max_similarity,
            worst_pairs=worst_pairs,
            mean_pairwise_similarity=mean_pairwise,
        )

    def check(self) -> UniquenessReport:
        """
        Score all added pages and raise if any pair is too similar to publish.

        Raises:
            UniquenessGateError: if any page's max similarity to another page
                meets/exceeds block_threshold.

        Returns:
            UniquenessReport with the full scoring breakdown, for warned
            (but not blocked) pages and for building a distribution report.
        """
        report = self.score()
        blocked = report.blocked_pages(self.block_threshold)
        warned = report.warned_pages(self.warn_threshold) - blocked

        for page_id in warned:
            logger.warning(
                f"Page '{page_id}' has high content similarity to another page "
                f"in this build (max {report.max_similarity[page_id]:.2f}, "
                f"warn_threshold {self.warn_threshold})"
            )

        if blocked:
            offending = sorted(
                (p for p in report.worst_pairs if p.similarity >= self.block_threshold),
                key=lambda p: p.similarity,
                reverse=True,
            )
            pairs_desc = ", ".join(
                f"{p.page_id} <-> {p.other_page_id} ({p.similarity:.2f})" for p in offending[:10]
            )
            more = f", and {len(offending) - 10} more pair(s)" if len(offending) > 10 else ""
            raise UniquenessGateError(
                f"{len(blocked)} page(s) are too similar to another page in this build "
                f"(similarity >= block_threshold {self.block_threshold}): {pairs_desc}{more}. "
                f"This is the definition of scaled content abuse and risks a Google penalty. "
                f"Add more per-page differentiation, or raise content_quality.block_threshold "
                f"to proceed deliberately."
            )

        return report
