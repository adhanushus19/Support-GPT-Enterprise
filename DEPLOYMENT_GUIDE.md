# Deployment & Scaling Manual

This document outlines deployment configurations, scaling topologies, persistent storage setups, and monitoring configurations for **SupportGPT Enterprise**.

---

## 🐳 Docker Container Orchestration

To run the application locally in an isolated docker cluster:

1. Clone the repository and execute compose:
   ```bash
   docker-compose -f deployment/docker-compose.yml up --build
   ```
2. This spins up the following services:
   - **FastAPI Backend (`backend`)**: Exposed on port `8000`.
   - **PostgreSQL Database (`db`)**: Exposes database connection on standard port `5432`.
   - **Redis Cache (`cache`)**: Listening on standard port `6379`.
   - **Prometheus Metric Scraper (`prometheus`)**: Serves monitoring dashboards on port `9090`.

---

## ☸️ Kubernetes Cluster Deployment

For cloud environments (EKS, GKE, AKS), use the manifests located in `deployment/k8s/`:

1. Apply config values:
   ```bash
   kubectl apply -f deployment/k8s/configmap.yml
   ```
2. Deploy replicas and routing service:
   ```bash
   kubectl apply -f deployment/k8s/deployment.yml
   ```

### Scaling Details
- **Replication**: The default manifest configures `replicas: 3` with rolling update strategies.
- **Resources**: Backend containers request `512Mi` of memory and limit usage to `1Gi` to avoid out-of-memory restarts.
- **Probes**: Ingress and backend containers run Readiness and Liveness probes checking `/health` on port `8000`.

---

## 📈 Monitoring & Telemetry Scrapers

We mount `monitoring/prometheus.yml` directly into the Prometheus container to scrap metrics from the backend service at 15-second intervals.

### Metrics Exposed at `/metrics`
- `http_requests_total`: Counter tracking request endpoints and HTTP codes.
- `http_request_duration_seconds`: Histogram tracking request durations.
- `llm_cost_total`: Counter tracking cumulative LLM dollars spent.
- `llm_tokens_total`: Counter tracking input/output tokens.
- `guardrail_violations_total`: Counter tracking scrubbed PII or blocked injections.
