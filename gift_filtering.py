"""Constraint-based gift option filtering for recommendation pipelines.

This module provides a lightweight, dependency-free filter layer that can be
used after sourcing candidate gift options and before ranking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class GiftOption:
    """Represents a sourced candidate gift option."""

    name: str
    unit_price: float
    min_order_quantity: int = 1
    max_order_quantity: int | None = None
    ships_to_regions: frozenset[str] = field(default_factory=frozenset)
    excluded_occasions: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "GiftOption":
        """Build a GiftOption from a dict-like payload.

        Accepted keys:
          - name (str)
          - unit_price (number)
          - min_order_quantity (int, optional, default 1)
          - max_order_quantity (int | None, optional, default None)
          - ships_to_regions (iterable[str], optional)
          - excluded_occasions (iterable[str], optional)
        """

        name = str(payload["name"])
        unit_price = float(payload["unit_price"])
        min_order_quantity = int(payload.get("min_order_quantity", 1))
        max_order_quantity_raw = payload.get("max_order_quantity")
        max_order_quantity = (
            None if max_order_quantity_raw is None else int(max_order_quantity_raw)
        )
        if min_order_quantity < 1:
            raise ValueError("min_order_quantity must be >= 1")
        if (
            max_order_quantity is not None
            and max_order_quantity < min_order_quantity
        ):
            raise ValueError("max_order_quantity cannot be less than min_order_quantity")
        ships_to_regions = _normalize_set(payload.get("ships_to_regions", []))
        excluded_occasions = _normalize_set(payload.get("excluded_occasions", []))
        return cls(
            name=name,
            unit_price=unit_price,
            min_order_quantity=min_order_quantity,
            max_order_quantity=max_order_quantity,
            ships_to_regions=ships_to_regions,
            excluded_occasions=excluded_occasions,
        )


@dataclass(frozen=True)
class RequestConstraints:
    """Filters that a recommendation request can impose."""

    min_budget_per_unit: float | None = None
    max_budget_per_unit: float | None = None
    quantity: int = 1
    shipping_region: str | None = None
    occasion: str | None = None
    max_total_budget: float | None = None

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise ValueError("quantity must be >= 1")
        if (
            self.min_budget_per_unit is not None
            and self.max_budget_per_unit is not None
            and self.min_budget_per_unit > self.max_budget_per_unit
        ):
            raise ValueError("min_budget_per_unit cannot exceed max_budget_per_unit")


def filter_gift_options(
    options: Iterable[GiftOption | Mapping[str, object]],
    constraints: RequestConstraints,
) -> list[GiftOption]:
    """Apply budget, quantity, shipping, and occasion constraints.

    Rules:
      - Exclude options priced below min_budget_per_unit.
      - Exclude options priced above max_budget_per_unit.
      - Exclude options whose order quantity constraints are not satisfied.
      - Exclude options whose total cost (unit_price * quantity) exceeds
        max_total_budget when max_total_budget is provided.
      - Exclude options that do not ship to shipping_region.
      - Exclude options explicitly disallowed for occasion.
    """

    region = _normalize_token(constraints.shipping_region)
    occasion = _normalize_token(constraints.occasion)

    accepted: list[GiftOption] = []
    for candidate in options:
        option = (
            candidate
            if isinstance(candidate, GiftOption)
            else GiftOption.from_mapping(candidate)
        )

        if constraints.min_budget_per_unit is not None and (
            option.unit_price < constraints.min_budget_per_unit
        ):
            continue

        if constraints.max_budget_per_unit is not None and (
            option.unit_price > constraints.max_budget_per_unit
        ):
            continue

        if constraints.quantity < option.min_order_quantity:
            continue

        if (
            option.max_order_quantity is not None
            and constraints.quantity > option.max_order_quantity
        ):
            continue

        if constraints.max_total_budget is not None and (
            option.unit_price * constraints.quantity > constraints.max_total_budget
        ):
            continue

        if region and region not in option.ships_to_regions:
            continue

        if occasion and occasion in option.excluded_occasions:
            continue

        accepted.append(option)

    return accepted


def _normalize_set(values: object) -> frozenset[str]:
    if values is None:
        return frozenset()
    if not isinstance(values, Iterable) or isinstance(values, (str, bytes)):
        raise TypeError("expected an iterable of strings")
    return frozenset(_normalize_token(value) for value in values if _normalize_token(value))


def _normalize_token(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()
