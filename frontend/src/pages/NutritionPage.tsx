// HealthFit AI - Nutrition Page
import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const s: Record<string, React.CSSProperties> = {
  page:       { fontFamily: "'Segoe UI', system-ui, sans-serif" },
  title:      { fontSize: 22, fontWeight: 700, color: '#1a202c', marginBottom: 4 },
  sub:        { fontSize: 14, color: '#718096', marginBottom: 24 },
  grid:       { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 },
  card:       { background: '#fff', borderRadius: 16, padding: '22px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)' },
  sTitle:     { fontSize: 15, fontWeight: 700, color: '#1a202c', marginBottom: 16 },
  label:      { fontSize: 12, fontWeight: 600, color: '#4a5568', marginBottom: 5, display: 'block', marginTop: 12 },
  input:      { width: '100%', padding: '10px 12px', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 14, boxSizing: 'border-box' as const },
  row2:       { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 },
  row4:       { display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10 },
  btn:        { padding: '10px 20px', borderRadius: 8, border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 14 },
  btnPrimary: { background: '#4ade80', color: '#14532d' },
  mealCard:   { background: '#f8fafc', borderRadius: 10, padding: '14px', marginBottom: 10 },
  mealTitle:  { fontSize: 14, fontWeight: 700, color: '#1a202c', marginBottom: 4 },
  mealMeta:   { display: 'flex', gap: 10, flexWrap: 'wrap' as const },
  mealTag:    { fontSize: 12, color: '#718096', display: 'flex', alignItems: 'center', gap: 3 },
  progBar:    { height: 8, borderRadius: 4, background: '#e2e8f0', overflow: 'hidden', marginTop: 4 },
  progFill:   { height: '100%', borderRadius: 4, transition: 'width 0.5s' },
  recCard:    { background: '#f0fff4', borderRadius: 12, padding: '16px', marginBottom: 12, borderLeft: '3px solid #4ade80' },
  recTitle:   { fontSize: 14, fontWeight: 700, color: '#166534', marginBottom: 6 },
  recMsg:     { fontSize: 13, color: '#1a202c', lineHeight: 1.6 },
  deleteBtn:  { float: 'right' as const, background: 'none', border: 'none', cursor: 'pointer', color: '#e53e3e', fontSize: 16 },
};

const MEAL_TYPES = ['breakfast','lunch','dinner','snack','pre_workout','post_workout'];
const TYPE_COLORS: Record<string,string> = {
  breakfast:'#fef3c7', lunch:'#d1fae5', dinner:'#dbeafe',
  snack:'#fce7f3', pre_workout:'#ede9fe', post_workout:'#ecfdf5',
};

