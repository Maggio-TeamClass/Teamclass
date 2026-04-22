# CHR-48 — Pilot Run and Launch Readiness Gap Report

## Context

Issue CHR-48 requests a pilot run of the Corporate Gift Recommendation Chatbot MVP, with findings and launch blockers.

## Pilot status

Pilot execution is **blocked**. No deployable MVP application, test harness, or runnable service was found in the repository at the time of analysis.

Observed repository state:

- Repository contains only a bootstrap shell script (`main`) with git setup commands.
- No source code for chatbot intake, search, ranking, shortlist UI/API, or safeguards.
- No environment configuration, package manifests, tests, or run instructions.
- External thread evidence reports:
  - `Failed to fetch branch/tag ref main ... Git Repository is empty`

Because the MVP artifact is missing, no end-user pilot could be executed in this environment.

## Findings summary

### What was validated

- The project intent and MVP definition are clear in the PRD (individual/group gifting flow, criteria extraction, search, ranking, rationale).
- The issue and external error trail identify a concrete operational blocker: repository initialization/content availability.

### What could not be validated

- Recommendation quality and ranking relevance.
- Criteria parsing correctness (budget, role, age, interests, occasion, quantity, region).
- Safety guardrails for inappropriate/low-confidence outputs.
- Performance metrics (time to first recommendation, click/save rate, refinement rate).
- Reliability, observability, and deployment readiness.

## Launch readiness assessment

Current readiness: **NOT READY**

### Critical blockers (must fix before pilot, therefore before launch)

1. **No MVP codebase available**
   - There is no implementation to run against pilot users.
2. **Repository/bootstrap failure**
   - External errors indicate empty remote or missing `main` ref content.
3. **No execution or deployment path**
   - Missing runtime config, startup scripts, and environment documentation.
4. **No test/QA coverage**
   - No automated or manual validation artifacts.
5. **No telemetry instrumentation**
   - Cannot collect success metrics defined in PRD.

## Recommended follow-up work

## Phase 0: unblock pilot infrastructure

- Initialize and push a non-empty repository baseline.
- Add project scaffold (backend/service + optional frontend) with README setup instructions.
- Define `.env.example` and required secrets/keys for web search and LLM providers.
- Add minimal CI checks (lint/test/build) to verify baseline health.

## Phase 1: MVP implementation readiness

- Implement conversational intake flow for required criteria.
- Implement candidate search across approved web sources.
- Implement scoring/ranking model with transparent rationale fields.
- Add confidence scoring and low-confidence fallback messaging.
- Implement shortlist response format: price, vendor, reason, URL, tradeoffs.

## Phase 2: pilot operations readiness

- Add event tracking for PRD metrics:
  - session start
  - first useful recommendation timestamp
  - recommendation click/save
  - refinement count
  - no-result / low-confidence outcomes
- Create pilot runbook:
  - participant profile
  - scenarios and prompts
  - acceptance criteria
  - issue triage process
- Prepare safe source allowlist / denylist and content moderation checks.

## Proposed pilot test matrix (once MVP exists)

### Core scenarios

1. **Individual gift, strict budget**
2. **Group gift, quantity and regional constraints**
3. **Sparse user input requiring clarification**
4. **No suitable results / low-confidence fallback**
5. **Brand-safety filtering edge case**

### Per-scenario pass criteria

- At least 3 relevant recommendations returned (or explicit low-confidence fallback).
- Price and vendor links are present and valid.
- Explanation references user criteria directly.
- Response time acceptable for conversational flow.

## Exit criteria for launch go/no-go

Before launch consideration, require:

- Pilot completed with representative users and documented outcomes.
- No open P0/P1 defects in recommendation correctness/safety.
- Metric baselines captured for all PRD success metrics.
- Source quality and vendor policy decisions documented.
- Runbook and on-call ownership in place for early launch period.

## Suggested Linear comment (ready to post)

> Pilot is currently blocked because the repository has no deployable MVP artifacts (code/config/tests) and external errors indicate an empty remote/main ref. I could not execute user pilot scenarios in the current state.  
>  
> **Launch readiness: NOT READY.**  
> **Primary blockers:** missing MVP implementation, missing repo/bootstrap integrity, no QA pipeline, and no telemetry for success metrics.  
>  
> I added a detailed readiness gap report with phased follow-up actions and a proposed pilot test matrix in `PILOT_LAUNCH_READINESS_CHR-48.md`.  
>  
> Once the MVP scaffold is available, we can run a structured pilot and produce quantified findings for go/no-go.
