# Agentic AI Architecture

This document details the multi-agent system design, StateGraph schema, and individual agent responsibilities implemented in **SupportGPT Enterprise**.

---

## 🧠 LangGraph State Orchestrator

We use **LangGraph** to construct a stateful multi-agent system. The `AgentState` dictionary serves as a shared memory canvas, modified sequentially by each agent node:

```python
class AgentState(TypedDict):
    ticket_id: int
    customer_id: str
    subject: str
    description: str
    kb_version: str
    sentiment: str
    priority: str
    intent: str
    department: str
    context_citations: List[Citation]
    suggested_response: str
    qa_score: float
    hallucination_detected: bool
    escalation_recommended: bool
    escalation_reason: Optional[str]
    tokens_input: int
    tokens_output: int
    cost_usd: float
    latency_seconds: float
    approval_required: bool
    errors: List[str]
```

---

## 👥 Node Agents and Responsibilities

### 1. Ticket Analysis Agent (`analyzer.py`)
- **Duty**: Scrub incoming customer queries for PII (phone, SSN, cards), inspect for prompt injection/jailbreaks, and analyze tone.
- **Output variables**: `sentiment` (positive, neutral, negative), `priority` (low, medium, high, urgent), `department` (billing, technical, general).

### 2. Knowledge Retrieval Agent (`retriever.py`)
- **Duty**: Pulls relevant policy articles and guidelines from ChromaDB.
- **Output variables**: `context_citations` (list of citations matching active `kb_version`).

### 3. Resolution Agent (`resolver.py`)
- **Duty**: Formulates a drafted email resolution response to the customer.
- **Output variables**: `suggested_response`.

### 4. Quality Assurance Agent (`quality_assurance.py`)
- **Duty**: Verifies that the drafted response is backed by retrieved citations and does not leak internal agent prompts.
- **Output variables**: `qa_score`, `hallucination_detected`.

### 5. Escalation Agent (`escalation.py`)
- **Duty**: Computes estimated SLA metrics and recommends human escalation for high-urgency cases or hallucinated drafts.
- **Output variables**: `escalation_recommended`, `escalation_reason`, `sla_hours`.
