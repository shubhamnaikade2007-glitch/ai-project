// HealthFit AI - Main Layout with Sidebar Navigation
import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

// Inline styles – no external CSS required, works out of the box
const styles: Record<string, React.CSSProperties> = {
  root:       { display: 'flex', minHeight: '100vh', fontFamily: "'Segoe UI', system-ui, sans-serif", background: '#f0f4f8' },
  sidebar:    { width: 240, background: 'linear-gradient(180deg, #0f2027 0%, #203a43 50%, #2c5364 100%)', color: '#fff', display: 'flex', flexDirection: 'column', flexShrink: 0 },
  sidebarCollapsed: { width: 64 },
  logo:       { padding: '24px 20px 16px', borderBottom: '1px solid rgba(255,255,255,0.1)' },
  logoText:   { fontSize: 20, fontWeight: 700, color: '#4ade80', letterSpacing: '-0.5px' },
  logoSub:    { fontSize: 11, color: 'rgba(255,255,255,0.5)', marginTop: 2 },
  nav:        { flex: 1, padding: '12px 0', overflowY: 'auto' },
  navSection: { padding: '8px 16px 4px', fontSize: 10, fontWeight: 600, color: 'rgba(255,255,255,0.35)', letterSpacing: 1, textTransform: 'uppercase' },
  navLink:    { display: 'flex', alignItems: 'center', gap: 12, padding: '10px 20px', color: 'rgba(255,255,255,0.7)', textDecoration: 'none', fontSize: 14, transition: 'all 0.15s', borderLeftWidth: '3px', borderLeftStyle: 'solid', borderLeftColor: 'transparent' },
  navLinkActive: { color: '#4ade80', background: 'rgba(74,222,128,0.1)', borderLeftColor: '#4ade80' },
  navLinkIcon:   { fontSize: 18, width: 20, textAlign: 'center' },
  userBox:    { padding: '16px 20px', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', gap: 12 },
  avatar:     { width: 36, height: 36, borderRadius: '50%', background: '#4ade80', color: '#0f2027', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 14, flexShrink: 0 },
  userName:   { fontSize: 13, fontWeight: 600, color: '#fff' },
  userRole:   { fontSize: 11, color: 'rgba(255,255,255,0.45)', textTransform: 'capitalize' },
  logoutBtn:  { marginLeft: 'auto', background: 'none', border: 'none', color: 'rgba(255,255,255,0.4)', cursor: 'pointer', fontSize: 18, padding: 4, lineHeight: 1 },
  main:       { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  topbar:     { background: '#fff', borderBottom: '1px solid #e2e8f0', padding: '0 28px', height: 60, display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0 },
  topbarTitle: { fontSize: 18, fontWeight: 600, color: '#1a202c' },
  topbarDate:  { marginLeft: 'auto', fontSize: 13, color: '#718096' },
  content:    { flex: 1, padding: 28, overflowY: 'auto' },
  badge:      { marginLeft: 'auto', background: '#fee2e2', color: '#dc2626', fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 10 },
};

const NAV_ITEMS = [
  { to: '/dashboard',    icon: '🏠', label: 'Dashboard',    section: 'MAIN' },
  { to: '/health',       icon: '❤️',  label: 'Health Metrics', section: 'MAIN' },
  { to: '/appointments', icon: '📅', label: 'Appointments', section: 'MAIN' },
  { to: '/nutrition',    icon: '🥗', label: 'Nutrition',    section: 'WELLNESS' },
  { to: '/fitness',      icon: '💪', label: 'Fitness',      section: 'WELLNESS' },
  { to: '/ai-insights',  icon: '🤖', label: 'AI Insights',  section: 'AI' },
  { to: '/profile',      icon: '👤', label: 'Profile',      section: 'ACCOUNT' },
];

const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  });

  // Group nav items by section
  const sections = NAV_ITEMS.reduce<Record<string, typeof NAV_ITEMS>>((acc, item) => {
    if (!acc[item.section]) acc[item.section] = [];
    acc[item.section].push(item);
    return acc;
  }, {});

  const initials = user ? `${user.first_name[0]}${user.last_name[0]}`.toUpperCase() : 'HF';

  return (
    <div style={styles.root}>
      {/* ── Sidebar ────────────────────────────────────── */}
      <aside style={{ ...styles.sidebar, ...(collapsed ? styles.sidebarCollapsed : {}) }}>
        {/* Logo */}
        <div style={styles.logo}>
          {!collapsed ? (
            <>
              <div style={styles.logoText}>🏃 HealthFit AI</div>
              <div style={styles.logoSub}>Intelligent Health Platform</div>
            </>
          ) : (
            <div style={{ ...styles.logoText, fontSize: 22 }}>🏃</div>
          )}
        </div>

        {/* Navigation */}
        <nav style={styles.nav}>
          {Object.entries(sections).map(([section, items]) => (
            <div key={section}>
              {!collapsed && <div style={styles.navSection}>{section}</div>}
              {items.map(({ to, icon, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  style={({ isActive }) => ({
                    ...styles.navLink,
    ...(isActive ? { ...styles.navLinkActive, borderLeftColor: '#4ade80' } : {}),
                  })}
                >
                  <span style={styles.navLinkIcon}>{icon}</span>
                  {!collapsed && <span>{label}</span>}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        {/* User box */}
        <div style={styles.userBox}>
          <div style={styles.avatar}>{initials}</div>
          {!collapsed && (
            <>
              <div>
                <div style={styles.userName}>{user?.first_name} {user?.last_name}</div>
                <div style={styles.userRole}>{user?.role}</div>
              </div>
              <button onClick={handleLogout} style={styles.logoutBtn} title="Logout">⎋</button>
            </>
          )}
        </div>
      </aside>

      {/* ── Main area ──────────────────────────────────── */}
      <div style={styles.main}>
        {/* Topbar */}
        <header style={styles.topbar}>
          <button
            onClick={() => setCollapsed(c => !c)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 20, color: '#718096', padding: 4 }}
            title="Toggle sidebar"
          >
            ☰
          </button>
          <span style={styles.topbarTitle}>HealthFit AI</span>
          <span style={styles.topbarDate}>{today}</span>
          <div style={{ marginLeft: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ ...styles.avatar, width: 32, height: 32, fontSize: 12 }}>{initials}</span>
            <span style={{ fontSize: 13, color: '#4a5568' }}>{user?.full_name}</span>
          </div>
        </header>

        {/* Page content */}
        <main style={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
