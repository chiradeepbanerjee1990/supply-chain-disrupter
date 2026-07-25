# Native Guardrails Design Spec

**Date:** 2026-07-23
**Status:** Approved
**Author:** Claude + User collaboration

## Overview

Implement the guardrail inventory described in `docs/specs/Guardrails_Complete_Reference_CapstoneP8.docx` (16 guardrails: 6 input, 8 output, 2 resource/execution) as native Python — no third-party guardrails SDK (NeMo Guardrails, Guardrails AI, etc.) — plus 3 supplemental checks pulled in from the earlier `docs/specs/2026-07-08-trulens-guardrails-design.md` spec that this replaces for guardrails purposes (`l3_hub_coverage`, `l4_label_score_alignment`, `l4_ensemble_coherence`).

This spec supersedes `2026-07-08-trulens-guardrails-design.md`'s architecture: that spec logged violations into TruLens's own SQLite (`data/trulens/trulens.db`), visible only in the standalone TruLens dashboard. This spec logs into one `guardrail_events` table in the main project database (`outputs/supply_chain.db`), visible on the React UI's existing "Observability & Guardrails" screen — avoiding a split source of truth between two dashboards. TruLens Phase 1 (tracing, cost/tokens, the `risk_score_stability`/`ensemble_agreement` trend metrics) is unaffected and stays as-is; it answers a different question ("is risk scoring drifting over time") than guardrails do ("did this run's output pass a hard check").

## Requirements

