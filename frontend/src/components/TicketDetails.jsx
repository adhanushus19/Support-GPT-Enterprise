import React, { useState, useEffect } from 'react';
import { fetchCustomerContext, submitChat, submitApproval, evaluateResponse } from '../api/client';
import { User, ShoppingBag, ShieldAlert, Sparkles, BookOpen, CheckCircle, RefreshCw } from 'lucide-react';

export default function TicketDetails({ ticket, onActionComplete }) {
  const [customer, setCustomer] = useState(null);
  const [chatOutput, setChatOutput] = useState(null);
  const [editedResponse, setEditedResponse] = useState('');
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [evalLoading, setEvalLoading] = useState(false);

  // Reload customer and trigger AI draft when ticket changes
  useEffect(() => {
    if (!ticket) return;
    setCustomer(null);
    setChatOutput(null);
    setEditedResponse('');
    setEvaluation(null);
    loadDetails();
  }, [ticket]);

  async function loadDetails() {
    setLoading(true);
    try {
      // 1. Fetch CRM details
      const crmProfile = await fetchCustomerContext(ticket.customer_id);
      setCustomer(crmProfile);

      // 2. Call chat/graph flow to generate suggestions
      const aiSessionId = `session_${ticket.id}`;
      const chatRes = await submitChat(ticket.description, ticket.customer_id, aiSessionId);
      setChatOutput(chatRes);
      setEditedResponse(chatRes.response);
    } catch (err) {
      console.error('Error loading details:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleApproval(status) {
    if (!chatOutput || !chatOutput.approval_id) return;
    setLoading(true);
    try {
      await submitApproval(chatOutput.approval_id, status, editedResponse);
      alert(`AI Suggestion ${status} successfully.`);
      if (onActionComplete) onActionComplete();
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function triggerEvaluation() {
    if (!chatOutput) return;
    setEvalLoading(true);
    try {
      const contexts = chatOutput.citations.map(c => c.text);
      const evalRes = await evaluateResponse(ticket.description, contexts, editedResponse);
      setEvaluation(evalRes);
    } catch (err) {
      alert('Failed to evaluate response: ' + err.message);
    } finally {
      setEvalLoading(false);
    }
  }

  if (!ticket) {
    return (
      <div className="glass-card" style={{ display: 'flex', flex: 1, alignItems: 'center', justifyContent: 'center', height: '550px', color: '#6b7280' }}>
        Select a customer case to inspect details and activate Copilot.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* 1. Original Ticket Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.8rem' }}>
          <h2 style={{ margin: 0, fontSize: '1.2rem', fontFamily: 'Outfit, sans-serif' }}>
            Case #{ticket.id}: {ticket.subject}
          </h2>
          <span className={`badge badge-priority-${ticket.priority}`}>{ticket.priority}</span>
        </div>
        <p style={{ margin: 0, fontSize: '0.95rem', color: '#d1d5db', lineHeight: 1.5, background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          {ticket.description}
        </p>
      </div>

      {loading ? (
        <div className="glass-card" style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <RefreshCw className="animate-spin" size={24} style={{ animation: 'spin 1.5s linear infinite' }} />
        </div>
      ) : (
        <>
          {/* 2. Customer CRM Context & Order history */}
          {customer && (
            <div className="glass-card" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
              <div>
                <h3 style={{ margin: '0 0 0.8rem 0', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#8b5cf6' }}>
                  <User size={16} /> CRM Customer Profile
                </h3>
                <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  <div><strong>Customer Name:</strong> {customer.name}</div>
                  <div><strong>Email:</strong> {customer.customer_id}@enterprise.com</div>
                  <div><strong>Tier Status:</strong> <span style={{ fontWeight: 'bold', color: '#8b5cf6' }}>{customer.tier}</span></div>
                  <div><strong>Open Tickets:</strong> {customer.open_tickets_count}</div>
                </div>
              </div>

              <div>
                <h3 style={{ margin: '0 0 0.8rem 0', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#3b82f6' }}>
                  <ShoppingBag size={16} /> Recent Invoice / Orders
                </h3>
                <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {customer.recent_orders.length === 0 ? (
                    <div style={{ color: '#6b7280' }}>No recent orders.</div>
                  ) : (
                    customer.recent_orders.map((o, idx) => (
                      <div key={idx} style={{ padding: '0.3rem', background: 'rgba(255,255,255,0.01)', border: '1px dashed rgba(255,255,255,0.05)', borderRadius: '4px' }}>
                        <div><strong>ID:</strong> {o.order_id} ({o.status})</div>
                        <div style={{ color: '#9ca3af', fontSize: '0.75rem' }}>Item: {o.items.join(', ')} - ${o.total_amount}</div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}

          {/* 3. AI Copilot Panel */}
          {chatOutput && (
            <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem', border: '1px solid rgba(139, 92, 246, 0.25)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.6rem' }}>
                <h3 style={{ margin: 0, fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#a5b4fc', fontFamily: 'Outfit, sans-serif' }}>
                  <Sparkles size={18} color="#8b5cf6" /> SupportGPT AI Assistant
                </h3>
                {chatOutput.approval_required && (
                  <span className="badge badge-priority-urgent" style={{ fontSize: '0.7rem' }}>
                    Agent Approval Required
                  </span>
                )}
              </div>

              {/* Citations section */}
              <div>
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#9ca3af' }}>
                  <BookOpen size={14} /> Retrieved RAG Citations
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {chatOutput.citations.length === 0 ? (
                    <div style={{ fontSize: '0.8rem', color: '#6b7280', fontStyle: 'italic' }}>No supporting articles retrieved.</div>
                  ) : (
                    chatOutput.citations.map((c, idx) => (
                      <div key={idx} style={{ padding: '0.6rem', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)', borderRadius: '6px', fontSize: '0.8rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', color: '#3b82f6', fontWeight: '500', marginBottom: '0.2rem' }}>
                          <span>Source: {c.source}</span>
                          <span>Score: {c.score}</span>
                        </div>
                        <div style={{ color: '#d1d5db' }}>{c.text}</div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* SLA / Escalation Alert */}
              {chatOutput.escalation_recommended && (
                <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '0.8rem', borderRadius: '6px', display: 'flex', alignItems: 'flex-start', gap: '0.6rem' }}>
                  <ShieldAlert color="#ef4444" size={18} style={{ flexShrink: 0, marginTop: '0.1rem' }} />
                  <div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 'bold', color: '#ef4444' }}>Escalation Recommendation</div>
                    <div style={{ fontSize: '0.8rem', color: '#fca5a5' }}>Reason: {chatOutput.escalation_reason}</div>
                  </div>
                </div>
              )}

              {/* Response Draft Box */}
              <div>
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.85rem', color: '#9ca3af' }}>Suggested Response Message</h4>
                <textarea
                  value={editedResponse}
                  onChange={(e) => setEditedResponse(e.target.value)}
                  style={{
                    width: '100%',
                    height: '140px',
                    padding: '0.8rem',
                    borderRadius: '8px',
                    background: '#0f172a',
                    border: '1px solid var(--border-color)',
                    color: '#f3f4f6',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '0.9rem',
                    lineHeight: 1.5,
                    resize: 'vertical',
                    boxSizing: 'border-box'
                  }}
                  placeholder="Review drafted answer here..."
                />
              </div>

              {/* Human-in-the-loop triggers */}
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                {chatOutput.approval_required ? (
                  <>
                    <button onClick={() => handleApproval('approved')} className="btn btn-primary">
                      <CheckCircle size={16} /> Approve & Close Ticket
                    </button>
                    <button onClick={() => handleApproval('modified')} className="btn btn-secondary">
                      Apply Custom Edits
                    </button>
                  </>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#10b981', fontSize: '0.85rem', fontWeight: '600' }}>
                    <CheckCircle size={16} /> Suggestion verified and ready to send.
                  </div>
                )}
                
                <button onClick={triggerEvaluation} className="btn btn-secondary" style={{ marginLeft: 'auto' }}>
                  <Sparkles size={14} /> Run Ragas & DeepEval Metrics
                </button>
              </div>

              {/* Evaluation score panel */}
              {evalLoading && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#9ca3af', fontSize: '0.85rem' }}>
                  <RefreshCw className="animate-spin" size={14} style={{ animation: 'spin 1.5s linear infinite' }} /> Computing evaluation matrix metrics...
                </div>
              )}

              {evaluation && (
                <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '0.9rem', color: '#a5b4fc', fontFamily: 'Outfit, sans-serif' }}>
                    RAGAS & DeepEval Evaluation Scores
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.8rem' }}>
                    <div style={{ padding: '0.5rem', background: '#0f172a', borderRadius: '4px', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Faithfulness</div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#10b981' }}>{evaluation.faithfulness_score}</div>
                    </div>
                    <div style={{ padding: '0.5rem', background: '#0f172a', borderRadius: '4px', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Hallucination Rate</div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: evaluation.hallucination_rate > 0.3 ? '#ef4444' : '#10b981' }}>{evaluation.hallucination_rate}</div>
                    </div>
                    <div style={{ padding: '0.5rem', background: '#0f172a', borderRadius: '4px', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Context Recall</div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#3b82f6' }}>{evaluation.context_recall}</div>
                    </div>
                    <div style={{ padding: '0.5rem', background: '#0f172a', borderRadius: '4px', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Answer Relevance</div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#eab308' }}>{evaluation.answer_relevance}</div>
                    </div>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#d1d5db', lineHeight: 1.4, borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '0.5rem' }}>
                    {evaluation.report_summary}
                  </div>
                </div>
              )}

            </div>
          )}
        </>
      )}
    </div>
  );
}
