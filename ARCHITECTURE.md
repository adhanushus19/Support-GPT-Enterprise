# Enterprise Architecture Blueprint

This document details the high-level system architecture, multi-agent coordination workflow, and request sequence loops for **SupportGPT Enterprise**.

---

## 🏗️ System Component Architecture

The platform follows a clean, decoupled design separating the client browser, API endpoint gateways, safety guardrails layer, agent states graph, databases, and third-party SaaS tools.

```mermaid
graph TD
    User([Support Agent / Customer]) -->|HTTP / JSON| API[FastAPI Gateway]
    
    subgraph Security Layer
        API -->|1. Sanitize| GR[Guardrails Engine]
        GR -->|PII Scrubbing| PII[pii_detection.py]
        GR -->|Injection Check| INJ[prompt_injection.py]
        GR -->|Jailbreak Block| JBL[jailbreak_detection.py]
    end
    
    subgraph Multi-Agent Graph (LangGraph)
        GR -->|2. Invoke Flow| LG[StateGraph Orchestrator]
        LG --> Node1[Analyzer Node]
        LG --> Node2[Retriever Node]
        LG --> Node3[Resolver Node]
        LG --> Node4[QA Validator Node]
        LG --> Node5[Escalation/SLA Node]
    end

    subgraph RAG & Data Stores
        Node2 -->|Semantic search| VS[(ChromaDB Vector Store)]
        Node5 -->|Save state / HITL| DB[(PostgreSQL Database)]
        LG -->|Session Caching| Cache[(Redis Cache)]
    end
    
    subgraph External Tools
        Node2 -->|Lookup invoice| CRM[Mock CRM Tool]
        Node2 -->|Lookup details| OM[Mock Order Management]
    end
```

---

## 🔄 Execution Sequence Loop

The diagram below maps the workflow when a customer submits a ticket to `POST /chat`.

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Client / Agent
    participant Gateway as FastAPI (main.py)
    participant Guards as Guardrails (src/guardrails/)
    participant Graph as LangGraph (src/agents/graph.py)
    participant RAG as Vector Store (src/rag/vector_store.py)
    participant DB as Postgres DB (src/database.py)

    Customer->>Gateway: POST /chat (session_id, customer_id, message)
    Gateway->>DB: Load session memory history
    Gateway->>Guards: Run security checks (PII, Injection, Jailbreaks)
    
    alt Security Threat Detected
        Guards-->>Gateway: Threat flagged
        Gateway-->>Customer: Return security validation error response (block)
    else Safety Checks Pass
        Gateway->>Graph: Invoke StateGraph (run_agent_workflow)
        
        Note over Graph: Node 1: Ticket Analyzer<br/>Classifies Priority, Sentiment, Intent
        
        Graph->>RAG: Node 2: Retrieve context scoped to KB Version
        RAG-->>Graph: Return document citations
        
        Note over Graph: Node 3: Resolution Agent<br/>Drafts response matching ticket and context
        
        Graph->>Guards: Node 4: Run QA evaluation & response leakage filters
        
        alt Hallucination or leakage detected
            Note over Graph: Flag response for escalation
        end
        
        Note over Graph: Node 5: SLA Prediction<br/>Assign routing queues
        
        Graph-->>Gateway: Return completed AgentState
        
        alt Human-In-The-Loop (HITL) Required
            Gateway->>DB: Create pending ResponseApproval ticket
        end
        
        Gateway->>DB: Commit session chat history & ticket parameters
        Gateway-->>Customer: Return ChatResponse (response, citations, approval_required)
    end
```

---

## 📊 Deployment Topology

For details regarding Kubernetes topology and Docker compose deployment layers, please consult the [Deployment Guide](DEPLOYMENT_GUIDE.md).
