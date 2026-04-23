"""Approved source registry used by the vendor collection pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse


def _normalize_domain(value: str) -> str:
    cleaned = value.strip().lower()
    if cleaned.startswith("www."):
        cleaned = cleaned[4:]
    return cleaned


@dataclass(slots=True)
class ApprovedSourceRegistry:
    """Holds source allowlist and helper logic for source checks."""

    approved_domains: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.approved_domains = {_normalize_domain(domain) for domain in self.approved_domains}

    @classmethod
    def from_domains(cls, domains: list[str] | set[str]) -> "ApprovedSourceRegistry":
        return cls(approved_domains=set(domains))

    def is_approved(self, domain: str | None) -> bool:
        if not domain:
            return False
        normalized = _normalize_domain(domain)
        if normalized in self.approved_domains:
            return True
        return any(normalized.endswith(f".{allowed}") for allowed in self.approved_domains)

    def extract_domain(self, url: str) -> str | None:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None
        return _normalize_domain(parsed.netloc)
