from gift_filtering import GiftOption, RequestConstraints, filter_gift_options


def _sample_options() -> list[GiftOption]:
    return [
        GiftOption(
            name="Premium Notebook",
            unit_price=45.0,
            min_order_quantity=5,
            max_order_quantity=500,
            ships_to_regions=frozenset({"us", "ca", "uk"}),
            excluded_occasions=frozenset({"memorial"}),
        ),
        GiftOption(
            name="Luxury Hamper",
            unit_price=120.0,
            min_order_quantity=1,
            max_order_quantity=25,
            ships_to_regions=frozenset({"us", "uk"}),
            excluded_occasions=frozenset({"halloween"}),
        ),
        GiftOption(
            name="Desk Plant",
            unit_price=25.0,
            min_order_quantity=1,
            max_order_quantity=None,
            ships_to_regions=frozenset({"eu", "ca"}),
            excluded_occasions=frozenset(),
        ),
    ]


def test_filters_by_budget_range() -> None:
    constraints = RequestConstraints(min_budget_per_unit=40, max_budget_per_unit=100)
    filtered = filter_gift_options(_sample_options(), constraints)
    assert [item.name for item in filtered] == []


def test_filters_by_quantity_bounds() -> None:
    constraints = RequestConstraints(quantity=2)
    filtered = filter_gift_options(_sample_options(), constraints)
    assert [item.name for item in filtered] == ["Luxury Hamper", "Desk Plant"]

    constraints = RequestConstraints(quantity=30)
    filtered = filter_gift_options(_sample_options(), constraints)
    assert [item.name for item in filtered] == ["Premium Notebook", "Desk Plant"]


def test_filters_by_quantity_and_total_budget() -> None:
    constraints = RequestConstraints(quantity=10, max_total_budget=500)
    filtered = filter_gift_options(_sample_options(), constraints)
    assert [item.name for item in filtered] == ["Premium Notebook", "Desk Plant"]


def test_filters_by_shipping_region_case_insensitive() -> None:
    constraints = RequestConstraints(shipping_region="US")
    filtered = filter_gift_options(_sample_options(), constraints)
    assert [item.name for item in filtered] == ["Luxury Hamper"]


def test_filters_by_occasion_exclusions() -> None:
    constraints = RequestConstraints(occasion=" Halloween ")
    filtered = filter_gift_options(_sample_options(), constraints)
    assert [item.name for item in filtered] == ["Premium Notebook", "Desk Plant"]


def test_accepts_dict_payloads_and_normalizes_fields() -> None:
    payload_options = [
        {
            "name": "Tea Box",
            "unit_price": 30,
            "min_order_quantity": 5,
            "max_order_quantity": 10,
            "ships_to_regions": [" US ", "ca"],
            "excluded_occasions": ["retirement"],
        },
        {
            "name": "Wine Crate",
            "unit_price": 80,
            "ships_to_regions": ["eu"],
            "excluded_occasions": [],
        },
    ]
    constraints = RequestConstraints(
        min_budget_per_unit=20,
        max_budget_per_unit=50,
        quantity=6,
        shipping_region="us",
        occasion="RETIREMENT",
    )
    filtered = filter_gift_options(payload_options, constraints)
    assert [item.name for item in filtered] == []


def test_invalid_constraints_raise_error() -> None:
    try:
        RequestConstraints(min_budget_per_unit=100, max_budget_per_unit=50)
    except ValueError as exc:
        assert "min_budget_per_unit cannot exceed max_budget_per_unit" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid budget bounds")
