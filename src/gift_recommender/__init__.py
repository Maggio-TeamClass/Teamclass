"""Gift recommendation service package."""

from .models import GiftCandidate, GiftSearchQuery, SearchResult
from .pipeline import VendorSearchPipeline
from .source_registry import ApprovedSourceRegistry

__all__ = [
    "ApprovedSourceRegistry",
    "GiftCandidate",
    "GiftSearchQuery",
    "SearchResult",
    "VendorSearchPipeline",
]
