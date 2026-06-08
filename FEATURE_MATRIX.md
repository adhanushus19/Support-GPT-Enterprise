# SupportGPT Enterprise Feature Matrix

This document provides a consolidated overview of the technical capabilities, algorithms, and modules implemented inside the **SupportGPT Enterprise** repository.

---

## 🛠️ Feature Matrix

| Functional Group | Tech Module | Feature Capabilities | Status |
|---|---|---|---|
| **Multi-Agent Orchestration** | LangGraph | State-driven workflow routing, self-correction nodes | ✅ Implemented |
| **Document Ingestion** | Ingestion Engine | Parsing PDF, DOCX, HTML, JSON FAQs, TXT, MD | ✅ Implemented |
| **Semantic Search** | Vector DB | Cosine distance similarity querying | ✅ Implemented |
| **Metadata Filtering** | Vector DB | Query scopes restricted by document category | ✅ Implemented |
| **Knowledge Versioning** | Versioning Service | Isolated vector indexing for version tags (`v1`, `v2`, `v3`) | ✅ Implemented |
| **PII Anonymization** | Input Guardrail | Regular expression masking for Emails, Cards, SSNs, Phones | ✅ Implemented |
| **Jailbreak Intercept** | Input Guardrail | Matching keywords (DAN, unlocked, sudo) | ✅ Implemented |
| **Injection Block** | Input Guardrail | Detecting context bypass prompts (ignore previous instructions) | ✅ Implemented |
| **Leakage Response Filter** | Output Guardrail | Masking internal agent configurations and graph contexts | ✅ Implemented |
| **Estimated Pricing** | Observability | Tracking USD costs dynamically based on model usage | ✅ Implemented |
| **Metrics Collector** | Observability | Prometheus counters/histograms for request throughput/latency | ✅ Implemented |
| **Distributed Tracing** | Observability | OpenTelemetry console export and LangSmith flags | ✅ Implemented |
| **Faithfulness Check** | Evaluation | Scopes response facts against retrieved context | ✅ Implemented |
| **Hallucination Tracker** | Evaluation | Computes percentage of unsupported assertions | ✅ Implemented |
| **Context Recall & Precision** | Evaluation | Evaluates relevance of ChromaDB retrieved chunks | ✅ Implemented |
| **Human-in-the-Loop** | Approval Workflow | Staging draft responses, capturing review latency times | ✅ Implemented |
| **Secure Authentication** | Auth gateway | JWT encryption and password hashing using bcrypt | ✅ Implemented |
| **Role-Based Authorization** | Auth gateway | Restricting endpoints to Agent, Manager, and Admin users | ✅ Implemented |
| **Locust Load Test** | Load validation | Simulating concurrent chat queries and approval pipelines | ✅ Implemented |
| **GitHub actions pipeline** | CI/CD | Auto-verifying unit and integration testing files | ✅ Implemented |
| **Vite / React UI** | Frontend | Glassmorphism dashboard displaying active tickets, metrics | ✅ Implemented |

---

## 🔗 Deep Technical Details
For deeper insights:
- **Agent workflows**: [Agent Architecture Guide](docs/AGENT_ARCHITECTURE.md)
- **RAG implementation**: [RAG Architecture Guide](docs/RAG_ARCHITECTURE.md)
- **API reference**: [API Documentation Reference](API_DOCUMENTATION.md)
- **Testing instructions**: [Testing and Performance Guide](docs/TESTING_GUIDE.md)