const NutritionPage: React.FC = () => {
  const [meals, setMeals]           = useState<any[]>([]);
  const [summary, setSummary]       = useState<any>(null);
  const [recs, setRecs]             = useState<any[]>([]);
  const [loading, setLoading]       = useState(true);
  const [saving, setSaving]         = useState(false);
  const [msg, setMsg]               = useState('');
  const [tab, setTab]               = useState<'log'|'today'|'recs'>('today');
  const [form, setForm]             = useState({
    meal_name:'', meal_type:'breakfast', calories:'', protein_g:'',
    carbohydrates_g:'', fat_g:'', fiber_g:'', serving_size:'',
  });

  const today = new Date().toISOString().split('T')[0];

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [mRes, sRes, rRes] = await Promise.all([
        api.get('/nutrition/meals', { params: { days: 7 } }),
        api.get('/nutrition/daily-summary', { params: { date: today } }),
        api.get('/nutrition/recommendations'),
      ]);
      setMeals(mRes.data.meals);
      setSummary(sRes.data);
      setRecs(rRes.data.recommendations);
    } catch {}
    setLoading(false);
  }, [today]);

  useEffect(() => { load(); }, [load]);

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  const handleLog = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.meal_name) return;
    setSaving(true); setMsg('');
    try {
      await api.post('/nutrition/meals', {
        ...form,
        calories:       form.calories       ? parseInt(form.calories)       : undefined,
        protein_g:      form.protein_g      ? parseFloat(form.protein_g)    : undefined,
        carbohydrates_g:form.carbohydrates_g? parseFloat(form.carbohydrates_g):undefined,
        fat_g:          form.fat_g          ? parseFloat(form.fat_g)        : undefined,
        fiber_g:        form.fiber_g        ? parseFloat(form.fiber_g)      : undefined,
      });
      setMsg('✅ Meal logged!');
      setForm({ meal_name:'', meal_type:'breakfast', calories:'', protein_g:'', carbohydrates_g:'', fat_g:'', fiber_g:'', serving_size:'' });
      await load();
    } catch (e: any) { setMsg('❌ ' + (e.response?.data?.error || 'Failed')); }
    setSaving(false);
  };

  const handleDelete = async (id: number) => {
    await api.delete(`/nutrition/meals/${id}`);
    await load();
  };

  const totals = summary?.totals ?? {};
  const targets = summary?.targets ?? { calories:2000, protein:150, carbs:250, fat:65, fiber:25 };
  const completion = summary?.completion ?? {};

  return (
    <div style={s.page}>
      <div style={s.title}>🥗 Nutrition Tracker</div>
      <div style={s.sub}>Log meals, track macros, and get AI-powered food recommendations</div>

      {/* Tabs */}
      <div style={{ display:'flex', gap:8, marginBottom:20 }}>
        {([['today','📊 Today','#fef9c3','#713f12'],['log','➕ Log Meal','#f0fff4','#166534'],['recs','🤖 AI Tips','#f0f9ff','#1e40af']] as const).map(([t,l,bg,col]) => (
          <button key={t} onClick={() => setTab(t as any)}
            style={{ padding:'8px 18px', borderRadius:8, border:'none', cursor:'pointer', fontSize:13, fontWeight:600,
              background: tab === t ? bg : '#f7fafc', color: tab === t ? col : '#4a5568' }}>
            {l}
          </button>
        ))}
      </div>

      {/* Today tab */}
      {tab === 'today' && (
        <>
          {/* Macro progress bars */}
          <div style={{ ...s.card, marginBottom:24 }}>
            <div style={s.sTitle}>📊 Today's Nutrition — {today}</div>
            {loading ? <div style={{color:'#718096'}}>Loading…</div> : (
              <div style={s.row4}>
                {[
                  { label:'Calories', key:'calories', color:'#f59e0b', unit:'kcal' },
                  { label:'Protein',  key:'protein',  color:'#3b82f6', unit:'g' },
                  { label:'Carbs',    key:'carbs',    color:'#10b981', unit:'g' },
                  { label:'Fat',      key:'fat',      color:'#ef4444', unit:'g' },
                ].map(({ label, key, color, unit }) => {
                  const val = totals[key] ?? 0;
                  const target = targets[key] ?? 1;
                  const pct = Math.min(val / target * 100, 100);
                  return (
                    <div key={key} style={{ textAlign:'center' as const }}>
                      <div style={{ fontSize:24, fontWeight:800, color }}>{Math.round(val)}</div>
                      <div style={{ fontSize:11, color:'#718096', marginBottom:6 }}>{label} ({unit})</div>
                      <div style={s.progBar}>
                        <div style={{ ...s.progFill, width:`${pct}%`, background:color }} />
                      </div>
                      <div style={{ fontSize:11, color:'#a0aec0', marginTop:4 }}>{Math.round(pct)}% of {target}{unit}</div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Today's meals */}
          <div style={s.card}>
            <div style={s.sTitle}>🍽️ Today's Meals</div>
            {meals.filter(m => m.logged_at?.startsWith(today)).length === 0
              ? <div style={{color:'#718096',fontSize:14}}>No meals logged today. <button onClick={()=>setTab('log')} style={{color:'#4ade80',background:'none',border:'none',cursor:'pointer',fontWeight:600}}>Log one now →</button></div>
              : meals.filter(m => m.logged_at?.startsWith(today)).map((meal: any) => (
                <div key={meal.id} style={{ ...s.mealCard, borderLeft:`3px solid ${TYPE_COLORS[meal.meal_type] ?? '#e2e8f0'}` }}>
                  <button style={s.deleteBtn} onClick={() => handleDelete(meal.id)}>🗑</button>
                  <div style={s.mealTitle}>{meal.meal_name}</div>
                  <div style={s.mealMeta}>
                    <span style={s.mealTag}>🍽 {meal.meal_type}</span>
                    {meal.calories && <span style={s.mealTag}>🔥 {meal.calories} kcal</span>}
                    {meal.protein_g && <span style={s.mealTag}>💪 {meal.protein_g}g protein</span>}
                    {meal.carbohydrates_g && <span style={s.mealTag}>🌾 {meal.carbohydrates_g}g carbs</span>}
                    {meal.fat_g && <span style={s.mealTag}>🧈 {meal.fat_g}g fat</span>}
                  </div>
                </div>
              ))
            }
          </div>
        </>
      )}

      {/* Log meal tab */}
      {tab === 'log' && (
        <div style={{ maxWidth: 600 }}>
          <div style={s.card}>
            <div style={s.sTitle}>➕ Log a Meal</div>
            <form onSubmit={handleLog}>
              <label style={s.label}>Meal Name *</label>
              <input style={s.input} placeholder="e.g. Grilled chicken with quinoa"
                value={form.meal_name} onChange={e => set('meal_name', e.target.value)} required />

              <label style={s.label}>Meal Type</label>
              <select style={s.input} value={form.meal_type} onChange={e => set('meal_type', e.target.value)}>
                {MEAL_TYPES.map(t => <option key={t} value={t}>{t.replace('_',' ')}</option>)}
              </select>

              <label style={s.label}>Calories (kcal)</label>
              <input style={s.input} type="number" placeholder="e.g. 420"
                value={form.calories} onChange={e => set('calories', e.target.value)} />

              <div style={{ marginTop: 12 }}>
                <label style={{ ...s.label, marginTop: 0 }}>Macros (grams)</label>
                <div style={s.row4}>
                  {[['protein_g','Protein'],['carbohydrates_g','Carbs'],['fat_g','Fat'],['fiber_g','Fiber']].map(([k,l]) => (
                    <div key={k}>
                      <label style={{ fontSize:11, color:'#718096', marginBottom:4, display:'block' }}>{l}</label>
                      <input style={s.input} type="number" step="0.1" placeholder="0"
                        value={(form as any)[k]} onChange={e => set(k, e.target.value)} />
                    </div>
                  ))}
                </div>
              </div>

              <label style={s.label}>Serving Size</label>
              <input style={s.input} placeholder="e.g. 200g, 1 cup"
                value={form.serving_size} onChange={e => set('serving_size', e.target.value)} />

              <button type="submit" style={{ ...s.btn, ...s.btnPrimary, marginTop:16, width:'100%' }} disabled={saving}>
                {saving ? 'Saving…' : '🥗 Save Meal'}
              </button>
            </form>
            {msg && <div style={{ marginTop:10, fontSize:13, color: msg.startsWith('✅')?'#166534':'#dc2626' }}>{msg}</div>}
          </div>
        </div>
      )}

      {/* AI Recommendations tab */}
      {tab === 'recs' && (
        <div>
          {recs.length === 0
            ? <div style={{ color:'#718096' }}>Loading recommendations…</div>
            : recs.map((rec: any, i) => (
              <div key={i} style={{ ...s.recCard, borderLeftColor: rec.priority==='high'?'#ef4444':rec.priority==='medium'?'#f59e0b':'#4ade80' }}>
                <div style={s.recTitle}>
                  {rec.priority === 'high' ? '🚨' : rec.priority === 'medium' ? '⚠️' : '💡'} {rec.title}
                </div>
                <div style={s.recMsg}>{rec.message}</div>
                {rec.suggestions && (
                  <ul style={{ margin:'8px 0 0', paddingLeft:18, fontSize:13, color:'#4a5568' }}>
                    {rec.suggestions.map((s: string, j: number) => <li key={j}>{s}</li>)}
                  </ul>
                )}
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
};

export default NutritionPage;
