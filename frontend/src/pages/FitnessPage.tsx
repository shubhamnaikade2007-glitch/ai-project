// HealthFit AI - Fitness Page
import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const s: Record<string, React.CSSProperties> = {
  page:       { fontFamily: "'Segoe UI', system-ui, sans-serif" },
  title:      { fontSize: 22, fontWeight: 700, color: '#1a202c', marginBottom: 4 },
  sub:        { fontSize: 14, color: '#718096', marginBottom: 24 },
  grid:       { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 },
  card:       { background: '#fff', borderRadius: 16, padding: '22px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)', marginBottom: 24 },
  sTitle:     { fontSize: 15, fontWeight: 700, color: '#1a202c', marginBottom: 16 },
  label:      { fontSize: 12, fontWeight: 600, color: '#4a5568', marginBottom: 5, display: 'block', marginTop: 12 },
  input:      { width: '100%', padding: '10px 12px', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 14, boxSizing: 'border-box' as const },
  row2:       { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 },
  row3:       { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10 },
  row4:       { display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10 },
  btn:        { padding: '10px 20px', borderRadius: 8, border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 14 },
  btnPrimary: { background: '#3b82f6', color: '#fff' },
  statBox:    { textAlign: 'center' as const, padding: '16px', background: '#f8fafc', borderRadius: 12 },
  statVal:    { fontSize: 28, fontWeight: 800, color: '#1a202c', lineHeight: 1 },
  statLabel:  { fontSize: 11, color: '#718096', marginTop: 4, textTransform: 'uppercase' as const, letterSpacing: 0.5 },
  workoutCard: { background: '#f8fafc', borderRadius: 10, padding: '14px', marginBottom: 10, borderLeft: '3px solid #3b82f6' },
  workoutTitle: { fontSize: 14, fontWeight: 700, color: '#1a202c', marginBottom: 6 },
  workoutMeta:  { display: 'flex', gap: 10, flexWrap: 'wrap' as const },
  metaTag:      { fontSize: 12, color: '#718096' },
  formScoreBadge: { padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 700, marginLeft: 8 },
  sleepCard:  { background: '#faf5ff', borderRadius: 10, padding: '14px', marginBottom: 10, borderLeft: '3px solid #8b5cf6' },
};

const WORKOUT_TYPES = ['running','walking','cycling','cardio','strength','hiit','yoga','swimming','sports','flexibility','other'];
const INTENSITIES   = ['low','moderate','high','extreme'];

