from gift_recommender.models import GiftSearchQuery, SearchResult
from gift_recommender.pipeline import VendorSearchPipeline
from gift_recommender.source_registry import ApprovedSourceRegistry


class FakeSearchProvider:
    def __init__(self, results: list[SearchResult]) -> None:
        self._results = results
        self.last_query: GiftSearchQuery | None = None

    def search(self, query: GiftSearchQuery) -> list[SearchResult]:
        self.last_query = query
        return self._results


def test_collect_candidates_filters_to_approved_sources_and_deduplicates() -> None:
    query = GiftSearchQuery(query_text="wellness gift", interests=["coffee", "remote"], max_results=10)
    provider = FakeSearchProvider(
        results=[
            SearchResult(
                title="Premium Coffee Sampler",
                url="https://www.approved.com/gifts/coffee-box/",
                snippet="A thoughtful coffee kit for remote teams.",
                metadata={"category": "beverages"},
            ),
            SearchResult(
                title="Premium Coffee Sampler Duplicate URL",
                url="https://approved.com/gifts/coffee-box",
                snippet="Duplicate record",
            ),
            SearchResult(
                title="Untrusted Vendor Result",
                url="https://badsource.biz/product/123",
                snippet="Should be dropped",
            ),
            SearchResult(
                title="Subdomain vendor result",
                url="https://shop.approved.com/collections/office",
                snippet="Remote office supplies",
            ),
        ]
    )
    registry = ApprovedSourceRegistry.from_domains({"approved.com", "curatedgifts.org"})
    pipeline = VendorSearchPipeline(source_registry=registry, search_provider=provider)

    candidates = pipeline.collect_candidates(query)

    assert provider.last_query == query
    assert len(candidates) == 2
    assert all(candidate.source_domain.endswith("approved.com") for candidate in candidates)
    assert candidates[0].matched_interests == ["coffee", "remote"]
    assert candidates[1].matched_interests == ["remote"]
    assert candidates[0].url == "https://approved.com/gifts/coffee-box"
    assert candidates[0].candidate_id


def test_collect_candidates_honors_max_results() -> None:
    query = GiftSearchQuery(query_text="snacks", max_results=1)
    provider = FakeSearchProvider(
        results=[
            SearchResult(title="A", url="https://approved.com/a"),
            SearchResult(title="B", url="https://approved.com/b"),
        ]
    )
    registry = ApprovedSourceRegistry.from_domains({"approved.com"})
    pipeline = VendorSearchPipeline(source_registry=registry, search_provider=provider)

    candidates = pipeline.collect_candidates(query)

    assert len(candidates) == 1
    assert candidates[0].title == "A"


def test_extracts_domain_from_url_when_provider_does_not_supply_source_domain() -> None:
    query = GiftSearchQuery(query_text="desk accessories", max_results=5)
    provider = FakeSearchProvider(
        results=[
            SearchResult(title="Desk Set", url="https://vendor-approved.io/desk/set"),
            SearchResult(title="No Domain URL", url="not-a-url"),
        ]
    )
    registry = ApprovedSourceRegistry.from_domains({"vendor-approved.io"})
    pipeline = VendorSearchPipeline(source_registry=registry, search_provider=provider)

    candidates = pipeline.collect_candidates(query)

    assert len(candidates) == 1
    assert candidates[0].source_domain == "vendor-approved.io"
