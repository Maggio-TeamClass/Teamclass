# Gift Request Criteria Schema (CHR-37)

This document defines the normalized input contract for gift recommendation requests.

## Schema location

- `schemas/gift-request-criteria.schema.json`

## Supported request types

- `recipient`: single-person gifting flow
- `group`: multi-recipient gifting flow

The top-level request carries a shared `criteria` object used by both flows. Each request type then adds one profile object:

- `recipient` requires `recipient` profile and forbids `group`
- `group` requires `group` profile and forbids `recipient`

## Required normalized criteria fields

All requests must include:

- `budget`
- `role`
- `ageRange`
- `interests`
- `occasion`
- `quantity`
- `region`

### Field notes

- `budget.currency` uses ISO-4217 uppercase 3-letter codes (for example `USD`, `EUR`)
- `region.countryCodes` uses ISO-3166-1 alpha-2 uppercase 2-letter codes (for example `US`, `GB`)
- `quantity.count` is explicit and can represent either a single recipient (`1`) or many recipients
- `budget.budgetScope` distinguishes budget interpretation:
  - `per_recipient`
  - `total`

## Recipient profile

`recipient` includes:

- `displayName` (required)
- optional metadata: `department`, `relationship`

## Group profile

`group` includes:

- `name` (required)
- `recipientCount` (required, minimum `2`)
- optional `segments` for internal cohort breakdowns with optional role and age refinements

## Example payloads

- `examples/recipient-gift-request.example.json`
- `examples/group-gift-request.example.json`

## Versioning

The schema currently pins `schemaVersion` to `"1.0"` for strict normalization in MVP. Future compatible updates should either:

1. keep `"1.0"` and only add optional fields, or
2. publish `"1.1"`/`"2.0"` with corresponding migration guidance.
