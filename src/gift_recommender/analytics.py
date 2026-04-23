"""Session analytics instrumentation for recommendation quality metrics."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class AnalyticsEvent(str, Enum):
    """Canonical analytics event names for recommendation sessions."""

    SESSION_STARTED = "recommendation.session_started"
    SHORTLIST_VIEWED = "recommendation.shortlist_viewed"
    SHORTLIST_ITEM_CLICKED = "recommendation.shortlist_item_clicked"
    REFINEMENT_REQUESTED = "recommendation.refinement_requested"
    RECOMMENDATION_MARKED_USEFUL = "recommendation.marked_useful"
    RECOMMENDATION_MARKED_NOT_USEFUL = "recommendation.marked_not_useful"
    SESSION_NO_RESULTS = "recommendation.session_no_results"
    SESSION_LOW_CONFIDENCE = "recommendation.session_low_confidence"
    SESSION_COMPLETED = "recommendation.session_completed"


@dataclass(slots=True)
class EventRecord:
    """In-memory event record used by analytics sinks."""

    name: AnalyticsEvent
    session_id: str
    properties: dict[str, object] = field(default_factory=dict)


class AnalyticsSink:
    """Contract for analytics emission backends."""

    def track(self, event: EventRecord) -> None:
        """Persist an analytics event."""


@dataclass(slots=True)
class InMemoryAnalyticsSink(AnalyticsSink):
    """Simple sink to support local tests and lightweight integrations."""

    events: list[EventRecord] = field(default_factory=list)

    def track(self, event: EventRecord) -> None:
        self.events.append(event)


@dataclass(slots=True)
class SessionMetrics:
    """Aggregated, queryable metrics for a recommendation session."""

    session_id: str
    total_recommendations_returned: int = 0
    shortlist_clicks: int = 0
    refinements: int = 0
    useful_feedback_count: int = 0
    not_useful_feedback_count: int = 0
    low_confidence: bool = False
    no_results: bool = False

    @property
    def has_usefulness_feedback(self) -> bool:
        return (self.useful_feedback_count + self.not_useful_feedback_count) > 0

    @property
    def usefulness_rate(self) -> float | None:
        total_feedback = self.useful_feedback_count + self.not_useful_feedback_count
        if total_feedback == 0:
            return None
        return self.useful_feedback_count / total_feedback


class RecommendationSessionAnalytics:
    """Tracks recommendation success metrics and analytics events."""

    def __init__(
        self,
        session_id: str,
        sink: AnalyticsSink,
        *,
        low_confidence_threshold: float = 0.45,
    ) -> None:
        if not session_id.strip():
            raise ValueError("session_id must not be empty")
        if low_confidence_threshold < 0 or low_confidence_threshold > 1:
            raise ValueError("low_confidence_threshold must be between 0 and 1")

        self._session_id = session_id
        self._sink = sink
        self._low_confidence_threshold = low_confidence_threshold
        self._metrics = SessionMetrics(session_id=session_id)
        self._started = False
        self._completed = False

    @property
    def metrics(self) -> SessionMetrics:
        return self._metrics

    def start_session(self, *, request_context: dict[str, object] | None = None) -> None:
        self._ensure_not_completed()
        if self._started:
            return
        self._started = True
        self._track(AnalyticsEvent.SESSION_STARTED, request_context=request_context or {})

    def record_shortlist_view(self, *, recommendation_count: int, avg_confidence: float | None = None) -> None:
        self._ensure_started()
        if recommendation_count < 0:
            raise ValueError("recommendation_count cannot be negative")
        self._metrics.total_recommendations_returned = recommendation_count
        self._metrics.no_results = recommendation_count == 0

        event_payload: dict[str, object] = {"recommendation_count": recommendation_count}
        if avg_confidence is not None:
            self._validate_confidence(avg_confidence)
            is_low_conf = avg_confidence < self._low_confidence_threshold
            self._metrics.low_confidence = is_low_conf
            event_payload["avg_confidence"] = avg_confidence
            event_payload["low_confidence_threshold"] = self._low_confidence_threshold

        self._track(AnalyticsEvent.SHORTLIST_VIEWED, **event_payload)

        if self._metrics.no_results:
            self._track(AnalyticsEvent.SESSION_NO_RESULTS, recommendation_count=recommendation_count)
        if self._metrics.low_confidence:
            self._track(
                AnalyticsEvent.SESSION_LOW_CONFIDENCE,
                avg_confidence=avg_confidence,
                low_confidence_threshold=self._low_confidence_threshold,
            )

    def record_shortlist_click(self, *, candidate_id: str, rank: int | None = None) -> None:
        self._ensure_started()
        if not candidate_id.strip():
            raise ValueError("candidate_id must not be empty")
        if rank is not None and rank < 1:
            raise ValueError("rank must be greater than 0")
        self._metrics.shortlist_clicks += 1
        payload: dict[str, object] = {
            "candidate_id": candidate_id,
            "shortlist_click_count": self._metrics.shortlist_clicks,
        }
        if rank is not None:
            payload["rank"] = rank
        self._track(AnalyticsEvent.SHORTLIST_ITEM_CLICKED, **payload)

    def record_refinement(self, *, refinement_type: str, changed_fields: list[str] | None = None) -> None:
        self._ensure_started()
        if not refinement_type.strip():
            raise ValueError("refinement_type must not be empty")
        self._metrics.refinements += 1
        self._track(
            AnalyticsEvent.REFINEMENT_REQUESTED,
            refinement_type=refinement_type,
            changed_fields=changed_fields or [],
            refinement_count=self._metrics.refinements,
        )

    def record_usefulness_feedback(self, *, useful: bool, candidate_id: str | None = None) -> None:
        self._ensure_started()
        if candidate_id is not None and not candidate_id.strip():
            raise ValueError("candidate_id must not be empty when provided")

        if useful:
            self._metrics.useful_feedback_count += 1
            event = AnalyticsEvent.RECOMMENDATION_MARKED_USEFUL
        else:
            self._metrics.not_useful_feedback_count += 1
            event = AnalyticsEvent.RECOMMENDATION_MARKED_NOT_USEFUL

        payload: dict[str, object] = {
            "useful_feedback_count": self._metrics.useful_feedback_count,
            "not_useful_feedback_count": self._metrics.not_useful_feedback_count,
            "usefulness_rate": self._metrics.usefulness_rate,
        }
        if candidate_id:
            payload["candidate_id"] = candidate_id
        self._track(event, **payload)

    def complete_session(self) -> SessionMetrics:
        self._ensure_started()
        if self._completed:
            return self._metrics
        self._completed = True
        self._track(
            AnalyticsEvent.SESSION_COMPLETED,
            recommendations_returned=self._metrics.total_recommendations_returned,
            shortlist_clicks=self._metrics.shortlist_clicks,
            refinements=self._metrics.refinements,
            useful_feedback_count=self._metrics.useful_feedback_count,
            not_useful_feedback_count=self._metrics.not_useful_feedback_count,
            usefulness_rate=self._metrics.usefulness_rate,
            no_results=self._metrics.no_results,
            low_confidence=self._metrics.low_confidence,
        )
        return self._metrics

    def _track(self, event: AnalyticsEvent, **properties: object) -> None:
        self._sink.track(EventRecord(name=event, session_id=self._session_id, properties=properties))

    def _ensure_started(self) -> None:
        if not self._started:
            raise RuntimeError("start_session must be called before tracking events")
        self._ensure_not_completed()

    def _ensure_not_completed(self) -> None:
        if self._completed:
            raise RuntimeError("session has already been completed")

    @staticmethod
    def _validate_confidence(value: float) -> None:
        if value < 0 or value > 1:
            raise ValueError("confidence values must be between 0 and 1")
