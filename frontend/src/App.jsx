import React, { useState, useEffect } from 'react';
import { fetchTickets, createTicket, login, register, logout } from './api/client';
import MetricsGrid from './components/MetricsGrid';
import TicketList from './components/TicketList';
import TicketDetails from './components/TicketDetails';
import { Sparkles, Key, LogOut, CheckCircle, RefreshCw } from 'lucide-react';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState('');
  const [username, setUsername] = useState('');
  const [loginUser, setLoginUser] = useState('');
  const [loginPass, setLoginPass] = useState('');

  // Main lists and states
  const [tickets, setTickets] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [kbVersion, setKbVersion] = useState('v1');
  const [showModal, setShowModal] = useState(false);
  const [newCustId, setNewCustId] = useState('cust_101');
  const [newSubject, setNewSubject] = useState('');
  const [newDesc, setNewDesc] = useState('');

  // Performance telemetry states
  const [sysMetrics, setSysMetrics] = useState({
    cost: 0.0035,
    tokens: 1450,
    latency: 1.25,
    violations: 0
  });

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
      setUserRole(localStorage.getItem('role') || 'agent');
      setUsername(localStorage.getItem('username') || '');
      loadTickets();
    }
  }, [isAuthenticated]);

  async function loadTickets() {
    try {
      const list = await fetchTickets();
      setTickets(list);
    } catch (err) {
      console.error('Error loading tickets:', err);
    }
  }

  async function handleLogin(e) {
    e.preventDefault();
    try {
      await login(loginUser, loginPass);
      setIsAuthenticated(true);
    } catch (err) {
      alert('Login failed. Please verify credentials.');
    }
  }

  async function handleRegister(role) {
    if (!loginUser || !loginPass) {
      alert('Please fill out credentials first.');
      return;
    }
    try {
      await register(loginUser, loginPass, role);
      alert(`User ${loginUser} registered as ${role}. Please login.`);
    } catch (err) {
      alert(err.message);
    }
  }

  function handleLogout() {
    logout();
    setIsAuthenticated(false);
    setTickets([]);
    setSelectedTicket(null);
  }

  async function handleCreateTicket(e) {
    e.preventDefault();
    try {
      await createTicket(newCustId, newSubject, newDesc);
      setShowModal(false);
      setNewSubject('');
      setNewDesc('');
      loadTickets();
      alert('Ticket submitted successfully!');
    } catch (err) {
      alert(err.message);
    }
  }

  // Update telemetry stats based on ticket events
  function handleActionComplete() {
    loadTickets();
    setSelectedTicket(null);
    setSysMetrics(prev => ({
      ...prev,
      cost: prev.cost + 0.0012,
      tokens: prev.tokens + 450,
      latency: (prev.latency + 0.85) / 2
    }));
  }

  if (!isAuthenticated) {
    return (
      <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center' }}>
        <div className="glass-card" style={{ width: '400px', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ textAlign: 'center' }}>
            <h1 style={{ margin: 0, fontFamily: 'Outfit, sans-serif', fontSize: '1.6rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
              <Sparkles color="#8b5cf6" size={24} /> SupportGPT
            </h1>
            <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.8rem', color: '#9ca3af' }}>Enterprise AI Customer Support Portal</p>
          </div>

          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              <label style={{ fontSize: '0.8rem', fontWeight: '500', color: '#9ca3af' }}>Username</label>
              <input
                type="text"
                value={loginUser}
                onChange={(e) => setLoginUser(e.target.value)}
                style={{ padding: '0.6rem', background: '#0f172a', border: '1px solid var(--border-color)', borderRadius: '6px', color: '#fff' }}
                required
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              <label style={{ fontSize: '0.8rem', fontWeight: '500', color: '#9ca3af' }}>Password</label>
              <input
                type="password"
                value={loginPass}
                onChange={(e) => setLoginPass(e.target.value)}
                style={{ padding: '0.6rem', background: '#0f172a', border: '1px solid var(--border-color)', borderRadius: '6px', color: '#fff' }}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: '0.5rem' }}>
              Sign In
            </button>
          </form>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', textAlign: 'center' }}>Or register seed user:</div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button onClick={() => handleRegister('agent')} className="btn btn-secondary" style={{ flex: 1, padding: '0.4rem', fontSize: '0.75rem' }}>
                Register Agent
              </button>
              <button onClick={() => handleRegister('admin')} className="btn btn-secondary" style={{ flex: 1, padding: '0.4rem', fontSize: '0.75rem' }}>
                Register Admin
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="app-title-group">
          <h1>SupportGPT Enterprise</h1>
          <p>Multi-Agent AI Copilot Dashboard</p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          {/* KB Version dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', color: '#9ca3af' }}>KB Version:</span>
            <select
              value={kbVersion}
              onChange={(e) => setKbVersion(e.target.value)}
              style={{
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                color: '#fff',
                padding: '0.4rem',
                fontSize: '0.8rem'
              }}
            >
              <option value="v1">v1 - Active Policy</option>
              <option value="v2">v2 - Extended 60-Day Policy</option>
              <option value="v3">v3 - Draft version</option>
            </select>
          </div>

          {/* User profile and logout */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', fontSize: '0.85rem' }}>
            <span style={{ color: '#8b5cf6', fontWeight: 'bold', textTransform: 'capitalize' }}>
              {username} ({userRole})
            </span>
            <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '0.4rem', borderRadius: '50%' }}>
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </header>

      {/* Metrics Section */}
      <MetricsGrid metrics={sysMetrics} />

      {/* Main Grid: sidebar and details */}
      <main className="grid-dashboard">
        <TicketList
          tickets={tickets}
          selectedId={selectedTicket?.id}
          onSelect={(t) => setSelectedTicket(t)}
          onNewTicket={() => setShowModal(true)}
        />

        <TicketDetails
          ticket={selectedTicket ? { ...selectedTicket, kb_version: kbVersion } : null}
          onActionComplete={handleActionComplete}
        />
      </main>

      {/* New Ticket Modal */}
      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          backdropFilter: 'blur(4px)'
        }}>
          <div className="glass-card" style={{ width: '450px', display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
            <h2 style={{ margin: 0, fontSize: '1.2rem', fontFamily: 'Outfit, sans-serif' }}>Submit Customer Case</h2>
            
            <form onSubmit={handleCreateTicket} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <label style={{ fontSize: '0.8rem', color: '#9ca3af' }}>Customer Profile ID</label>
                <select
                  value={newCustId}
                  onChange={(e) => setNewCustId(e.target.value)}
                  style={{ padding: '0.6rem', background: '#0f172a', border: '1px solid var(--border-color)', borderRadius: '6px', color: '#fff' }}
                >
                  <option value="cust_101">cust_101 (Jane Doe - VIP)</option>
                  <option value="cust_102">cust_102 (John Smith - Standard)</option>
                  <option value="cust_103">cust_103 (Acme Corp - Enterprise)</option>
                </select>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <label style={{ fontSize: '0.8rem', color: '#9ca3af' }}>Subject / Case Title</label>
                <input
                  type="text"
                  value={newSubject}
                  onChange={(e) => setNewSubject(e.target.value)}
                  style={{ padding: '0.6rem', background: '#0f172a', border: '1px solid var(--border-color)', borderRadius: '6px', color: '#fff' }}
                  required
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <label style={{ fontSize: '0.8rem', color: '#9ca3af' }}>Detailed Issue Description</label>
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  style={{ padding: '0.6rem', background: '#0f172a', border: '1px solid var(--border-color)', borderRadius: '6px', color: '#fff', height: '100px', resize: 'vertical' }}
                  required
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
                  File Case
                </button>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary" style={{ flex: 1 }}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
