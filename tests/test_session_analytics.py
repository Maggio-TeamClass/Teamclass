from gift_recommender.analytics import (
    AnalyticsEvent,
    InMemoryAnalyticsSink,
    RecommendationSessionAnalytics,
)


def _event_names(sink: InMemoryAnalyticsSink) -> list[AnalyticsEvent]:
    return [event.name for event in sink.events]


def test_tracks_required_success_metric_events() -> None:
    sink = InMemoryAnalyticsSink()
    analytics = RecommendationSessionAnalytics(session_id="session-123", sink=sink)

    analytics.start_session(request_context={"channel": "chat"})
    analytics.record_shortlist_view(recommendation_count=3, avg_confidence=0.76)
    analytics.record_shortlist_click(candidate_id="cand-1", rank=1)
    analytics.record_refinement(refinement_type="budget_update", changed_fields=["budget_min", "budget_max"])
    analytics.record_usefulness_feedback(useful=True, candidate_id="cand-1")
    metrics = analytics.complete_session()

    assert metrics.total_recommendations_returned == 3
    assert metrics.shortlist_clicks == 1
    assert metrics.refinements == 1
    assert metrics.useful_feedback_count == 1
    assert metrics.not_useful_feedback_count == 0
    assert metrics.usefulness_rate == 1.0
    assert metrics.no_results is False
    assert metrics.low_confidence is False

    assert _event_names(sink) == [
        AnalyticsEvent.SESSION_STARTED,
        AnalyticsEvent.SHORTLIST_VIEWED,
        AnalyticsEvent.SHORTLIST_ITEM_CLICKED,
        AnalyticsEvent.REFINEMENT_REQUESTED,
        AnalyticsEvent.RECOMMENDATION_MARKED_USEFUL,
        AnalyticsEvent.SESSION_COMPLETED,
    ]


def test_tracks_no_results_and_low_confidence_sessions() -> None:
    sink = InMemoryAnalyticsSink()
    analytics = RecommendationSessionAnalytics(
        session_id="session-456",
        sink=sink,
        low_confidence_threshold=0.6,
    )

    analytics.start_session()
    analytics.record_shortlist_view(recommendation_count=0, avg_confidence=0.42)
    analytics.record_usefulness_feedback(useful=False)
    metrics = analytics.complete_session()

    assert metrics.no_results is True
    assert metrics.low_confidence is True
    assert metrics.not_useful_feedback_count == 1
    assert metrics.usefulness_rate == 0.0

    assert _event_names(sink) == [
        AnalyticsEvent.SESSION_STARTED,
        AnalyticsEvent.SHORTLIST_VIEWED,
        AnalyticsEvent.SESSION_NO_RESULTS,
        AnalyticsEvent.SESSION_LOW_CONFIDENCE,
        AnalyticsEvent.RECOMMENDATION_MARKED_NOT_USEFUL,
        AnalyticsEvent.SESSION_COMPLETED,
    ]


def test_refinement_counter_increments_each_time() -> None:
    sink = InMemoryAnalyticsSink()
    analytics = RecommendationSessionAnalytics(session_id="session-789", sink=sink)

    analytics.start_session()
    analytics.record_shortlist_view(recommendation_count=2)
    analytics.record_refinement(refinement_type="region_update", changed_fields=["region"])
    analytics.record_refinement(refinement_type="interest_update", changed_fields=["interests"])
    analytics.complete_session()

    refinement_events = [
        event
        for event in sink.events
        if event.name == AnalyticsEvent.REFINEMENT_REQUESTED
    ]
    assert len(refinement_events) == 2
    assert refinement_events[0].properties["refinement_count"] == 1
    assert refinement_events[1].properties["refinement_count"] == 2


def test_requires_start_before_other_event_tracking() -> None:
    sink = InMemoryAnalyticsSink()
    analytics = RecommendationSessionAnalytics(session_id="session-guard", sink=sink)

    try:
        analytics.record_shortlist_click(candidate_id="cand-2")
        raised = False
    except RuntimeError:
        raised = True

    assert raised is True
