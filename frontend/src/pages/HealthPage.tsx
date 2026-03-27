// HealthFit AI - Health Metrics Page
import React, { useState, useEffect } from 'react';
import HealthService from '../services/health.service';
import { HealthMetric } from '../types';

const METRIC_TYPES = [
  { value: 'heart_rate',               label: 'Heart Rate',            unit: 'bpm',   icon: '❤️' },
  { value: 'blood_pressure_systolic',  label: 'Systolic BP',           unit: 'mmHg',  icon: '🩺' },
  { value: 'blood_pressure_diastolic', label: 'Diastolic BP',          unit: 'mmHg',  icon: '🩺' },
  { value: 'blood_glucose',            label: 'Blood Glucose',         unit: 'mg/dL', icon: '🩸' },
  { value: 'body_temperature',         label: 'Temperature',           unit: '°C',    icon: '🌡️' },
  { value: 'oxygen_saturation',        label: 'O₂ Saturation',         unit: '%',     icon: '💨' },
  { value: 'bmi',                      label: 'BMI',                   unit: 'kg/m²', icon: '⚖️' },
  { value: 'weight',                   label: 'Weight',                unit: 'kg',    icon: '🏋️' },
  { value: 'sleep_hours',              label: 'Sleep Hours',           unit: 'hrs',   icon: '😴' },
  { value: 'stress_level',             label: 'Stress Level',          unit: '/10',   icon: '😤' },
  { value: 'steps_count',              label: 'Daily Steps',           unit: 'steps', icon: '👟' },
  { value: 'water_intake_ml',          label: 'Water Intake',          unit: 'ml',    icon: '💧' },
  { value: 'cholesterol_total',        label: 'Total Cholesterol',     unit: 'mg/dL', icon: '🧪' },
  { value: 'body_fat_percentage',      label: 'Body Fat %',            unit: '%',     icon: '📐' },
];

const NORMAL_RANGES: Record<string, {min?: number; max?: number}> = {
  heart_rate: {min:60,max:100}, blood_pressure_systolic: {min:90,max:120},
  blood_pressure_diastolic: {min:60,max:80}, blood_glucose: {min:70,max:100},
  body_temperature: {min:36.1,max:37.2}, oxygen_saturation: {min:95,max:100},
  bmi: {min:18.5,max:24.9}, sleep_hours: {min:7,max:9},
  stress_level: {min:0,max:4}, steps_count: {min:7500},
};

