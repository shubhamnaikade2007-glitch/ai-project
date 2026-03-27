// HealthFit AI - Login Page
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const s: Record<string, React.CSSProperties> = {
  page:      { minHeight: '100vh', display: 'flex', background: 'linear-gradient(135deg, #0f2027, #203a43, #2c5364)', fontFamily: "'Segoe UI', system-ui, sans-serif" },
  left:      { flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '60px 80px', color: '#fff' },
  brand:     { fontSize: 32, fontWeight: 800, color: '#4ade80', marginBottom: 12 },
  tagline:   { fontSize: 18, opacity: 0.8, maxWidth: 380, lineHeight: 1.6 },
  features:  { marginTop: 48, display: 'flex', flexDirection: 'column', gap: 16 },
  feature:   { display: 'flex', alignItems: 'center', gap: 14, fontSize: 15, opacity: 0.85 },
  featureIcon: { width: 36, height: 36, borderRadius: '50%', background: 'rgba(74,222,128,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, flexShrink: 0 },
  right:     { width: 480, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 40 },
  card:      { background: '#fff', borderRadius: 20, padding: '44px 40px', width: '100%', boxShadow: '0 25px 60px rgba(0,0,0,0.3)' },
  title:     { fontSize: 26, fontWeight: 700, color: '#1a202c', marginBottom: 6 },
  subtitle:  { fontSize: 14, color: '#718096', marginBottom: 32 },
  tabs:      { display: 'flex', background: '#f7fafc', borderRadius: 10, padding: 4, marginBottom: 28, gap: 4 },
  tab:       { flex: 1, padding: '8px 0', border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 14, fontWeight: 500, background: 'none', color: '#718096', transition: 'all 0.2s' },
  tabActive: { background: '#fff', color: '#2c5364', fontWeight: 600, boxShadow: '0 1px 4px rgba(0,0,0,0.1)' },
  label:     { display: 'block', fontSize: 13, fontWeight: 600, color: '#4a5568', marginBottom: 6, marginTop: 16 },
  input:     { width: '100%', padding: '11px 14px', border: '1px solid #e2e8f0', borderRadius: 10, fontSize: 14, color: '#2d3748', outline: 'none', boxSizing: 'border-box', transition: 'border-color 0.2s' },
  row:       { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 },
  btn:       { width: '100%', marginTop: 24, padding: '13px', background: 'linear-gradient(135deg, #203a43, #2c5364)', color: '#fff', border: 'none', borderRadius: 10, fontSize: 15, fontWeight: 600, cursor: 'pointer', transition: 'opacity 0.2s' },
  btnDisabled: { opacity: 0.6, cursor: 'not-allowed' },
  error:     { marginTop: 12, padding: '10px 14px', background: '#fff5f5', color: '#c53030', borderRadius: 8, fontSize: 13, border: '1px solid #fed7d7' },
  demo:      { marginTop: 20, padding: '14px', background: '#f0fff4', borderRadius: 10, fontSize: 13, color: '#276749' },
  demoTitle: { fontWeight: 600, marginBottom: 6 },
  demoRow:   { display: 'flex', justifyContent: 'space-between', marginTop: 4 },
};

const DEMO_ACCOUNTS = [
  { label: 'Patient',  email: 'patient@healthfit.com', password: 'password123' },
  { label: 'Doctor',   email: 'doctor@healthfit.com',  password: 'password123' },
  { label: 'Admin',    email: 'admin@healthfit.com',   password: 'admin123' },
];

const Login: React.FC = () => {
  const navigate  = useNavigate();
  const { login, register, loading, error, clearError } = useAuth();
  const [tab, setTab]     = useState<'login'|'register'>('login');
  const [form, setForm]   = useState({
    email: '', password: '', first_name: '', last_name: '',
    gender: '', phone: '', role: 'patient',
  });

  useEffect(() => { clearError(); }, [tab]);

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await login({ email: form.email, password: form.password });
    if ((result as any).payload?.access_token) navigate('/dashboard');
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await register({
      email: form.email, password: form.password,
      first_name: form.first_name, last_name: form.last_name,
      gender: form.gender || undefined, phone: form.phone || undefined,
      role: form.role,
    });
    if ((result as any).payload?.access_token) navigate('/dashboard');
  };

  const fillDemo = (acc: typeof DEMO_ACCOUNTS[0]) => {
    setForm(f => ({ ...f, email: acc.email, password: acc.password }));
    setTab('login');
  };

  const inputStyle = (focused?: boolean): React.CSSProperties => ({
    ...s.input,
    borderColor: focused ? '#2c5364' : '#e2e8f0',
  });

  return (
    <div style={s.page}>
      {/* Left panel */}
      <div style={s.left}>
        <div style={s.brand}>🏃 HealthFit AI</div>
        <div style={s.tagline}>
          Your intelligent health companion. Track vitals, schedule appointments, analyze fitness, and get AI-powered health insights — all in one place.
        </div>
        <div style={s.features}>
          {[
            ['📊', 'Real-time health metrics & trend analysis'],
            ['🤖', 'AI-powered health risk predictions'],
            ['📅', 'Doctor appointment scheduling'],
            ['🥗', 'Nutrition tracking & meal recommendations'],
            ['💪', 'Exercise form analysis with MediaPipe'],
            ['😴', 'Sleep quality & stress detection'],
          ].map(([icon, text]) => (
            <div key={text as string} style={s.feature}>
              <div style={s.featureIcon}>{icon}</div>
              <span>{text}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Right panel – card */}
      <div style={s.right}>
        <div style={s.card}>
          <div style={s.title}>Welcome back 👋</div>
          <div style={s.subtitle}>Sign in to your HealthFit account</div>

          {/* Tabs */}
          <div style={s.tabs}>
            {(['login', 'register'] as const).map(t => (
              <button key={t} style={{ ...s.tab, ...(tab === t ? s.tabActive : {}) }}
                onClick={() => setTab(t)}>
                {t === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            ))}
          </div>

          {/* Error */}
          {error && <div style={s.error}>⚠️ {error}</div>}

          {/* Login form */}
          {tab === 'login' && (
            <form onSubmit={handleLogin}>
              <label style={s.label}>Email Address</label>
              <input style={inputStyle()} type="email" placeholder="you@example.com"
                value={form.email} onChange={e => set('email', e.target.value)} required />
              <label style={s.label}>Password</label>
              <input style={inputStyle()} type="password" placeholder="••••••••"
                value={form.password} onChange={e => set('password', e.target.value)} required />
              <button type="submit" style={{ ...s.btn, ...(loading ? s.btnDisabled : {}) }} disabled={loading}>
                {loading ? 'Signing in…' : 'Sign In →'}
              </button>
            </form>
          )}

          {/* Register form */}
          {tab === 'register' && (
            <form onSubmit={handleRegister}>
              <div style={s.row}>
                <div>
                  <label style={{ ...s.label, marginTop: 0 }}>First Name</label>
                  <input style={inputStyle()} placeholder="Alex"
                    value={form.first_name} onChange={e => set('first_name', e.target.value)} required />
                </div>
                <div>
                  <label style={{ ...s.label, marginTop: 0 }}>Last Name</label>
                  <input style={inputStyle()} placeholder="Johnson"
                    value={form.last_name} onChange={e => set('last_name', e.target.value)} required />
                </div>
              </div>
              <label style={s.label}>Email Address</label>
              <input style={inputStyle()} type="email" placeholder="you@example.com"
                value={form.email} onChange={e => set('email', e.target.value)} required />
              <label style={s.label}>Password</label>
              <input style={inputStyle()} type="password" placeholder="Min. 6 characters"
                value={form.password} onChange={e => set('password', e.target.value)} required minLength={6} />
              <div style={s.row}>
                <div>
                  <label style={s.label}>Gender</label>
                  <select style={inputStyle()} value={form.gender} onChange={e => set('gender', e.target.value)}>
                    <option value="">Select</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label style={s.label}>Phone</label>
                  <input style={inputStyle()} placeholder="+1-555-0100"
                    value={form.phone} onChange={e => set('phone', e.target.value)} />
                </div>
              </div>
              <label style={s.label}>Account Type</label>
              <select style={inputStyle()} value={form.role} onChange={e => set('role', e.target.value)}>
                <option value="patient">Patient</option>
                <option value="doctor">Healthcare Provider</option>
              </select>
              <button type="submit" style={{ ...s.btn, ...(loading ? s.btnDisabled : {}) }} disabled={loading}>
                {loading ? 'Creating account…' : 'Create Account →'}
              </button>
            </form>
          )}

          {/* Demo accounts */}
          <div style={s.demo}>
            <div style={s.demoTitle}>🚀 Demo accounts (click to auto-fill)</div>
            {DEMO_ACCOUNTS.map(acc => (
              <div key={acc.label} style={s.demoRow}>
                <span>{acc.label}</span>
                <button onClick={() => fillDemo(acc)}
                  style={{ background: '#276749', color: '#fff', border: 'none', borderRadius: 6, padding: '3px 10px', cursor: 'pointer', fontSize: 12 }}>
                  {acc.email}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
