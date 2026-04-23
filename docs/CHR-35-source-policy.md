# CHR-35: Approved and Excluded Gift Sources

This decision document defines the default source policy for recommendation generation in the Corporate Gift Recommendation Chatbot.

Canonical config: `config/gift_source_policy.json`

## Decision summary

Recommendations should prioritize:

1. Direct vendor product pages and corporate gifting program pages from vetted domains
2. Vendor collection/category pages that still contain pricing and shipping details
3. Trusted marketplace listings only when seller quality thresholds are met
4. Editorial guides only as discovery/research input, not as final purchase links

Recommendations must exclude:

- Coupon/cashback portals
- Link-farm and SEO-content-farm pages
- Forum/social-only suggestions without reliable product metadata
- Low-trust cross-border marketplaces that create high fulfillment and quality variance

## Approved source type priority

| Priority | Source type | How it is used |
| --- | --- | --- |
| 1 | `vendor_product_page` | Preferred candidate for final recommendation |
| 2 | `vendor_category_collection_page` | Good fallback when direct SKU pages are sparse |
| 3 | `vendor_gifting_program_page` | Useful for B2B/group gifting constraints |
| 4 | `trusted_marketplace_listing` | Allowed with seller/review/shipping gates |
| 5 | `reputable_editorial_gift_guide` | Research only; should map to a vendor page before final output |

## Approved vendor domain tiers

### Priority 1: Direct corporate gifting vendors

- `loopandtie.com`
- `sugarwish.com`
- `snackmagic.com`
- `giftsforgood.com`
- `corporategift.com`
- `sendoso.com`
- `goody.com`
- `packedwithpurpose.gifts`

### Priority 2: Reliable general gift vendors

- `1-800-flowers.com`
- `harryanddavid.com`
- `uncommongoods.com`
- `oliveandcocoa.com`
- `gourmetgiftbaskets.com`
- `giftbasket.com`
- `worldmarket.com`
- `etsy.com` (conditional quality checks apply)

### Priority 3: Editorial discovery domains (research-only)

- `nytimes.com`
- `wirecutter.com`
- `forbes.com`
- `foodandwine.com`
- `goodhousekeeping.com`

## Excluded source types and domains

### Source types

- `coupon_aggregator`
- `cashback_portal`
- `user_generated_forum_post`
- `social_media_post`
- `video_only_recommendation`
- `expired_deal_page`
- `pdf_catalog_without_checkout`
- `affiliate_link_farm`
- `seo_content_farm`

### Domains

- `temu.com`
- `aliexpress.com`
- `wish.com`
- `dhgate.com`
- `craigslist.org`
- `facebook.com/marketplace`

## Conditional domain handling

Some domains are high-coverage but variable-quality, so they are conditionally allowed:

- `amazon.com`: seller rating >= 4.5, review count >= 100, verified shipping availability
- `etsy.com`: shop rating >= 4.7, review count >= 200, processing time <= 5 days

## Hard filters

Candidates are rejected if any of these fail:

- Price is missing
- Destination shipping is unsupported
- Item is out of stock
- Item is age-restricted/inappropriate for workplace gifting

## Notes for future iteration

- Admin-configurable allow/deny lists can layer on top of this default policy.
- Regional variants of approved domains may be added once geography-specific shipping SLAs are modeled.