const s: Record<string, React.CSSProperties> = {
  page:      { fontFamily: "'Segoe UI', system-ui, sans-serif" },
  header:    { marginBottom: 24 },
  title:     { fontSize: 22, fontWeight: 700, color: '#1a202c', marginBottom: 4 },
  sub:       { fontSize: 14, color: '#718096' },
  grid:      { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 },
  card:      { background: '#fff', borderRadius: 16, padding: '22px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)', marginBottom: 24 },
  sTitle:    { fontSize: 15, fontWeight: 700, color: '#1a202c', marginBottom: 16 },
  formRow:   { display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 12, alignItems: 'end', marginBottom: 12 },
  label:     { fontSize: 12, fontWeight: 600, color: '#4a5568', marginBottom: 5, display: 'block' },
  input:     { width: '100%', padding: '10px 12px', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 14, boxSizing: 'border-box' as const, outline: 'none' },
  btn:       { padding: '10px 18px', borderRadius: 8, border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 14 },
  btnPrimary: { background: '#2c5364', color: '#fff' },
  metricRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid #f7fafc' },
  metricName: { fontSize: 13, color: '#4a5568', display: 'flex', alignItems: 'center', gap: 6 },
  metricVal:  { display: 'flex', alignItems: 'center', gap: 8 },
  metricNum:  { fontSize: 16, fontWeight: 700, color: '#1a202c' },
  metricUnit: { fontSize: 12, color: '#718096' },
  badge:     { padding: '2px 8px', borderRadius: 10, fontSize: 11, fontWeight: 600 },
  metricTime: { fontSize: 11, color: '#a0aec0', marginLeft: 4 },
  tabs:      { display: 'flex', gap: 8, marginBottom: 20 },
  tab:       { padding: '7px 16px', borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 500 },
  tabActive: { background: '#2c5364', color: '#fff' },
  tabIdle:   { background: '#f7fafc', color: '#4a5568' },
  histRow:   { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 80px', gap: 8, padding: '9px 0', borderBottom: '1px solid #f7fafc', fontSize: 13, alignItems: 'center' },
  deleteBtn: { background: 'none', border: 'none', cursor: 'pointer', color: '#e53e3e', fontSize: 16, padding: '2px 6px' },
};

const getBadge = (status: string) => ({
  background: status === 'normal' ? '#dcfce7' : '#fee2e2',
  color: status === 'normal' ? '#16a34a' : '#dc2626',
});

const HealthPage: React.FC = () => {
  const [latest, setLatest]       = useState<Record<string, HealthMetric>>({});
  const [history, setHistory]     = useState<HealthMetric[]>([]);
  const [loading, setLoading]     = useState(true);
  const [saving, setSaving]       = useState(false);
  const [tab, setTab]             = useState<'latest'|'history'>('latest');
  const [filterType, setFilter]   = useState('');
  const [msg, setMsg]             = useState('');
  const [form, setForm]           = useState({ metric_type: 'heart_rate', value: '', source: 'manual' });

  const load = async () => {
    setLoading(true);
    try {
      const [lat, hist] = await Promise.all([
        HealthService.getLatestMetrics(),
        HealthService.getMetrics({ days: 30, limit: 100 }),
      ]);
      setLatest(lat.latest);
      setHistory(hist.metrics);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.value) return;
    setSaving(true); setMsg('');
    try {
      const meta = METRIC_TYPES.find(m => m.value === form.metric_type);
      await HealthService.addMetric({
        metric_type: form.metric_type,
        value: parseFloat(form.value),
        unit: meta?.unit,
        source: form.source as any,
      });
      setMsg('✅ Metric recorded!');
      setForm(f => ({ ...f, value: '' }));
      await load();
    } catch (e: any) {
      setMsg('❌ ' + (e.response?.data?.error || 'Failed to save'));
    }
    setSaving(false);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this reading?')) return;
    await HealthService.deleteMetric(id);
    await load();
  };

  const filteredHistory = filterType
    ? history.filter(m => m.metric_type === filterType)
    : history;

  return (
    <div style={s.page}>
      <div style={s.header}>
        <div style={s.title}>❤️ Health Metrics</div>
        <div style={s.sub}>Track and monitor all your health readings in one place</div>
      </div>

      <div style={s.grid}>
        {/* Add metric form */}
        <div style={s.card}>
          <div style={s.sTitle}>➕ Record New Reading</div>
          <form onSubmit={handleAdd}>
            <div style={s.formRow}>
              <div>
                <label style={s.label}>Metric Type</label>
                <select style={s.input} value={form.metric_type}
                  onChange={e => setForm(f => ({ ...f, metric_type: e.target.value }))}>
                  {METRIC_TYPES.map(m => (
                    <option key={m.value} value={m.value}>{m.icon} {m.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={s.label}>
                  Value ({METRIC_TYPES.find(m => m.value === form.metric_type)?.unit})
                </label>
                <input style={s.input} type="number" step="0.01" placeholder="0.00"
                  value={form.value} onChange={e => setForm(f => ({ ...f, value: e.target.value }))} required />
              </div>
              <div>
                <label style={s.label}>Source</label>
                <select style={s.input} value={form.source}
                  onChange={e => setForm(f => ({ ...f, source: e.target.value }))}>
                  <option value="manual">Manual</option>
                  <option value="wearable">Wearable</option>
                  <option value="device">Device</option>
                </select>
              </div>
            </div>
            {/* Normal range hint */}
            {NORMAL_RANGES[form.metric_type] && (
              <div style={{ fontSize: 12, color: '#718096', marginBottom: 12 }}>
                📏 Normal range: {NORMAL_RANGES[form.metric_type].min ?? '—'} – {NORMAL_RANGES[form.metric_type].max ?? '—'} {METRIC_TYPES.find(m => m.value === form.metric_type)?.unit}
              </div>
            )}
            <button type="submit" style={{ ...s.btn, ...s.btnPrimary }} disabled={saving}>
              {saving ? 'Saving…' : '💾 Save Reading'}
            </button>
            {msg && <div style={{ marginTop: 10, fontSize: 13, color: msg.startsWith('✅') ? '#16a34a' : '#dc2626' }}>{msg}</div>}
          </form>
        </div>

        {/* Latest readings */}
        <div style={s.card}>
          <div style={s.sTitle}>📊 Latest Readings</div>
          {loading ? (
            <div style={{ color: '#718096', fontSize: 14 }}>Loading…</div>
          ) : (
            METRIC_TYPES.map(({ value, label, icon, unit }) => {
              const m = latest[value];
              if (!m) return null;
              return (
                <div key={value} style={s.metricRow}>
                  <span style={s.metricName}>{icon} {label}</span>
                  <div style={s.metricVal}>
                    <span style={s.metricNum}>{m.value}</span>
                    <span style={s.metricUnit}>{unit}</span>
                    {m.status && (
                      <span style={{ ...s.badge, ...getBadge(m.status) }}>{m.status}</span>
                    )}
                    <span style={s.metricTime}>
                      {new Date(m.recorded_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* History table */}
      <div style={s.card}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div style={s.sTitle}>📋 Reading History (Last 30 Days)</div>
          <select style={{ ...s.input, width: 200, marginBottom: 0 }}
            value={filterType} onChange={e => setFilter(e.target.value)}>
            <option value="">All types</option>
            {METRIC_TYPES.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
          </select>
        </div>

        {/* Header */}
        <div style={{ ...s.histRow, fontWeight: 600, color: '#4a5568', borderBottom: '2px solid #e2e8f0' }}>
          <span>Metric</span><span>Value</span><span>Date / Source</span><span>Action</span>
        </div>

        {filteredHistory.length === 0 ? (
          <div style={{ padding: '20px 0', color: '#718096', fontSize: 14 }}>
            No readings found. Add your first reading above!
          </div>
        ) : (
          filteredHistory.map(m => {
            const meta = METRIC_TYPES.find(t => t.value === m.metric_type);
            return (
              <div key={m.id} style={s.histRow}>
                <span style={{ fontSize: 13, color: '#2d3748' }}>{meta?.icon} {meta?.label ?? m.metric_type}</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <strong>{m.value}</strong>
                  <span style={{ fontSize: 11, color: '#718096' }}>{m.unit}</span>
                  {m.status && (
                    <span style={{ ...s.badge, ...getBadge(m.status) }}>{m.status}</span>
                  )}
                </span>
                <span style={{ fontSize: 12, color: '#718096' }}>
                  {new Date(m.recorded_at).toLocaleString('en-US', {
                    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
                  })} · {m.source}
                </span>
                <button style={s.deleteBtn} onClick={() => handleDelete(m.id)} title="Delete">🗑</button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default HealthPage;
