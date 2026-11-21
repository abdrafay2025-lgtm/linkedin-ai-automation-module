# AI & Automation Module

**Developer:** Abdul Raffay — AI & Automation Developer  
**Module Scope:** AI Intelligence, Search Query Generation, and Message Personalization Layer.

This module provides the core AI intelligence and deterministic preprocessing layer for the LinkedIn messaging workflow. It executes keyword sanitization, AI-assisted search query generation, verified profile interpretation, personalization, and anti-hallucination message validation.

---

## Architecture Principles

1. **Deterministic Operations Stay Deterministic**: Formatting, deduplication, schema validation, and placeholder checks never touch an LLM.
2. **AI Where Value is Real**: LLMs (Google Gemini) are strictly used for natural language intent interpretation, contextual personalization, and linguistic validation.
3. **Zero Hallucination Tolerance**: Personalization strictly uses verified input data. Missing fields remain omitted.
4. **Decoupled Contracts**: Outputs are typed Pydantic models designed for seamless downstream consumption by backend dispatchers.

---

## Project Structure

```text
ai-automation-module/
├── app/
│   ├── config/
│   │   └── settings.py
│   ├── models/
│   │   └── search_models.py
│   ├── services/
│   │   └── keyword_normalizer.py
│   ├── validators/
│   │   └── query_validator.py
│   └── utils/
│       └── logging_config.py
├── tests/
│   └── test_keyword_normalization.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md