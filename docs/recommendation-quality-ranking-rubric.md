# CHR-36: Recommendation Quality and Ranking Rubric

This document defines how gift recommendations are filtered, scored, ranked, and labeled with confidence for the Corporate Gift Recommendation Chatbot.

## 1) Goals

- Rank candidate gifts by how well they satisfy stated user criteria.
- Balance relevance ("fit") with value for money and reliability of evidence.
- Suppress or down-rank low-confidence and low-safety options.
- Produce explainable outputs so users can understand why items are ranked.

## 2) Inputs to Scoring

Each candidate recommendation should be normalized into a common schema:

- `price_amount`, `price_currency`, `price_type` (unit, pack, subscription)
- `vendor`, `product_name`, `product_url`
- `category`, `tags`, `description`
- `availability_region`, `shipping_regions`, `lead_time_days` (if available)
- `ratings` (review count + average when available)
- `source_quality` (trusted vendor, marketplace, blog/listicle, unknown)
- `last_seen_at`

Each user request should be normalized into:

- `budget_min`, `budget_max` (or point budget)
- `recipient_type` (`individual` or `group`)
- `quantity` (for group)
- `role`, `age_range`, `interests`, `occasion`, `region`
- optional excludes (`disallowed_categories`, dietary/religious/brand constraints)

## 3) Hard Eligibility Filters (must pass)

Candidates are excluded before ranking if any condition is true:

1. **Broken or invalid destination**: no working product URL.
2. **Unsafe or inappropriate content**: violates policy or stated constraints.
3. **Price cannot be inferred** and no equivalent trusted source can confirm pricing.
4. **Region impossible**: cannot ship/sell to requested region (when region provided).
5. **Budget miss beyond tolerance**:
   - Individual: price > `budget_max * 1.20`
   - Group: total estimated cost > `group_budget_max * 1.10` (or per-person equivalent)

Notes:
- Items slightly over budget but within tolerance remain eligible and get penalized in scoring.
- If strict budget mode is introduced later, tolerance should become 0%.

## 4) Weighted Quality Score (0-100)

Final ranking score:

`final_score = fit_score * 0.45 + price_quality_score * 0.25 + confidence_score * 0.20 + logistics_score * 0.10`

### 4.1 Fit Score (0-100, weight 45%)

How well the item matches request intent and recipient profile.

Subcomponents:

- Criteria relevance (role, interests, occasion): 40%
- Recipient appropriateness (age/culture/professional context): 25%
- Use-case suitability (individual vs group scaling): 20%
- Constraint compatibility (exclusions, special constraints): 15%

Scoring guidance:
- 90-100: direct and specific match across most criteria.
- 70-89: strong match with minor mismatch.
- 50-69: partial match; generic gift for the scenario.
- <50: weak relevance.

### 4.2 Price Quality Score (0-100, weight 25%)

Measures value relative to budget and quality signals.

Subcomponents:

- Budget alignment (distance from target range): 50%
- Product quality signals (ratings/reputation/warranty): 30%
- Value indicators (features per dollar, bundle utility): 20%

Budget alignment rules:
- Inside range: 80-100 depending on proximity to midpoint or target.
- Up to tolerance over max: 40-79 (scaled penalty).
- Under budget by large margin with weak quality: cap at 70 to avoid "cheapest wins."

### 4.3 Confidence Score (0-100, weight 20%)

How reliable the recommendation evidence is.

Subcomponents:

- Data completeness (price, availability, description, vendor identity): 35%
- Source trust level: 30%
- Freshness (`last_seen_at` recency): 20%
- Cross-source corroboration (same item/details seen in multiple trusted places): 15%

Suggested source trust defaults:
- Brand/vendor official site: 95
- Major trusted marketplace with strong listing data: 80
- Curated gift retailer with complete listing: 75
- Editorial/listicle only (no direct listing): 45
- Unknown/low-signal source: 30

### 4.4 Logistics Score (0-100, weight 10%)

Operational feasibility, especially for group gifting.

Subcomponents:

- Shipping feasibility to region: 40%
- Lead time vs occasion urgency: 35%
- Quantity scalability / bulk ordering support: 25%

For individual gifting with no timeline constraints, default logistics baseline is 70 if unknown.

## 5) Confidence Bands and Display Rules

After computing `final_score`, assign confidence band:

- **High confidence**: `final_score >= 80` and `confidence_score >= 70`
- **Medium confidence**: `65 <= final_score < 80` and `confidence_score >= 55`
- **Low confidence**: below medium thresholds

Display behavior:

1. Show high + medium confidence results by default.
2. Hide low-confidence results unless fewer than 3 medium/high recommendations exist.
3. If low-confidence items are shown, label clearly with missing data reasons.
4. If all candidates are low confidence, return "needs refinement" guidance and request clarifying constraints.

## 6) Ranking and Tie-Breaking

Primary sort: `final_score` descending.

Tie-breakers (in order):

1. Higher `fit_score`
2. Higher `confidence_score`
3. Better budget alignment (closer to budget target without exceeding)
4. Better logistics score (when region/occasion constraints exist)
5. Diversity rule: prefer not to repeat same vendor/category when alternatives are near-equal (within 2 points)

## 7) Group vs Individual Adjustments

When `recipient_type = group`:

- Increase logistics importance by +5 and reduce fit by -5 in effective weighting.
- Require total-cost feasibility check at requested quantity.
- Add bonus (+0 to +8) for gifts with clear bulk fulfillment and per-recipient consistency.

When `recipient_type = individual`:

- Keep default weights.
- Increase personalization signals (role/interests/occasion) in fit subscore.

## 8) Missing Data Handling

- Missing non-critical fields (e.g., rating count) reduce confidence but do not auto-exclude.
- Missing critical fields (price, vendor identity, or region feasibility when region specified) should trigger exclusion or severe confidence penalties per Section 3.
- Any inferred value must be labeled as inferred and included in rationale.

## 9) Output Contract (for each recommended item)

Each returned recommendation should include:

- `rank`
- `final_score`
- `confidence_band` (`high`, `medium`, `low`)
- component scores: `fit_score`, `price_quality_score`, `confidence_score`, `logistics_score`
- `why_it_fits` (2-4 bullets mapped to user criteria)
- `tradeoffs` (1-3 bullets, especially for budget/logistics uncertainty)
- `price_summary` (unit and total where relevant)
- `vendor`, `link`, and any key caveats

## 10) Acceptance Checks for Implementation

1. Out-of-budget and non-shippable candidates are consistently filtered by policy.
2. Ranking is deterministic for same inputs.
3. Top recommendations are not dominated by ultra-cheap but poor-fit items.
4. Confidence labels match evidence completeness and source trust.
5. Group queries prefer options that can scale operationally.
6. Every displayed recommendation has an explainable rationale and explicit tradeoffs.
