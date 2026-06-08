# Phase 9: Monitoring

## 🎯 Goals
Expose telemetry scrapers at `/metrics`. Track active sessions, API token usage volumes, transaction costs, and latency across endpoints.

---

## ⚙️ Design Decisions
- **Prometheus Scrapers**: Mounts metrics endpoint using `prometheus_client`.
- **Grafana Panel Configuration**: Pre-defines panels to visualize cost accumulations, request volumes, and guardrail hits.

---

## 💻 Code Walkthrough Reference
- Metric registers: [metrics.py](file:///C:/Users/adhan/.gemini/antigravity/scratch/supportgpt-enterprise/src/observability/metrics.py).
- Request duration metrics capture: [main.py](file:///C:/Users/adhan/.gemini/antigravity/scratch/supportgpt-enterprise/src/main.py).
- Dashboard JSON layouts: [grafana-dashboard.json](file:///C:/Users/adhan/.gemini/antigravity/scratch/supportgpt-enterprise/monitoring/grafana-dashboard.json).

---

## 🧪 Validation Steps
1. Curl the metrics endpoint: `curl http://localhost:8000/metrics`.
2. Inspect if counters increment after submitting tickets.
