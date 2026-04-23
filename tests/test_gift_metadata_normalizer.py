import unittest

from gift_metadata_normalizer import normalize_candidate, normalize_candidates


class NormalizeGiftCandidateTests(unittest.TestCase):
    def test_normalizes_nested_vendor_price_and_relative_url(self) -> None:
        candidate = {
            "product": {
                "title": "  Ember   Mug 2  ",
                "url": "/products/ember-mug-2#details",
            },
            "offer": {"price": "US$129.95"},
            "merchant": {"name": "  Ember  "},
            "taxonomy": {"category": "Desk Accessories"},
            "stock": {"status": "Ready to ship"},
        }

        normalized = normalize_candidate(candidate, base_url="https://example.com")

        self.assertEqual(normalized.title, "Ember Mug 2")
        self.assertEqual(normalized.price, 129.95)
        self.assertEqual(normalized.currency, "USD")
        self.assertEqual(normalized.vendor, "Ember")
        self.assertEqual(normalized.category, "Desk Accessories")
        self.assertEqual(normalized.availability, "in_stock")
        self.assertEqual(
            normalized.destination_url,
            "https://example.com/products/ember-mug-2",
        )

    def test_parses_european_number_format_and_currency_code(self) -> None:
        candidate = {
            "name": "Noise-Cancelling Headphones",
            "pricing": {"amount": "EUR 1.234,50"},
            "availability": "In Stock",
        }

        normalized = normalize_candidate(candidate)

        self.assertEqual(normalized.price, 1234.5)
        self.assertEqual(normalized.currency, "EUR")
        self.assertEqual(normalized.availability, "in_stock")

    def test_normalizes_boolean_and_text_availability(self) -> None:
        self.assertEqual(
            normalize_candidate({"title": "Gift", "in_stock": True}).availability,
            "in_stock",
        )
        self.assertEqual(
            normalize_candidate({"title": "Gift", "availability": "Sold out"}).availability,
            "out_of_stock",
        )
        self.assertEqual(
            normalize_candidate({"title": "Gift", "stock": "Only 3 left"}).availability,
            "limited",
        )
        self.assertEqual(
            normalize_candidate({"title": "Gift", "availability": "Backorder now"}).availability,
            "preorder",
        )

    def test_handles_missing_or_invalid_metadata(self) -> None:
        candidate = {
            "title": "Gift Card",
            "price": "Contact us",
            "vendor": "",
            "category": None,
            "link": "not_a_url",
        }
        normalized = normalize_candidate(candidate)

        self.assertEqual(normalized.title, "Gift Card")
        self.assertIsNone(normalized.price)
        self.assertIsNone(normalized.currency)
        self.assertIsNone(normalized.vendor)
        self.assertIsNone(normalized.category)
        self.assertEqual(normalized.availability, "unknown")
        self.assertIsNone(normalized.destination_url)

    def test_batch_normalization(self) -> None:
        candidates = [
            {"title": "A", "price": 10, "link": "https://example.com/a"},
            {"name": "B", "price": "$20.00", "availability": False},
        ]
        normalized = normalize_candidates(candidates)

        self.assertEqual(len(normalized), 2)
        self.assertEqual(normalized[0].title, "A")
        self.assertEqual(normalized[0].price, 10.0)
        self.assertEqual(normalized[1].title, "B")
        self.assertEqual(normalized[1].currency, "USD")
        self.assertEqual(normalized[1].availability, "out_of_stock")


if __name__ == "__main__":
    unittest.main()
