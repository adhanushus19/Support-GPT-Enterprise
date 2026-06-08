# Security & Safety Manual

This document details the security implementations, data privacy protocols, and input/output guardrails built into **SupportGPT Enterprise**.

---

## 🔑 Authentication and RBAC

We protect API resources using **JWT Bearer tokens** signed with `HS256`.

### Role-Based Access Control (RBAC)
We enforce role limits at the route dependency layer:
- **Agent (`agent`)**: Can view tickets, request chat replies, and approve AI-generated response cards.
- **Manager (`manager`)**: Can view agent latency metrics, roll back knowledge base versions, and process billing escalations.
- **Admin (`admin`)**: Has full access to delete collections, write new system prompts, and register new support staff users.

```python
# FastAPI Route Protection Example
@app.get("/approvals/pending")
async def list_pending_approvals(current_user: User = Depends(require_agent)):
    ...
```

---

## 🛡️ AI Guardrails & Safety Layer

To defend against malicious actors and secure customer privacy, all text payloads pass through input/output filters (`src/guardrails/`):

### 1. PII Anonymization (`pii_detection.py`)
- Matches Social Security Numbers (SSNs), Credit Cards (Visa/Mastercard), phone numbers, and email patterns using precompiled regular expressions.
- Replaces matches with anonymized tags (e.g. `[CREDIT_CARD]`, `[EMAIL]`) before text is sent to LLM providers.

### 2. Prompt Injection Protection (`prompt_injection.py`)
- Scans input descriptions for instruction hijack prompts (e.g. "ignore previous instructions", "override rules").
- Blocks threat payloads immediately, bypassing LLM compilation and routing the ticket to high-priority escalation queues.

### 3. Jailbreak Detection (`jailbreak_detection.py`)
- Blocks common sandbox escape models (such as "DAN mode" or "sudo override" commands).

### 4. Output Response Leak Filter (`response_filter.py`)
- Evaluates LLM responses before they are returned to client browsers.
- If the response leaks system prompts or references internal graph nodes, the filter replaces it with a safe fallback response.
