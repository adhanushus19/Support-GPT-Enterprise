# Phase 4: Technology Decisions

## 🎯 Goals
Analyze technical requirements and select frameworks:
- Pluggable LLM design to support Azure and OpenAI.
- Local Ephemeral vector database configuration to support zero-credential unit testing runs.

---

## ⚙️ Design Decisions
- **Pluggable LLM Provider**: Defined a clean interface (`BaseLLMProvider`). This enables mock modes, saving API costs during testing.
- **SQLite + Asyncpg**: Using `aiosqlite` for tests/local SQLite configurations, and `asyncpg` for PostgreSQL in production.

---

## 💻 Code Walkthrough Reference
- Pluggable provider overrides are handled in [provider.py](file:///C:/Users/adhan/.gemini/antigravity/scratch/supportgpt-enterprise/src/llm/provider.py).
- SQLite/PostgreSQL engine creation is defined in [database.py](file:///C:/Users/adhan/.gemini/antigravity/scratch/supportgpt-enterprise/src/database.py).

---

## 🧪 Validation Steps
1. Run `pytest` to verify mock LLM providers successfully intercept model outputs.
