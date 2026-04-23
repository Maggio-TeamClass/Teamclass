"""Utilities to parse and normalize sourced gift candidate metadata."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Iterable, Mapping
from urllib.parse import urljoin, urlparse, urlunparse


_WHITESPACE_RE = re.compile(r"\s+")
_KEY_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")
_PRICE_NUMBER_RE = re.compile(r"-?\d[\d.,]*")
_CURRENCY_CODE_RE = re.compile(r"\b([A-Z]{3})\b")


_SYMBOL_TO_CURRENCY = {
    "$": "USD",
    "US$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "₹": "INR",
    "C$": "CAD",
    "A$": "AUD",
}


@dataclass(frozen=True)
class NormalizedGiftCandidate:
    """Normalized shape used by ranking and recommendation steps."""

    title: str | None
    price: float | None
    currency: str | None
    vendor: str | None
    category: str | None
    availability: str
    destination_url: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_candidate(
    candidate: Mapping[str, Any], base_url: str | None = None
) -> NormalizedGiftCandidate:
    """Normalize a single candidate result from external source metadata."""

    flattened: list[tuple[tuple[str, ...], Any]] = []
    _flatten(candidate, (), flattened)

    title = _normalize_text(
        _pick_value(
            flattened,
            preferred_paths=(
                ("title",),
                ("name",),
                ("product", "title"),
                ("item", "title"),
                ("product_name",),
            ),
            fallback_last_tokens={"title", "name", "product_title", "item_title"},
        )
    )

    price_raw = _pick_value(
        flattened,
        preferred_paths=(
            ("price",),
            ("sale_price",),
            ("amount",),
            ("cost",),
            ("offer", "price"),
            ("pricing", "price"),
            ("pricing", "amount"),
            ("offer", "amount"),
            ("price", "amount"),
            ("price", "value"),
        ),
        fallback_last_tokens={"price", "amount", "cost", "value"},
    )
    price, currency = _parse_price(price_raw)

    vendor = _normalize_text(
        _pick_value(
            flattened,
            preferred_paths=(
                ("vendor",),
                ("merchant",),
                ("seller",),
                ("brand",),
                ("merchant", "name"),
                ("seller", "name"),
                ("vendor", "name"),
                ("store", "name"),
            ),
            fallback_last_tokens={"vendor", "merchant", "seller", "brand", "store"},
        )
    )

    category = _normalize_text(
        _pick_value(
            flattened,
            preferred_paths=(
                ("category",),
                ("product_type",),
                ("type",),
                ("taxonomy", "category"),
                ("department",),
            ),
            fallback_last_tokens={"category", "product_type", "department", "vertical"},
        )
    )

    availability = _normalize_availability(
        _pick_value(
            flattened,
            preferred_paths=(
                ("availability",),
                ("stock",),
                ("stock", "status"),
                ("inventory", "status"),
                ("in_stock",),
            ),
            fallback_last_tokens={"availability", "stock", "inventory", "in_stock"},
        )
    )

    destination_url = _normalize_url(
        _pick_value(
            flattened,
            preferred_paths=(
                ("destination_url",),
                ("url",),
                ("link",),
                ("product_url",),
                ("href",),
                ("links", "product"),
                ("product", "url"),
                ("destination", "url"),
            ),
            fallback_last_tokens={"url", "link", "href", "destination_url", "product_url"},
        ),
        base_url=base_url,
    )

    return NormalizedGiftCandidate(
        title=title,
        price=price,
        currency=currency,
        vendor=vendor,
        category=category,
        availability=availability,
        destination_url=destination_url,
    )


def normalize_candidates(
    candidates: Iterable[Mapping[str, Any]], base_url: str | None = None
) -> list[NormalizedGiftCandidate]:
    return [normalize_candidate(candidate, base_url=base_url) for candidate in candidates]


def _flatten(
    value: Any, path: tuple[str, ...], flattened: list[tuple[tuple[str, ...], Any]]
) -> None:
    if isinstance(value, Mapping):
        for key, subvalue in value.items():
            normalized_key = _normalize_key(str(key))
            if not normalized_key:
                continue
            _flatten(subvalue, path + (normalized_key,), flattened)
        return

    if isinstance(value, list):
        for idx, item in enumerate(value):
            _flatten(item, path + (str(idx),), flattened)
        return

    flattened.append((path, value))


def _normalize_key(key: str) -> str:
    key = key.strip().lower()
    key = _KEY_NORMALIZE_RE.sub("_", key)
    return key.strip("_")


def _pick_value(
    flattened: list[tuple[tuple[str, ...], Any]],
    preferred_paths: tuple[tuple[str, ...], ...],
    fallback_last_tokens: set[str],
) -> Any:
    for preferred_path in preferred_paths:
        for path, value in flattened:
            if path == preferred_path:
                return value

    for path, value in flattened:
        if path and path[-1] in fallback_last_tokens:
            return value

    return None


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, list):
        for item in value:
            text = _normalize_text(item)
            if text:
                return text
        return None

    text = str(value).strip()
    if not text:
        return None
    return _WHITESPACE_RE.sub(" ", text)


def _parse_price(value: Any) -> tuple[float | None, str | None]:
    if value is None:
        return None, None

    if isinstance(value, bool):
        return None, None

    if isinstance(value, (int, float)):
        return float(value), None

    text = _normalize_text(value)
    if not text:
        return None, None

    currency = _extract_currency(text)
    number_match = _PRICE_NUMBER_RE.search(text)
    if not number_match:
        return None, currency

    amount = _parse_number(number_match.group(0))
    return amount, currency


def _extract_currency(text: str) -> str | None:
    for symbol, currency in _SYMBOL_TO_CURRENCY.items():
        if symbol in text:
            return currency

    code_match = _CURRENCY_CODE_RE.search(text.upper())
    if code_match:
        return code_match.group(1)
    return None


def _parse_number(text: str) -> float | None:
    cleaned = text.strip()
    if not cleaned:
        return None

    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        comma_index = cleaned.rfind(",")
        digits_after = len(cleaned) - comma_index - 1
        if digits_after in (1, 2):
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")

    try:
        return float(cleaned)
    except ValueError:
        return None


def _normalize_availability(value: Any) -> str:
    if value is None:
        return "unknown"

    if isinstance(value, bool):
        return "in_stock" if value else "out_of_stock"

    if isinstance(value, (int, float)):
        return "in_stock" if value > 0 else "out_of_stock"

    text = _normalize_text(value)
    if not text:
        return "unknown"

    normalized = text.lower()

    if any(
        token in normalized
        for token in (
            "out of stock",
            "sold out",
            "unavailable",
            "not available",
            "discontinued",
            "no stock",
        )
    ):
        return "out_of_stock"

    if any(token in normalized for token in ("preorder", "pre-order", "coming soon", "backorder", "back-order")):
        return "preorder"

    if any(
        token in normalized
        for token in ("limited", "few left", "low stock", "running low", "only ")
    ):
        return "limited"

    if any(
        token in normalized
        for token in ("in stock", "available", "ships", "ready to ship", "instock")
    ):
        return "in_stock"

    return "unknown"


def _normalize_url(value: Any, base_url: str | None) -> str | None:
    text = _normalize_text(value)
    if not text:
        return None

    text = text.strip()
    if text.startswith("//"):
        text = f"https:{text}"

    parsed = urlparse(text)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return _drop_fragment(text)

    if not parsed.scheme and parsed.path.startswith("www."):
        candidate = f"https://{parsed.path}"
        parsed_candidate = urlparse(candidate)
        if parsed_candidate.netloc:
            return _drop_fragment(candidate)

    if base_url:
        joined = urljoin(base_url, text)
        parsed_joined = urlparse(joined)
        if parsed_joined.scheme in ("http", "https") and parsed_joined.netloc:
            return _drop_fragment(joined)

    return None


def _drop_fragment(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(fragment=""))
