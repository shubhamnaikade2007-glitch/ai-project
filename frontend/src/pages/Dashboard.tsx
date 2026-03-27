// HealthFit AI - Dashboard Page
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useHealth } from '../hooks/useHealth';
import HealthService from '../services/health.service';
import AppointmentService from '../services/appointment.service';
import { Appointment, OrganHealthScore } from '../types';

const s: Record<string, React.CSSProperties> = {
  page:       { fontFamily: "'Segoe UI', system-ui, sans-serif" },
  greeting:   { fontSize: 24, fontWeight: 700, color: '#1a202c', marginBottom: 4 },
  sub:        { fontSize: 14, color: '#718096', marginBottom: 28 },
  grid4:      { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 18, marginBottom: 24 },
  grid2:      { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 },
  grid3:      { display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 },
  card:       { background: '#fff', borderRadius: 16, padding: '20px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' },
  statCard:   { background: '#fff', borderRadius: 16, padding: '20px', boxShadow: '0 1px 4px rgba(0,0,0,0.06)', borderLeft: '4px solid #4ade80' },
  statVal:    { fontSize: 32, fontWeight: 800, color: '#1a202c', lineHeight: 1 },
  statLabel:  { fontSize: 12, color: '#718096', marginTop: 6, fontWeight: 500, textTransform: 'uppercase', letterSpacing: 0.5 },
  statChange: { fontSize: 12, marginTop: 8, fontWeight: 600 },
  sectionTitle: { fontSize: 16, fontWeight: 700, color: '#1a202c', marginBottom: 16 },
  metricRow:  { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid #f7fafc' },
  metricLabel: { fontSize: 14, color: '#4a5568' },
  metricVal:  { fontSize: 14, fontWeight: 600, color: '#1a202c' },
  badge:      { padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 600 },
  organGrid:  { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10 },
  organCard:  { background: '#f7fafc', borderRadius: 12, padding: '12px 14px' },
  organName:  { fontSize: 12, color: '#718096', fontWeight: 500, textTransform: 'capitalize', marginBottom: 6 },
  organScore: { fontSize: 22, fontWeight: 800 },
  progressBar: { height: 6, borderRadius: 3, background: '#e2e8f0', overflow: 'hidden', marginTop: 6 },
  apptCard:   { background: '#f0fff4', borderRadius: 12, padding: '14px 16px', marginBottom: 10, borderLeft: '3px solid #4ade80' },
  apptDate:   { fontSize: 12, color: '#276749', fontWeight: 600, marginBottom: 4 },
  apptDoc:    { fontSize: 14, color: '#1a202c', fontWeight: 600 },
  apptReason: { fontSize: 12, color: '#718096', marginTop: 2 },
  quickBtn:   { padding: '10px 20px', borderRadius: 10, border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8, transition: 'opacity 0.15s' },
  alertCard:  { display: 'flex', alignItems: 'flex-start', gap: 12, padding: '12px 14px', borderRadius: 10, marginBottom: 8 },
};

const ORGAN_ICONS: Record<string, string> = {
  heart: '❤️', liver: '🫁', kidneys: '🫘', lungs: '🫁',
  brain: '🧠', immune_system: '🛡️', digestive: '🌿', overall: '⭐',
};

const getRiskColor = (level: string) => {
  return { low: '#22c55e', moderate: '#f59e0b', high: '#ef4444', critical: '#7c3aed' }[level] || '#718096';
};

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user }  = useAuth();
  const { summary, latestMetrics, organScores, loading } = useHealth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [apptLoading, setApptLoading]   = useState(true);

  useEffect(() => {
    AppointmentService.getAppointments({ upcoming_only: true, limit: 3 })
      .then(d => setAppointments(d.appointments))
      .catch(() => {})
      .finally(() => setApptLoading(false));
  }, []);

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  const statCards = [
    {
      label: 'Heart Rate',
      value: latestMetrics['heart_rate'] ? `${latestMetrics['heart_rate'].value} bpm` : '—',
      icon: '❤️',
      color: '#fee2e2',
      border: '#ef4444',
      status: latestMetrics['heart_rate']?.status,
    },
    {
      label: 'Blood Pressure',
      value: latestMetrics['blood_pressure_systolic']
        ? `${latestMetrics['blood_pressure_systolic'].value}/${latestMetrics['blood_pressure_diastolic']?.value ?? '?'}`
        : '—',
      icon: '🩺',
      color: '#dbeafe',
      border: '#3b82f6',
      status: latestMetrics['blood_pressure_systolic']?.status,
    },
    {
      label: 'BMI',
      value: latestMetrics['bmi'] ? latestMetrics['bmi'].value.toFixed(1) : '—',
      icon: '⚖️',
      color: '#fef3c7',
      border: '#f59e0b',
      status: latestMetrics['bmi']?.status,
    },
    {
      label: 'Blood Glucose',
      value: latestMetrics['blood_glucose'] ? `${latestMetrics['blood_glucose'].value} mg/dL` : '—',
      icon: '🩸',
      color: '#d1fae5',
      border: '#10b981',
      status: latestMetrics['blood_glucose']?.status,
    },
  ];

  const keyMetrics = [
    { label: 'Oxygen Saturation', key: 'oxygen_saturation', unit: '%' },
    { label: 'Sleep (last night)', key: 'sleep_hours', unit: 'hrs' },
    { label: 'Steps Today',        key: 'steps_count', unit: '' },
    { label: 'Stress Level',       key: 'stress_level', unit: '/10' },
    { label: 'Body Temperature',   key: 'body_temperature', unit: '°C' },
    { label: 'Weight',             key: 'weight', unit: 'kg' },
  ];

  const overallScore = organScores.find(s => s.organ === 'overall');

  return (
    <div style={s.page}>
      {/* Greeting */}
      <div style={s.greeting}>{greeting}, {user?.first_name}! 👋</div>
      <div style={s.sub}>
        Here's your health overview for today. {loading && '(Loading…)'}
      </div>

      {/* Overall health score banner */}
      {overallScore && (
        <div style={{ ...s.card, marginBottom: 24, background: `linear-gradient(135deg, #0f2027, #2c5364)`, color: '#fff', display: 'flex', alignItems: 'center', gap: 24 }}>
          <div>
            <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.6)', marginBottom: 4 }}>OVERALL HEALTH SCORE</div>
            <div style={{ fontSize: 56, fontWeight: 900, color: '#4ade80', lineHeight: 1 }}>{overallScore.score.toFixed(0)}</div>
            <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.7)', marginTop: 4 }}>/ 100 · Risk: {overallScore.risk_level}</div>
          </div>
          <div style={{ flex: 1, borderLeft: '1px solid rgba(255,255,255,0.15)', paddingLeft: 24 }}>
            <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.6)', marginBottom: 8 }}>AI RECOMMENDATIONS</div>
            <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.85)', lineHeight: 1.7 }}>
              {overallScore.recommendations || 'Keep up your current healthy lifestyle. Continue monitoring your vitals regularly.'}
            </div>
          </div>
        </div>
      )}

      {/* Vital stat cards */}
      <div style={s.grid4}>
        {statCards.map(({ label, value, icon, color, border, status }) => (
          <div key={label} style={{ ...s.statCard, borderLeftColor: border, background: color }}>
            <div style={{ fontSize: 26, marginBottom: 8 }}>{icon}</div>
            <div style={s.statVal}>{value}</div>
            <div style={s.statLabel}>{label}</div>
            {status && (
              <div style={{
                ...s.badge,
                marginTop: 8,
                display: 'inline-block',
                background: status === 'normal' ? '#dcfce7' : '#fee2e2',
                color: status === 'normal' ? '#16a34a' : '#dc2626',
              }}>
                {status === 'normal' ? '✓ Normal' : `⚠ ${status}`}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Middle row */}
      <div style={s.grid3}>
        {/* Key metrics list */}
        <div style={s.card}>
          <div style={s.sectionTitle}>📊 All Vitals</div>
          {keyMetrics.map(({ label, key, unit }) => {
            const m = latestMetrics[key];
            return (
              <div key={key} style={s.metricRow}>
                <span style={s.metricLabel}>{label}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={s.metricVal}>{m ? `${m.value}${unit}` : '—'}</span>
                  {m?.status && (
                    <span style={{
                      ...s.badge,
                      background: m.status === 'normal' ? '#dcfce7' : '#fee2e2',
                      color: m.status === 'normal' ? '#16a34a' : '#dc2626',
                    }}>
                      {m.status}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
          <button onClick={() => navigate('/health')}
            style={{ ...s.quickBtn, marginTop: 16, background: '#f0fff4', color: '#166534', width: '100%', justifyContent: 'center' }}>
            ➕ Add New Reading
          </button>
        </div>

        {/* Right column: organ scores + appointments */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Organ scores */}
          <div style={s.card}>
            <div style={s.sectionTitle}>🫀 Organ Health</div>
            <div style={s.organGrid}>
              {organScores.filter(o => o.organ !== 'overall').slice(0, 6).map(score => (
                <div key={score.organ} style={s.organCard}>
                  <div style={s.organName}>{ORGAN_ICONS[score.organ]} {score.organ.replace('_', ' ')}</div>
                  <div style={{ ...s.organScore, color: getRiskColor(score.risk_level) }}>
                    {score.score.toFixed(0)}
                  </div>
                  <div style={s.progressBar}>
                    <div style={{ height: '100%', width: `${score.score}%`, background: getRiskColor(score.risk_level), borderRadius: 3, transition: 'width 0.5s' }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Upcoming appointments */}
          <div style={s.card}>
            <div style={s.sectionTitle}>📅 Upcoming Appointments</div>
            {apptLoading ? (
              <div style={{ color: '#718096', fontSize: 14 }}>Loading…</div>
            ) : appointments.length === 0 ? (
              <div style={{ color: '#718096', fontSize: 14 }}>No upcoming appointments.</div>
            ) : (
              appointments.map(appt => (
                <div key={appt.id} style={s.apptCard}>
                  <div style={s.apptDate}>
                    📅 {new Date(appt.appointment_date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })} at {appt.appointment_time?.slice(0, 5)}
                  </div>
                  <div style={s.apptDoc}>Dr. {appt.doctor_name}</div>
                  <div style={s.apptReason}>{appt.reason}</div>
                </div>
              ))
            )}
            <button onClick={() => navigate('/appointments')}
              style={{ ...s.quickBtn, marginTop: 8, background: '#eff6ff', color: '#1d4ed8', fontSize: 12 }}>
              📅 Book Appointment
            </button>
          </div>
        </div>
      </div>

      {/* Quick actions row */}
      <div style={{ ...s.card, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#4a5568', alignSelf: 'center', marginRight: 8 }}>Quick Actions:</div>
        {[
          { label: '🩺 Log Vitals',         path: '/health',      bg: '#f0fff4', color: '#166534' },
          { label: '🥗 Log Meal',            path: '/nutrition',   bg: '#fefce8', color: '#713f12' },
          { label: '💪 Log Workout',         path: '/fitness',     bg: '#eff6ff', color: '#1e3a8a' },
          { label: '🤖 Get AI Insights',     path: '/ai-insights', bg: '#faf5ff', color: '#6b21a8' },
          { label: '📅 Book Appointment',    path: '/appointments', bg: '#fff1f2', color: '#9f1239' },
        ].map(({ label, path, bg, color }) => (
          <button key={path} onClick={() => navigate(path)}
            style={{ ...s.quickBtn, background: bg, color }}>
            {label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
