# System Design & Data Schemas

This document provides a deep dive into the database models, relationships, caching topologies, and state storage mechanisms of **SupportGPT Enterprise**.

---

## 🗄️ Relational Database Schema (PostgreSQL)

We utilize **SQLAlchemy** (async) to define and interact with the database tables.

```mermaid
erDiagram
    users ||--o{ response_approvals : "approves/edits"
    tickets ||--o{ response_approvals : "requires validation"
    
    users {
        int id PK
        string username UNIQUE
        string hashed_password
        string role "admin | manager | agent"
        datetime created_at
    }

    tickets {
        int id PK
        string customer_id FK
        string subject
        text description
        string status "open | in_progress | resolved"
        string priority "low | medium | high | urgent"
        string sentiment "positive | neutral | negative"
        string department "billing | technical | shipping"
        float sla_hours
        datetime created_at
        datetime updated_at
    }

    session_memories {
        string session_id PK
        string customer_id
        json conversation_history "[{role, content}]"
        datetime updated_at
    }

    knowledge_docs {
        string id PK
        string title
        text content
        string version "v1 | v2"
        string category
        json metadata_json
        datetime created_at
    }

    response_approvals {
        int id PK
        int ticket_id FK
        text drafted_response
        text modified_response
        string status "pending | approved | modified | rejected"
        int agent_id FK
        float latency_seconds
        datetime created_at
    }
```

---

## ⚡ Caching and Session Management (Redis)

Redis is deployed as an active cache to store:
1. **User JWT Sessions**: Reduces database query overhead on active API requests by caching authenticated payloads.
2. **LLM Context Cache**: Caches identical ticket summaries and sentiment requests to minimize LLM billing costs.
3. **Active Chat History**: Active chats are serialized and saved to Redis under `session:<session_id>` with a 1-hour expiration time (TTL) for performance, and periodically synchronized back to PostgreSQL for permanent storage.

---

## 🏷️ Vector Store Topology (ChromaDB)

- **Vector space**: Cosine similarity.
- **Dimensionality**: 1536 (matching OpenAI `text-embedding-3-small` dimensions).
- **Chunking parameters**: 600 character size with 120 character overlap, recursively split by paragraph boundaries.
- **Partitioning / Namespace**: Documents are indexed with metadata tag `version: v1`, `version: v2`, or `version: v3`. Semantic query vectors are executed against filters ensuring isolation between active document versions:
  ```python
  where_filter = {"version": requested_kb_version}
  ```
