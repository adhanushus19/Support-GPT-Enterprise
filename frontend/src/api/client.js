const BASE_URL = 'http://localhost:8000';

function getHeaders() {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function login(username, password) {
  const response = await fetch(`${BASE_URL}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) {
    throw new Error('Authentication failed');
  }
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('role', data.role);
  localStorage.setItem('username', username);
  return data;
}

export function logout() {
  localStorage.clear();
}

export async function register(username, password, role = 'agent') {
  const response = await fetch(`${BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, role }),
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Registration failed');
  }
  return response.json();
}

export async function fetchTickets() {
  const response = await fetch(`${BASE_URL}/tickets`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch tickets');
  return response.json();
}

export async function createTicket(customerId, subject, description) {
  const response = await fetch(`${BASE_URL}/tickets`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ customer_id: customerId, subject, description }),
  });
  if (!response.ok) throw new Error('Failed to create ticket');
  return response.json();
}

export async function fetchPendingApprovals() {
  const response = await fetch(`${BASE_URL}/approvals/pending`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch approvals');
  return response.json();
}

export async function submitApproval(approvalId, status, modifiedResponse) {
  const response = await fetch(`${BASE_URL}/approvals/${approvalId}`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ approval_id: approvalId, status, modified_response: modifiedResponse }),
  });
  if (!response.ok) throw new Error('Failed to process approval request');
  return response.json();
}

export async function submitChat(message, customerId, sessionId, kbVersion = 'v1') {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ message, customer_id: customerId, session_id: sessionId, kb_version: kbVersion }),
  });
  if (!response.ok) throw new Error('Chat request failed');
  return response.json();
}

export async function fetchCustomerContext(customerId) {
  const response = await fetch(`${BASE_URL}/customer-context`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ customer_id: customerId }),
  });
  if (!response.ok) throw new Error('Failed to load customer profile');
  return response.json();
}

export async function evaluateResponse(query, context, responseText) {
  const response = await fetch(`${BASE_URL}/evaluate-response`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ query, context, response: responseText }),
  });
  if (!response.ok) throw new Error('Evaluation request failed');
  return response.json();
}
