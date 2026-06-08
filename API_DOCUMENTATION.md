# API Specification

This document details the HTTP endpoints, input schemas, response bodies, and security constraints for **SupportGPT Enterprise**.

All requests must accept and return JSON payloads.

---

## 🔒 Authentication & Authorization

Protected endpoints require a JWT bearer token attached to the `Authorization` header:
```http
Authorization: Bearer <your-jwt-token>
```

---

## 🚀 Authentication Endpoints

### 1. Register User
- **Route**: `POST /auth/register`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "username": "agent_dan",
    "password": "dansecretpassword",
    "role": "agent"
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "id": 1,
    "username": "agent_dan",
    "role": "agent",
    "created_at": "2026-06-08T16:32:00Z"
  }
  ```

### 2. Login Token
- **Route**: `POST /auth/token`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "username": "agent_dan",
    "password": "dansecretpassword"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "role": "agent"
  }
  ```

---

## 🤖 Core Copilot Endpoints

### 1. Conversational Chat
- **Route**: `POST /chat`
- **Access**: Public (registers ticket automatically)
- **Request Body**:
  ```json
  {
    "session_id": "sess_991",
    "customer_id": "cust_101",
    "message": "I would like to request a refund for my charge.",
    "kb_version": "v1"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "session_id": "sess_991",
    "response": "Thank you for reaching out... Approved refunds reflect in your statement in 3-5 days.",
    "sentiment": "negative",
    "priority": "high",
    "citations": [
      {
        "source": "Corporate Refund Policy (v1)",
        "text": "All billing refund requests must be filed within 30 days of payment.",
        "score": 0.98,
        "version": "v1"
      }
    ],
    "escalation_recommended": true,
    "escalation_reason": "Negative customer sentiment combined with high priority.",
    "cost_metadata": {
      "tokens_input": 150,
      "tokens_output": 80,
      "cost_usd": 0.0039,
      "latency_seconds": 1.45
    },
    "approval_required": true,
    "approval_id": 4
  }
  ```

### 2. Summarize Case Ticket
- **Route**: `POST /summarize-ticket`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "ticket_id": 1,
    "kb_version": "v1"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "ticket_id": 1,
    "summary": "The customer is reporting an issue regarding billing. Category: billing.",
    "key_issues": ["Billing issue", "Detected Intent: billing_dispute"],
    "sentiment": "negative",
    "priority": "high",
    "urgency_score": 0.9
  }
  ```

### 3. Suggest Response
- **Route**: `POST /suggest-response`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "ticket_id": 1,
    "kb_version": "v1"
  }
  ```

### 4. Run Offline Metrics Evaluation
- **Route**: `POST /evaluate-response`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "query": "I want a refund",
    "context": ["Corporate refund policies state requests must be filed within 30 days."],
    "response": "According to corporate policies, refund requests must be filed within 30 days."
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "faithfulness_score": 1.0,
    "context_precision": 1.0,
    "context_recall": 1.0,
    "hallucination_rate": 0.0,
    "answer_relevance": 1.0,
    "overall_quality_score": 1.0,
    "passed_evaluation": true,
    "report_summary": "Evaluation completed in 0.01s. Quality: 1.0. Passed: True."
  }
  ```

---

## 🧑‍💻 Human-In-The-Loop Approval Endpoints

### 1. List Pending Approvals
- **Route**: `GET /approvals/pending`
- **Access**: Protected (Agent / Manager role)
- **Response** (200 OK):
  ```json
  [
    {
      "id": 4,
      "ticket_id": 1,
      "status": "pending",
      "final_response": "Thank you for reaching out... Approved refunds reflect in 3-5 days.",
      "latency_seconds": 0.0,
      "approved_at": "2026-06-08T16:32:00Z"
    }
  ]
  ```

### 2. Process Approval Ticket
- **Route**: `POST /approvals/{approval_id}`
- **Access**: Protected (Agent / Manager role)
- **Request Body**:
  ```json
  {
    "approval_id": 4,
    "modified_response": "This is my edited support agent answer for the user.",
    "status": "approved"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "id": 4,
    "ticket_id": 1,
    "status": "approved",
    "final_response": "This is my edited support agent answer for the user.",
    "latency_seconds": 45.5,
    "approved_at": "2026-06-08T16:32:45Z"
  }
  ```