| Requirement | Detail |
|---|---|
| Enforcement mode | Soft — log violations, never halt the pipeline (matches the original TruLens spec's philosophy) |
| Coverage | All 7 agents (L1–L7), unlike the TruLens spec's L2/L3/L4-only scope |
| Storage | One `guardrail_events` table in `outputs/supply_chain.db`, sibling to `llm_call_log` |
| Dashboard | React UI's existing "Observability & Guardrails" screen (`src/api/routers/guardrails.py`, currently a fixture stub) |
| Dependencies | None new — `pydantic`, `tenacity`, `ragas` are all already project dependencies |

## Scope: 18 of 19 candidate checks

19 candidates were identified (16 from the docx + 3 from the TruLens spec). One is deferred; the rest ship in this pass.

### Deferred (not built this pass)

| Guardrail | Reason |
|---|---|
| Hard business-rule override (`slack_should_fire`) | `src/agents/mitigation_agent.py`'s actual Slack webhook call is a `pass` placeholder — nothing real exists yet to guard. Revisit once the webhook is implemented. |

### Dropped from scope entirely

`l2_category_valid` (one of the TruLens spec's original 8) is **not** one of the 3 supplemental checks folded in here — it was assessed as redundant in kind with output guardrail #11 (label-enum enforcement) applied to a different field, and it also carries a known bug (its pass-condition enum, `weather, geopolitical, logistics, demand, supplier, regulatory, other`, doesn't match the real `NewsAnalysisLLMOutput.category` field, which is `weather, geopolitical, logistics, raw_material, demand_shock`). Decision: skip it, not fix-and-build it.

### The 18 to implement

`guardrail_name` is the exact string logged in `guardrail_events.guardrail_name` — the canonical identifier for each check, not just a prose description.

| # | `guardrail_name` | Direction | Hook point | Notes |
|---|---|---|---|---|
| 1 | `ingest_schema_validation` | input | `src/utils/ingestion_validator.py`'s `DataValidator` (existing) | Add `log_guardrail_event()` at existing schema-stage failure points |
| 2 | `prompt_injection_screen` | input | `call_openai_structured()` | Keyword/pattern screen on `user_message` before the call |
| 3 | `input_token_cap` | input | `call_openai_structured()` | Check final message length before sending |
| 4 | `critical_field_null_gate` | input | `src/agents/risk_classifier_agent/agent.py` | Before the composite formula runs |
| 5 | `ingestion_circuit_breaker` | input | `DataIngestionAgent._is_circuit_open()` (existing) | Add `log_guardrail_event()` to existing trip logic |
| 6 | `parameterized_query_check` | input | **static test**, not runtime | See "Guardrail #6" below — a codebase-wide property, not a per-call event |
| 7 | `structured_output_schema` | output | `call_openai_structured()` (existing, via `response_format`) | Add `log_guardrail_event()` at the existing "no parsed result" `RuntimeError` path |
| 8 | `numeric_bounds_check` | output | `risk_classifier_agent/agent.py` | `composite_score`/confidence clipped to `[0,1]`, logged if clipped |
| 9 | `citation_groundedness` | output | L4/L7, reusing `evaluation/ragas/rag_tracer.py`'s retrieval/LLM-output correlation pattern | Compare `rag_citations` against actual chunk IDs returned by that call |
| 10 | `label_enum_enforcement` | output | `call_openai_structured()` (same path as #7) | Pydantic `Literal` already enforces this; log the violation at the same parse-failure hook |
| 11 | `locked_formula_tamper_check` | output | `risk_classifier_agent/agent.py` | Assert echoed `composite_score`/`final_label` in the LLM enhancement matches the true locked calculation |
| 12 | `fallback_on_failure` | output | Existing except blocks in L2, L3, L4 (judge + LLM signal), L7 | One `log_guardrail_event()` call added per existing catch block |
| 13 | `ragas_faithfulness_gate` | output | L4/L7, **only when `final_label == "CRITICAL"`** | Scoped to avoid adding LLM-judge cost/latency to every run |
| 14 | `llm_call_timeout_retry` | execution | `call_openai_structured()` | Extend the existing `tenacity` `@retry` (already retries `RateLimitError`) to also bound total call duration |
| 15 | `per_run_cost_breaker` | execution | `call_openai_structured()` | Query cumulative `llm_call_log.cost_usd` for this `run_id` before allowing the call through |
| 16 | `l3_hub_coverage` | output | `src/agents/weather_agent/agent.py` | Confirm `weather_signals` has a row for the active hub |
| 17 | `l4_label_score_alignment` | output | `risk_classifier_agent/agent.py` | LOW <0.3, MEDIUM 0.3–0.5, HIGH 0.5–0.7, CRITICAL >0.7 |
| 18 | `l4_ensemble_coherence` | output | `risk_classifier_agent/agent.py`, **reusing `feedback_functions.ensemble_agreement()`** | Call with a single-element list `[(rule, distilbert, llm)]`; `1.0` = pass, `0.0` = fail |

Note: `call_openai_structured()` is the hook point for 7 of the 18 (#2, #3, #7, #10, #14, #15, plus #9 partially) — the same centralization principle `observability.py` already uses for cost/token logging.

## Architecture

### `guardrail_events` table (new, `db_utils.py`)

```sql
CREATE TABLE IF NOT EXISTS guardrail_events (
    event_id     TEXT PRIMARY KEY,   -- UUID
    agent_name   TEXT NOT NULL,      -- e.g. L4_risk_classifier, L7_mitigation
    guardrail_name TEXT NOT NULL,    -- e.g. prompt_injection_screen, per_run_cost_breaker
    direction    TEXT NOT NULL,      -- input | output | execution
    passed       INTEGER NOT NULL,   -- 0 = blocked/clipped/routed to fallback
    reason       TEXT,               -- human-readable explanation, self-contained (no separate details column)
    record_id    TEXT,               -- FK to lite_master; nullable for ingest- or run-level events
    ts           TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_guardrail_events_agent ON guardrail_events(agent_name);
CREATE INDEX IF NOT EXISTS idx_guardrail_events_guardrail ON guardrail_events(guardrail_name);
```

`ensure_guardrail_events_table()` follows the existing lazy-create pattern (`ensure_risk_classification_table()`). `log_guardrail_event(...)` is the single writer every guardrail calls — unconditional, fail-open (a logging bug must never raise into the pipeline), matching `insert_llm_call_log()`'s contract.

### `src/utils/guardrails.py` (new)

Pure check functions, no DB/framework dependency — mirrors `feedback_functions.py`'s style. Each returns:

```python
@dataclass
class GuardrailResult:
    passed: bool
    guardrail_name: str
    reason: str
```

Callers (agent code, `call_openai_structured`, the ingestion validator) call the pure function, then call `log_guardrail_event()` with the result. This separation means every guardrail check is unit-testable without touching SQLite.

### Guardrail #6 (parameterized queries) — static test, not runtime

Logging "used bound params" as a `guardrail_events` row on every one of the thousands of real queries this app runs would be pure noise, not signal. Implemented instead as a pytest test that scans `src/utils/db_utils.py` for f-string/`.format()`-based SQL construction and fails if any is found — same guarantee (no SQL-injection surface), zero runtime cost, zero log spam.

### Dashboard

`src/api/routers/guardrails.py`'s current fixture-reading stub is replaced with a real `fetch_guardrail_events()` reader (new, `db_utils.py`), filterable by `direction`/`agent_name`, feeding the React "Observability & Guardrails" screen's existing Guardrail Activity table. The "Slack Alerts Suppressed by Guardrail" headline metric stays out of scope — it depends on the deferred hard-rule-override guardrail (#8 candidate, not built this pass).

## Testing

- **Unit tests** — one per guardrail's pure check function in `src/utils/guardrails.py`, covering valid/invalid/boundary cases (mirrors `test_trulens_feedback_functions.py`'s style: e.g. bounds accept `0.0`/`0.5`/`1.0`, reject `-0.1`/`1.5`/`None`).
- **Static test** — the parameterized-query scan (guardrail #6).
- **Integration tests** — one per hook-point group (e.g. `call_openai_structured`'s 7 guardrails, `risk_classifier_agent`'s 6), confirming a violation lands in `guardrail_events` without raising, and that a clean run logs `passed=1` rows.
- **Manual verification** — run a real scenario with an intentionally bad value (e.g. mock `composite_score=1.5`), confirm the violation appears via `/api/guardrails/events?direction=output`, and confirm the pipeline still completes.

## Out of Scope

- Hard enforcement (halting the pipeline on a guardrail failure) — soft enforcement only, matching the original TruLens spec's rationale (development/monitoring focus, not production-critical for a capstone)
- The deferred hard-rule Slack override (candidate #8) and its dependent "Slack Alerts Suppressed" headline metric
- `l2_category_valid` (dropped from scope — see above)
- Full PII redaction, toxicity classifiers, RAG corpus poisoning protection, inbound rate limiting, model-version pinning, Slack webhook idempotency — all explicitly deferred in the source docx's own Section 7, unchanged here
