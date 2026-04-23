"""Domain models for vendor search and candidate collection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class GiftSearchQuery:
    """Normalized search request used by provider integrations."""

    query_text: str
    budget_min: float | None = None
    budget_max: float | None = None
    interests: list[str] = field(default_factory=list)
    recipient_role: str | None = None
    region: str | None = None
    quantity: int | None = None
    max_results: int = 25


@dataclass(slots=True)
class SearchResult:
    """Raw provider result before source filtering and candidate shaping."""

    title: str
    url: str
    source_domain: str | None = None
    price: float | None = None
    currency: str | None = None
    snippet: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GiftCandidate:
    """Candidate gift item passed downstream into ranking/scoring."""

    candidate_id: str
    title: str
    url: str
    source_domain: str
    price: float | None = None
    currency: str | None = None
    snippet: str | None = None
    matched_interests: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
