# CHR-34: Target Users and Priority Gifting Scenarios (MVP)

## Purpose

Define the highest-priority buyer segments and gifting scenarios the MVP must support first so product, engineering, and evaluation all align on the same target behavior.

## Scope

- In scope: segmentation and scenario prioritization for recommendation quality in the chatbot MVP.
- Out of scope: procurement workflows, payment, inventory integrations, and non-corporate gifting use cases.

---

## 1) Priority Buyer Segments

Prioritization is based on:

1. Frequency of gifting requests
2. Need for both individual and group recommendations
3. Time pressure and need for fast shortlist generation
4. Clear measurable constraints (budget, quantity, occasion, shipping)

### Segment A (P0): Executive Assistants (EA) and Office Managers

**Why prioritized**
- Handle high-visibility gifting for executives and external stakeholders.
- Frequently need both one-off premium gifts and scaled group gifts.
- Strong requirement for polished rationale and low-risk recommendations.

**Typical constraints**
- Tight deadlines
- Premium but capped budgets
- Preference for reliable vendors and presentation quality
- Geographic shipping constraints for remote recipients

**MVP support expectation**
- Excellent quality for both individual and small-to-medium group gifting scenarios.

---

### Segment B (P0): People Ops / Employee Experience

**Why prioritized**
- Own recurring employee moments (onboarding, work anniversaries, holidays).
- High volume and repeatable scenario patterns make this ideal for MVP learning loops.
- Need practical, scalable options that still feel personalized.

**Typical constraints**
- Per-person budget caps
- Group quantity and shipping-to-multiple-addresses considerations
- Inclusion and appropriateness across diverse teams
- Region-specific availability

**MVP support expectation**
- Excellent quality for group gifting with configurable quantity, budget, and region.

---

### Segment C (P1): Recruiting Teams

**Why prioritized**
- Clear, frequent use case (candidate appreciation / welcome kits) with moderate complexity.
- Valuable for expanding beyond internal employee events once P0 quality is stable.

**Typical constraints**
- Brand-safe and professional gift categories
- Mid-range budgets
- Fast shipping timing around interview/hiring milestones

**MVP support expectation**
- Strong individual recommendations and curated group options for small cohorts.

---

### Segment D (P1): Sales and Customer Success

**Why prioritized**
- Strategic revenue-aligned gifting (thank-you, renewal milestones, events).
- High upside but higher policy complexity and varied compliance needs by company.

**Typical constraints**
- Account tier-based budgets
- Occasion sensitivity
- Regional gifting norms
- Potential category restrictions

**MVP support expectation**
- Supported after P0 stabilization; focus on configurable constraints and rationale quality.

---

### Segment E (P2): People Managers

**Why prioritized**
- Important long tail, but typically lower volume and less formal process.
- Better served after core flows are proven with professional buyers.

**Typical constraints**
- Small team budgets
- Preference for easy, practical choices

**MVP support expectation**
- Opportunistic coverage via same flows, not a primary optimization target in MVP.

---

## 2) MVP Scenario Priority Matrix

### Prioritization framework

Scenarios are ranked by combined score of:

- **Frequency**: how often requests occur
- **Business impact**: visibility, recipient importance, and buyer pain
- **Complexity fit**: whether MVP can satisfy constraints with current scope

### Priority definitions

- **P0**: Must work well at launch. Critical path for product value.
- **P1**: Should be supported shortly after launch once P0 reliability is strong.
- **P2**: Nice-to-have / long-tail for later iteration.

---

## 3) Priority Individual Gifting Scenarios

### I-1 (P0): Executive or VIP thank-you gift

**Primary users**: EA, Office Manager, Sales/CS  
**Core inputs**: role/seniority, budget range, occasion, interests, region, shipping timeline  
**Success criteria**:
- Returns 3-5 high-confidence options inside budget
- Every option includes rationale tied to role/occasion/interests
- Includes premium-feel options and practical fallback choices

---

### I-2 (P0): Employee milestone recognition (birthday/anniversary/promotion)

**Primary users**: People Ops, Managers  
**Core inputs**: recipient profile (role/age band/interests), budget, occasion, location  
**Success criteria**:
- Personalized but workplace-appropriate options
- No obvious mismatches with stated interests or budget
- Clear tradeoffs (premium vs practical, fast shipping vs best fit)

---

### I-3 (P1): Candidate/new hire welcome gift

**Primary users**: Recruiting, People Ops  
**Core inputs**: role level, brand-safe preference, budget, region, timing  
**Success criteria**:
- Professional, neutral, and onboarding-friendly options
- Region-appropriate availability and shipping signal included

---

### I-4 (P1): Client appreciation gift for account milestone

**Primary users**: Sales/CS  
**Core inputs**: account tier, occasion, budget, recipient role, region  
**Success criteria**:
- Tier-appropriate recommendations
- Rationale reflects business context (relationship-building, premium tone)

---

## 4) Priority Group Gifting Scenarios

### G-1 (P0): Team holiday gifting (10-200 recipients)

**Primary users**: People Ops, EA  
**Core inputs**: per-person budget, quantity, region(s), occasion, interests (optional)  
**Success criteria**:
- Recommends options that scale by quantity and budget
- Flags where personalization is low vs medium vs high
- Provides shortlist with clear per-unit pricing and total cost estimate

---

### G-2 (P0): Onboarding cohort kits (5-50 recipients)

**Primary users**: People Ops, Recruiting  
**Core inputs**: quantity, budget, recipient role band, region, shipping constraints  
**Success criteria**:
- Cohort-consistent recommendations suitable for professional onboarding
- Highlights practical shipping/reliability tradeoffs for multi-recipient sends

---

### G-3 (P1): Event or offsite attendee gifts

**Primary users**: EA, Office Manager, People Ops  
**Core inputs**: event type, quantity, budget, destination, timeline  
**Success criteria**:
- Recommendations optimized for portability and event appropriateness
- Includes options with realistic lead times

---

### G-4 (P1): Department recognition gifts (small internal teams)

**Primary users**: Managers, People Ops  
**Core inputs**: team size, per-person budget, occasion, broad preferences  
**Success criteria**:
- Balanced shortlist between universal-appeal and semi-personalized options

---

## 5) MVP Acceptance Coverage (What “done” means for CHR-34)

To consider this issue satisfied in product scope terms, MVP planning and implementation should explicitly target:

1. **Segments in focus**: Segment A and B as launch-critical (P0), with C/D as near-term extensions (P1).
2. **Scenario coverage**:
   - Individual P0: I-1, I-2
   - Group P0: G-1, G-2
3. **Intake fields must map to scenarios**:
   - budget (range/per-person), role/seniority, interests, age band (optional), occasion, quantity, region, shipping timing
4. **Recommendation output requirements**:
   - ranked shortlist, budget fit, rationale per option, vendor link, and tradeoff notes
5. **Guardrails**:
   - avoid clearly inappropriate categories for workplace context
   - surface low-confidence conditions when criteria conflict or data is incomplete

---

## 6) Suggested Instrumentation Tags (for evaluation)

To evaluate scenario performance after launch, tag sessions by:

- `segment`: EA_office_manager | people_ops | recruiting | sales_cs | manager
- `scenario_type`: individual | group
- `scenario_id`: I-1 | I-2 | I-3 | I-4 | G-1 | G-2 | G-3 | G-4
- `confidence_level`: high | medium | low
- `outcome`: clicked_link | saved | refined_query | no_result

This enables a direct read on whether the MVP is solving the highest-priority workflows first.
