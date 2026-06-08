import React from 'react';
import { DollarSign, Cpu, Clock, ShieldAlert } from 'lucide-react';

export default function MetricsGrid({ metrics = {} }) {
  const items = [
    {
      title: 'Estimated API Cost',
      value: `$${(metrics.cost || 0.0).toFixed(4)}`,
      desc: 'Based on token usage rates',
      icon: DollarSign,
      color: '#10b981',
    },
    {
      title: 'LLM Tokens Consumed',
      value: (metrics.tokens || 0).toLocaleString(),
      desc: 'Prompt + Completion tokens',
      icon: Cpu,
      color: '#3b82f6',
    },
    {
      title: 'Avg Agent Latency',
      value: `${(metrics.latency || 0).toFixed(2)}s`,
      desc: 'LangGraph execution span',
      icon: Clock,
      color: '#eab308',
    },
    {
      title: 'Guardrail Intercepts',
      value: metrics.violations || 0,
      desc: 'PII, Injection, and Jailbreaks',
      icon: ShieldAlert,
      color: '#ef4444',
    },
  ];

  return (
    <div className="metrics-panel">
      {items.map((item, idx) => (
        <div key={idx} className="glass-card" style={{ borderLeft: `4px solid ${item.color}` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: '#9ca3af', fontWeight: '500' }}>{item.title}</span>
            <item.icon size={18} color={item.color} />
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', fontFamily: 'Outfit, sans-serif', marginBottom: '0.2rem' }}>
            {item.value}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{item.desc}</div>
        </div>
      ))}
    </div>
  );
}
