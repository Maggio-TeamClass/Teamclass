"""Vendor source search and candidate collection pipeline."""

from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from typing import Protocol
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from .models import GiftCandidate, GiftSearchQuery, SearchResult
from .source_registry import ApprovedSourceRegistry


class SearchProvider(Protocol):
    """Provider contract for external search integrations."""

    def search(self, query: GiftSearchQuery) -> list[SearchResult]:
        """Return raw search results for a normalized query."""


class VendorSearchPipeline:
    """Collect candidate gifts from approved vendor sources."""

    def __init__(self, source_registry: ApprovedSourceRegistry, search_provider: SearchProvider) -> None:
        self._source_registry = source_registry
        self._search_provider = search_provider

    def collect_candidates(self, query: GiftSearchQuery) -> list[GiftCandidate]:
        """Fetch, filter, and normalize candidates from search results."""
        raw_results = self._search_provider.search(query)
        candidates: list[GiftCandidate] = []
        seen_urls: set[str] = set()

        for result in raw_results:
            domain = result.source_domain or self._source_registry.extract_domain(result.url)
            if not self._source_registry.is_approved(domain):
                continue

            canonical_url = self._canonicalize_url(result.url)
            if canonical_url in seen_urls:
                continue
            seen_urls.add(canonical_url)

            matched_interests = self._matched_interests(result, query.interests)
            candidate = GiftCandidate(
                candidate_id=self._candidate_id(canonical_url, result.title),
                title=result.title.strip(),
                url=canonical_url,
                source_domain=domain or "",
                price=result.price,
                currency=result.currency,
                snippet=result.snippet,
                matched_interests=matched_interests,
                metadata=asdict(result),
            )
            candidates.append(candidate)
            if len(candidates) >= query.max_results:
                break
        return candidates

    def _matched_interests(self, result: SearchResult, interests: list[str]) -> list[str]:
        haystack = " ".join(
            item
            for item in (result.title, result.snippet or "", " ".join(map(str, result.metadata.values())))
            if item
        ).lower()
        return [interest for interest in interests if interest.lower() in haystack]

    @staticmethod
    def _canonicalize_url(url: str) -> str:
        cleaned = url.strip()
        parsed = urlparse(cleaned)
        if not parsed.scheme or not parsed.netloc:
            return cleaned.rstrip("/")

        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        path = parsed.path.rstrip("/") or "/"
        # Keep non-tracking parameters while stripping common campaign tags.
        query_pairs = [
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if not key.lower().startswith("utm_")
        ]
        query = urlencode(query_pairs)
        canonical = urlunparse((parsed.scheme.lower(), netloc, path, "", query, ""))
        return canonical.rstrip("/")

    @staticmethod
    def _candidate_id(url: str, title: str) -> str:
        digest = sha256(f"{url}|{title.strip().lower()}".encode("utf-8")).hexdigest()
        return digest[:16]
