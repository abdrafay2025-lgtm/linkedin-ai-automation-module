# AI & Automation Layer Architecture Specification

**Author:** Abdul Raffay  
**Role:** AI & Automation Developer  
**Module:** AI Intelligence, Search Generation & Outreach Personalization  

---

## 1. Executive Summary

This module provides the core artificial intelligence and deterministic sanitization services for an 8-week automated LinkedIn outreach workflow.

It is strictly decoupled from:
- Frontend/dashboard state.
- Backend dispatch, rate-limiting, and document ingestion.
- Direct LinkedIn platform scraping or unauthorized automation.

The module interfaces with other services purely via strongly-typed Pydantic contracts and FastAPI HTTP endpoints.

---

## 2. Architectural Philosophy: Deterministic vs. Probabilistic

- DETERMINISTIC LAYER: Whitespace collapsing, token deduplication, stop-connector filtering, connection degree authorization, and placeholder detection are handled by pure Python 3.11 logic without LLM cost or latency.
- PROBABILISTIC (LLM) LAYER: Search intent parsing, contextual outreach tailoring, and tone alignment use Google Gemini with strict system instructions.

---

## 3. The Two Primary Pipelines

### Pipeline 1: Search Query Intelligence
User Keywords -> KeywordNormalizer -> QueryValidator -> AISearchQueryGenerator (Gemini 1.5 Pro, Temp: 0.1) -> AISearchQueryOutput (Typed JSON Schema)

### Pipeline 2: Grounded Personalization & Message Safety
Approved Form Letter + Verified Profile Data -> ProfileInterpreter (Zero-inference) -> PersonalizationEngine (Gemini / Deterministic fallback) -> HallucinationValidator (PASS / REVIEW / FAIL gate) -> PersonalizationResponse

---

## 4. Zero-Hallucination Guarantees

1. Explicit Data Boundary: The model is strictly instructed and evaluated to reference only first_name and headline.
2. Missing Field Invariance: If a profile omits company, education, or achievements, these fields remain None. The inference of past history is strictly prohibited.
3. Auditing Gate: If heuristic triggers (e.g., "noticed your recent post", "congratulations on your new role") are detected when unverified, the message is automatically downgraded to status: REVIEW.