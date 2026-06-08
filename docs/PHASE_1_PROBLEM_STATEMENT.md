# Phase 1: Problem Statement

## 🎯 Goals
Customer support teams are burdened with manual workflows that lower efficiency:
1. **Long Average Handle Times (AHT)**: Reps spend too much time reading documentation, fetching order histories, or searching historical solutions.
2. **Reduced Customer Satisfaction (CSAT)**: Inconsistent responses or delay escalations hurt user trust.
3. **High Operational Costs**: Manual routing and SLA sorting require extensive staff overhead.

The goal is to build an AI Copilot that acts as a supportive companion for human support agents.

---

## ⚙️ Design Decisions
Rather than replacing human agents with an unmonitored chatbot, SupportGPT Enterprise implements a **Human-in-the-Loop** architecture:
- High-priority, negative-sentiment, or low-QA-score responses are staged in a validation queue.
- Agents verify, edit, and approve drafts before they are sent, improving accuracy.

---

## 💻 Code Walkthrough Reference
- Safety guardrails and validation routing is implemented in [analyzer.py](file:///C:/Users/adhan/.gemini/antigravity/scratch/supportgpt-enterprise/src/agents/analyzer.py).
- LangGraph orchestration graph transitions are configured in [graph.py](file:///C:/Users/adhan/.gemini/antigravity/scratch/supportgpt-enterprise/src/agents/graph.py).

---

## 🧪 Validation Steps
1. Send ticket chat payloads to `POST /chat`.
2. Inspect responses to verify they map correct classifications.