const FitnessPage: React.FC = () => {
  const [workouts, setWorkouts]   = useState<any[]>([]);
  const [sleepRecs, setSleepRecs] = useState<any[]>([]);
  const [stats, setStats]         = useState<any>(null);
  const [loading, setLoading]     = useState(true);
  const [saving, setSaving]       = useState(false);
  const [msg, setMsg]             = useState('');
  const [tab, setTab]             = useState<'workouts'|'log'|'sleep'>('workouts');
  const [form, setForm]           = useState({
    workout_name:'', workout_type:'running', duration_min:'30', calories_burned:'',
    distance_km:'', heart_rate_avg:'', heart_rate_max:'', intensity:'moderate', notes:'',
  });
  const [sleepForm, setSleepForm] = useState({
    sleep_date: new Date().toISOString().split('T')[0],
    bedtime:'22:30', wake_time:'06:30', total_hours:'8', awakenings:'0',
    deep_sleep_pct:'20', rem_sleep_pct:'25', quality_rating:'good', notes:'',
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [wRes, stRes, slRes] = await Promise.all([
        api.get('/fitness/workouts', { params: { days: 30 } }),
        api.get('/fitness/stats', { params: { days: 30 } }),
        api.get('/fitness/sleep', { params: { days: 14 } }),
      ]);
      setWorkouts(wRes.data.workouts);
      setStats(stRes.data);
      setSleepRecs(slRes.data.sleep_records);
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const set  = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));
  const setS = (k: string, v: string) => setSleepForm(f => ({ ...f, [k]: v }));

  const handleLogWorkout = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true); setMsg('');
    try {
      await api.post('/fitness/workouts', {
        ...form,
        duration_min:   parseInt(form.duration_min),
        calories_burned: form.calories_burned ? parseInt(form.calories_burned) : undefined,
        distance_km:    form.distance_km     ? parseFloat(form.distance_km)    : undefined,
        heart_rate_avg: form.heart_rate_avg  ? parseInt(form.heart_rate_avg)   : undefined,
        heart_rate_max: form.heart_rate_max  ? parseInt(form.heart_rate_max)   : undefined,
      });
      setMsg('✅ Workout logged!');
      setForm({ workout_name:'', workout_type:'running', duration_min:'30', calories_burned:'', distance_km:'', heart_rate_avg:'', heart_rate_max:'', intensity:'moderate', notes:'' });
      await load();
      setTab('workouts');
    } catch (e: any) { setMsg('❌ ' + (e.response?.data?.error || 'Failed')); }
    setSaving(false);
  };

  const handleLogSleep = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true); setMsg('');
    try {
      await api.post('/fitness/sleep', {
        ...sleepForm,
        total_hours:    parseFloat(sleepForm.total_hours),
        awakenings:     parseInt(sleepForm.awakenings),
        deep_sleep_pct: parseFloat(sleepForm.deep_sleep_pct),
        rem_sleep_pct:  parseFloat(sleepForm.rem_sleep_pct),
      });
      setMsg('✅ Sleep logged!');
      await load();
    } catch (e: any) { setMsg('❌ ' + (e.response?.data?.error || 'Failed')); }
    setSaving(false);
  };

  const handleDeleteWorkout = async (id: number) => {
    if (!window.confirm('Delete workout?')) return;
    await api.delete(`/fitness/workouts/${id}`);
    await load();
  };

  const formScoreColor = (score?: number) => {
    if (!score) return { background:'#e2e8f0', color:'#4a5568' };
    if (score >= 90) return { background:'#d1fae5', color:'#065f46' };
    if (score >= 75) return { background:'#fef3c7', color:'#92400e' };
    return { background:'#fee2e2', color:'#991b1b' };
  };

  const sleepQualityColor = (q?: string) => {
    return { excellent:'#d1fae5', good:'#dbeafe', fair:'#fef3c7', poor:'#fee2e2' }[q as string] || '#f3f4f6';
  };

  return (
    <div style={s.page}>
      <div style={s.title}>💪 Fitness Tracker</div>
      <div style={s.sub}>Log workouts, track sleep, and monitor your progress</div>

      {/* Tabs */}
      <div style={{ display:'flex', gap:8, marginBottom:20 }}>
        {([['workouts','💪 Workouts'],['log','➕ Log Workout'],['sleep','😴 Sleep']] as const).map(([t,l]) => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding:'8px 18px', borderRadius:8, border:'none', cursor:'pointer', fontSize:13, fontWeight:600,
              background: tab===t ? '#3b82f6' : '#f7fafc', color: tab===t ? '#fff' : '#4a5568' }}>
            {l}
          </button>
        ))}
      </div>

      {/* Workouts tab */}
      {tab === 'workouts' && (
        <>
          {/* Stats row */}
          {stats && (
            <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:16, marginBottom:24 }}>
              {[
                { label:'Workouts',    val: stats.totals?.workouts ?? 0,                       unit:'' },
                { label:'Total Hours', val: Math.round((stats.totals?.minutes ?? 0) / 60 * 10)/10, unit:'hrs' },
                { label:'Calories',    val: Math.round(stats.totals?.calories ?? 0),            unit:'kcal' },
                { label:'Distance',    val: Math.round((stats.totals?.distance_km ?? 0)*10)/10, unit:'km' },
                { label:'Avg Form',    val: Math.round(stats.totals?.avg_form_score ?? 0),      unit:'/100' },
              ].map(({ label, val, unit }) => (
                <div key={label} style={s.statBox}>
                  <div style={s.statVal}>{val}<span style={{ fontSize:14, fontWeight:400, color:'#718096' }}>{unit}</span></div>
                  <div style={s.statLabel}>{label}</div>
                </div>
              ))}
            </div>
          )}

          {/* Workout list */}
          <div style={s.card}>
            <div style={s.sTitle}>📋 Recent Workouts (30 days)</div>
            {loading ? <div style={{color:'#718096'}}>Loading…</div>
              : workouts.length === 0
                ? <div style={{color:'#718096',fontSize:14}}>No workouts yet. <button onClick={()=>setTab('log')} style={{color:'#3b82f6',background:'none',border:'none',cursor:'pointer',fontWeight:600}}>Log one now →</button></div>
                : workouts.map((w:any) => (
                  <div key={w.id} style={s.workoutCard}>
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                      <div style={s.workoutTitle}>
                        {w.workout_name}
                        {w.form_score && (
                          <span style={{ ...s.formScoreBadge, ...formScoreColor(w.form_score) }}>
                            Form: {w.form_score.toFixed(0)}/100
                          </span>
                        )}
                      </div>
                      <button onClick={() => handleDeleteWorkout(w.id)}
                        style={{ background:'none', border:'none', cursor:'pointer', color:'#e53e3e', fontSize:16 }}>🗑</button>
                    </div>
                    <div style={s.workoutMeta}>
                      <span style={s.metaTag}>🏃 {w.workout_type}</span>
                      <span style={s.metaTag}>⏱ {w.duration_min} min</span>
                      {w.calories_burned && <span style={s.metaTag}>🔥 {w.calories_burned} kcal</span>}
                      {w.distance_km    && <span style={s.metaTag}>📏 {w.distance_km} km</span>}
                      {w.heart_rate_avg && <span style={s.metaTag}>❤️ avg {w.heart_rate_avg} bpm</span>}
                      <span style={s.metaTag}>💥 {w.intensity}</span>
                      <span style={s.metaTag}>📅 {new Date(w.started_at).toLocaleDateString('en-US',{month:'short',day:'numeric'})}</span>
                    </div>
                    {w.form_feedback && (
                      <div style={{ fontSize:12, color:'#4a5568', marginTop:8, padding:'8px', background:'#eff6ff', borderRadius:6 }}>
                        💡 {w.form_feedback}
                      </div>
                    )}
                  </div>
                ))
            }
          </div>
        </>
      )}

      {/* Log workout tab */}
      {tab === 'log' && (
        <div style={{ maxWidth:600 }}>
          <div style={s.card}>
            <div style={s.sTitle}>➕ Log Workout</div>
            <form onSubmit={handleLogWorkout}>
              <label style={s.label}>Workout Name *</label>
              <input style={s.input} placeholder="e.g. Morning run, Leg day"
                value={form.workout_name} onChange={e => set('workout_name', e.target.value)} required />

              <div style={{ ...s.row2, marginTop:12 }}>
                <div>
                  <label style={{ ...s.label, marginTop:0 }}>Type</label>
                  <select style={s.input} value={form.workout_type} onChange={e => set('workout_type', e.target.value)}>
                    {WORKOUT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ ...s.label, marginTop:0 }}>Intensity</label>
                  <select style={s.input} value={form.intensity} onChange={e => set('intensity', e.target.value)}>
                    {INTENSITIES.map(i => <option key={i} value={i}>{i}</option>)}
                  </select>
                </div>
              </div>

              <div style={{ ...s.row3, marginTop:12 }}>
                <div>
                  <label style={{ ...s.label, marginTop:0 }}>Duration (min) *</label>
                  <input style={s.input} type="number" value={form.duration_min} onChange={e => set('duration_min', e.target.value)} required />
                </div>
                <div>
                  <label style={{ ...s.label, marginTop:0 }}>Calories</label>
                  <input style={s.input} type="number" placeholder="kcal"
                    value={form.calories_burned} onChange={e => set('calories_burned', e.target.value)} />
                </div>
                <div>
                  <label style={{ ...s.label, marginTop:0 }}>Distance (km)</label>
                  <input style={s.input} type="number" step="0.01"
                    value={form.distance_km} onChange={e => set('distance_km', e.target.value)} />
                </div>
              </div>

              <div style={{ ...s.row2, marginTop:12 }}>
                <div>
                  <label style={{ ...s.label, marginTop:0 }}>Avg HR (bpm)</label>
                  <input style={s.input} type="number"
                    value={form.heart_rate_avg} onChange={e => set('heart_rate_avg', e.target.value)} />
                </div>
                <div>
                  <label style={{ ...s.label, marginTop:0 }}>Max HR (bpm)</label>
                  <input style={s.input} type="number"
                    value={form.heart_rate_max} onChange={e => set('heart_rate_max', e.target.value)} />
                </div>
              </div>

              <label style={s.label}>Notes</label>
              <textarea style={{ ...s.input, height:70, resize:'vertical' as const }}
                value={form.notes} onChange={e => set('notes', e.target.value)} />

              <button type="submit" style={{ ...s.btn, ...s.btnPrimary, marginTop:16, width:'100%' }} disabled={saving}>
                {saving ? 'Saving…' : '💪 Save Workout'}
              </button>
            </form>
            {msg && <div style={{ marginTop:10, fontSize:13, color: msg.startsWith('✅')?'#166534':'#dc2626' }}>{msg}</div>}
          </div>
        </div>
      )}

      {/* Sleep tab */}
      {tab === 'sleep' && (
        <div style={s.grid}>
          {/* Log sleep */}
          <div style={s.card}>
            <div style={s.sTitle}>😴 Log Sleep</div>
            <form onSubmit={handleLogSleep}>
              <label style={s.label}>Date</label>
              <input style={s.input} type="date" value={sleepForm.sleep_date} onChange={e => setS('sleep_date', e.target.value)} required />
              <div style={s.row2}>
                <div><label style={s.label}>Bedtime</label><input style={s.input} type="time" value={sleepForm.bedtime} onChange={e => setS('bedtime', e.target.value)} /></div>
                <div><label style={s.label}>Wake Time</label><input style={s.input} type="time" value={sleepForm.wake_time} onChange={e => setS('wake_time', e.target.value)} /></div>
              </div>
              <div style={s.row2}>
                <div><label style={s.label}>Total Hours</label><input style={s.input} type="number" step="0.25" value={sleepForm.total_hours} onChange={e => setS('total_hours', e.target.value)} /></div>
                <div><label style={s.label}>Awakenings</label><input style={s.input} type="number" value={sleepForm.awakenings} onChange={e => setS('awakenings', e.target.value)} /></div>
              </div>
              <div style={s.row2}>
                <div><label style={s.label}>Deep Sleep %</label><input style={s.input} type="number" step="0.1" value={sleepForm.deep_sleep_pct} onChange={e => setS('deep_sleep_pct', e.target.value)} /></div>
                <div><label style={s.label}>REM Sleep %</label><input style={s.input} type="number" step="0.1" value={sleepForm.rem_sleep_pct} onChange={e => setS('rem_sleep_pct', e.target.value)} /></div>
              </div>
              <label style={s.label}>Quality</label>
              <select style={s.input} value={sleepForm.quality_rating} onChange={e => setS('quality_rating', e.target.value)}>
                {['poor','fair','good','excellent'].map(q => <option key={q} value={q}>{q}</option>)}
              </select>
              <button type="submit" style={{ ...s.btn, background:'#8b5cf6', color:'#fff', marginTop:16, width:'100%' }} disabled={saving}>
                {saving ? 'Saving…' : '😴 Save Sleep Record'}
              </button>
            </form>
            {msg && <div style={{ marginTop:10, fontSize:13, color: msg.startsWith('✅')?'#166534':'#dc2626' }}>{msg}</div>}
          </div>

          {/* Sleep history */}
          <div style={s.card}>
            <div style={s.sTitle}>📊 Sleep History (14 days)</div>
            {sleepRecs.length === 0
              ? <div style={{color:'#718096',fontSize:14}}>No sleep records yet.</div>
              : sleepRecs.map((r:any) => (
                <div key={r.id} style={{ ...s.sleepCard, background: sleepQualityColor(r.quality_rating) }}>
                  <div style={{ display:'flex', justifyContent:'space-between' }}>
                    <strong style={{ fontSize:14 }}>{r.sleep_date}</strong>
                    <span style={{ fontSize:13, color:'#6b7280' }}>{r.quality_rating}</span>
                  </div>
                  <div style={{ display:'flex', gap:16, marginTop:6, fontSize:13, color:'#4a5568' }}>
                    <span>⏰ {r.total_hours}h</span>
                    {r.deep_sleep_pct && <span>🌊 {r.deep_sleep_pct}% deep</span>}
                    {r.rem_sleep_pct  && <span>💭 {r.rem_sleep_pct}% REM</span>}
                    {r.awakenings     && <span>🌙 {r.awakenings} wakes</span>}
                    {r.sleep_score    && <span>⭐ {r.sleep_score.toFixed(0)}/100</span>}
                  </div>
                </div>
              ))
            }
          </div>
        </div>
      )}
    </div>
  );
};

export default FitnessPage;
