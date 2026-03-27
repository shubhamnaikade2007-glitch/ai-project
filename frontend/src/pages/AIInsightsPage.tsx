// HealthFit AI - AI Insights Page
import React, { useState, useEffect } from 'react';
import api from '../services/api';

const s: Record<string, React.CSSProperties> = {
  page:       { fontFamily: "'Segoe UI', system-ui, sans-serif" },
  title:      { fontSize: 22, fontWeight: 700, color: '#1a202c', marginBottom: 4 },
  sub:        { fontSize: 14, color: '#718096', marginBottom: 24 },
  grid:       { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 },
  card:       { background: '#fff', borderRadius: 16, padding: '22px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)', marginBottom: 24 },
  sTitle:     { fontSize: 15, fontWeight: 700, color: '#1a202c', marginBottom: 16 },
  resultCard: { borderRadius: 12, padding: '20px', marginBottom: 16 },
  riskLevel:  { fontSize: 36, fontWeight: 900, lineHeight: 1 },
  riskLabel:  { fontSize: 12, color: '#718096', marginTop: 4, textTransform: 'uppercase' as const, letterSpacing: 0.5 },
  alertItem:  { display: 'flex', alignItems: 'flex-start', gap: 10, padding: '10px 0', borderBottom: '1px solid rgba(0,0,0,0.05)' },
  recItem:    { display: 'flex', alignItems: 'flex-start', gap: 10, padding: '8px 0', fontSize: 14, color: '#2d3748', borderBottom: '1px solid #f7fafc' },
  btn:        { padding: '11px 24px', borderRadius: 10, border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 14, transition: 'opacity 0.15s' },
  btnPrimary: { background: 'linear-gradient(135deg, #7c3aed, #6d28d9)', color: '#fff' },
  input:      { width: '100%', padding: '10px 12px', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 14, boxSizing: 'border-box' as const },
  label:      { fontSize: 12, fontWeight: 600, color: '#4a5568', marginBottom: 5, display: 'block', marginTop: 12 },
  row3:       { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10 },
  histCard:   { background: '#f8fafc', borderRadius: 10, padding: '12px 14px', marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
};

const RISK_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  low:      { bg: '#f0fff4', text: '#16a34a', border: '#4ade80' },
  moderate: { bg: '#fefce8', text: '#b45309', border: '#fbbf24' },
  high:     { bg: '#fff1f2', text: '#dc2626', border: '#f87171' },
  critical: { bg: '#faf5ff', text: '#7c3aed', border: '#a78bfa' },
};

const AIInsightsPage: React.FC = () => {
  const [tab, setTab]             = useState<'risk'|'sleep'|'stress'|'history'>('risk');
  const [loading, setLoading]     = useState(false);
  const [history, setHistory]     = useState<any[]>([]);
  const [riskResult, setRiskResult]   = useState<any>(null);
  const [sleepResult, setSleepResult] = useState<any>(null);
  const [stressResult, setStressResult] = useState<any>(null);

  const [overrides, setOverrides] = useState({
    bmi:'', systolic:'', diastolic:'', glucose:'', heart_rate:'',
  });
  const [stressForm, setStressForm] = useState({
    hrv_ms:'45', resting_hr:'70', sleep_score:'75',
    sleep_hours:'7', activity_minutes:'30', subjective_stress:'5',
  });

  const setO = (k: string, v: string) => setOverrides(f => ({ ...f, [k]: v }));
  const setF = (k: string, v: string) => setStressForm(f => ({ ...f, [k]: v }));

  useEffect(() => {
    api.get('/ai/history').then(r => setHistory(r.data.predictions)).catch(() => {});
  }, []);

  const runRiskPrediction = async () => {
    setLoading(true); setRiskResult(null);
    try {
      const payload: any = {};
      if (overrides.bmi)        payload.bmi       = parseFloat(overrides.bmi);
      if (overrides.systolic)   payload.systolic  = parseFloat(overrides.systolic);
      if (overrides.diastolic)  payload.diastolic = parseFloat(overrides.diastolic);
      if (overrides.glucose)    payload.glucose   = parseFloat(overrides.glucose);
      if (overrides.heart_rate) payload.heart_rate = parseFloat(overrides.heart_rate);
      const res = await api.post('/ai/predict-risk', payload);
      setRiskResult(res.data.prediction);
    } catch (e: any) {
      setRiskResult({ error: e.response?.data?.error || 'Prediction failed' });
    }
    setLoading(false);
  };

  const runSleepAnalysis = async () => {
    setLoading(true); setSleepResult(null);
    try {
      const res = await api.post('/ai/analyze-sleep', {});
      setSleepResult(res.data.analysis);
    } catch (e: any) {
      setSleepResult({ error: e.response?.data?.error || 'Analysis failed' });
    }
    setLoading(false);
  };

  const runStressDetection = async () => {
    setLoading(true); setStressResult(null);
    try {
      const payload = {
        hrv_ms:           parseFloat(stressForm.hrv_ms),
        resting_hr:       parseFloat(stressForm.resting_hr),
        sleep_score:      parseFloat(stressForm.sleep_score),
        sleep_hours:      parseFloat(stressForm.sleep_hours),
        activity_minutes: parseFloat(stressForm.activity_minutes),
        subjective_stress: parseFloat(stressForm.subjective_stress),
      };
      const res = await api.post('/ai/detect-stress', payload);
      setStressResult(res.data.analysis);
    } catch (e: any) {
      setStressResult({ error: e.response?.data?.error || 'Detection failed' });
    }
    setLoading(false);
  };

  const renderRiskBadge = (level: string) => {
    const colors = RISK_COLORS[level] || RISK_COLORS.low;
    return (
      <span style={{ padding:'4px 14px', borderRadius:20, fontSize:13, fontWeight:700,
        background: colors.bg, color: colors.text, border:`1px solid ${colors.border}` }}>
        {level?.toUpperCase()}
      </span>
    );
  };

  return (
    <div style={s.page}>
      <div style={s.title}>🤖 AI Health Insights</div>
      <div style={s.sub}>AI-powered predictions for health risk, sleep quality, and stress detection</div>

      {/* Tabs */}
      <div style={{ display:'flex', gap:8, marginBottom:24 }}>
        {([
          ['risk',   '🫀 Risk Prediction'],
          ['sleep',  '😴 Sleep Analysis'],
          ['stress', '😤 Stress Detection'],
          ['history','📋 History'],
        ] as const).map(([t, l]) => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding:'8px 18px', borderRadius:8, border:'none', cursor:'pointer', fontSize:13, fontWeight:600,
              background: tab===t ? '#7c3aed' : '#f7fafc', color: tab===t ? '#fff' : '#4a5568' }}>
            {l}
          </button>
        ))}
      </div>

      {/* ─── RISK PREDICTION ─────────────────────────────── */}
      {tab === 'risk' && (
        <div style={s.grid}>
          <div style={s.card}>
            <div style={s.sTitle}>🫀 Health Risk Prediction</div>
            <p style={{ fontSize:13, color:'#718096', marginBottom:16 }}>
              Our AI automatically pulls your latest health metrics. You can override specific values below for a custom scenario analysis.
            </p>
            <div style={s.row3}>
              {[['bmi','BMI'],['systolic','Systolic BP'],['diastolic','Diastolic BP'],['glucose','Blood Glucose'],['heart_rate','Heart Rate']].map(([k,l]) => (
                <div key={k}>
                  <label style={s.label}>{l} (override)</label>
                  <input style={s.input} type="number" step="0.1" placeholder="From your data"
                    value={(overrides as any)[k]} onChange={e => setO(k, e.target.value)} />
                </div>
              ))}
            </div>
            <button onClick={runRiskPrediction} disabled={loading}
              style={{ ...s.btn, ...s.btnPrimary, marginTop:16, width:'100%', opacity: loading ? 0.6 : 1 }}>
              {loading ? '🤖 Analyzing…' : '🤖 Run Risk Analysis'}
            </button>
            <button onClick={async () => {
              try {
                await api.post('/smartwatch/sync-now');
                alert('✅ Smartwatch data synced! Check Health tab.');
              } catch(e) { alert('Connect Fitbit first: /smartwatch/fitbit/auth') }
            }} style={{...s.btn, background:'#10b981', color:'white', marginTop:8, width:'100%'}}>
              🔄 Sync Smartwatch (Fitbit)
            </button>
          </div>

          {/* Result */}
          {riskResult && (
            <div>
              {riskResult.error ? (
                <div style={{ ...s.card, color:'#dc2626' }}>❌ {riskResult.error}</div>
              ) : (
                <>
                  <div style={{ ...s.card,
                    background: RISK_COLORS[riskResult.risk_level]?.bg ?? '#f0fff4',
                    borderLeft: `5px solid ${RISK_COLORS[riskResult.risk_level]?.border ?? '#4ade80'}` }}>
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
                      <div>
                        <div style={{ ...s.riskLevel, color: RISK_COLORS[riskResult.risk_level]?.text }}>
                          {riskResult.risk_score?.toFixed(1)}
                        </div>
                        <div style={s.riskLabel}>Overall Risk Score</div>
                      </div>
                      {renderRiskBadge(riskResult.risk_level)}
                    </div>
                    {riskResult.confidence && (
                      <div style={{ fontSize:12, color:'#718096', marginTop:12 }}>
                        Model confidence: {riskResult.confidence}%
                        {riskResult.model && ` · Model: ${riskResult.model}`}
                      </div>
                    )}
                  </div>

                  {/* Disease breakdown */}
                  {riskResult.disease_risks && (
                    <div style={s.card}>
                      <div style={s.sTitle}>📊 Risk Breakdown by Condition</div>
                      {Object.entries(riskResult.disease_risks).map(([disease, score]: [string, any]) => (
                        <div key={disease} style={{ marginBottom:12 }}>
                          <div style={{ display:'flex', justifyContent:'space-between', fontSize:13, marginBottom:4 }}>
                            <span style={{ color:'#4a5568', textTransform:'capitalize' }}>{disease.replace('_',' ')}</span>
                            <span style={{ fontWeight:700, color: score>50?'#dc2626':score>25?'#f59e0b':'#16a34a' }}>{score}%</span>
                          </div>
                          <div style={{ height:6, borderRadius:3, background:'#e2e8f0', overflow:'hidden' }}>
                            <div style={{ height:'100%', width:`${score}%`, borderRadius:3, transition:'width 0.5s',
                              background: score>50?'#ef4444':score>25?'#f59e0b':'#4ade80' }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Alerts */}
                  {riskResult.alerts?.length > 0 && (
                    <div style={{ ...s.card, background:'#fff5f5', borderLeft:'4px solid #f87171' }}>
                      <div style={{ ...s.sTitle, color:'#dc2626' }}>⚠️ Health Alerts</div>
                      {riskResult.alerts.map((a: string, i: number) => (
                        <div key={i} style={s.alertItem}><span>⚠️</span><span style={{ fontSize:13 }}>{a}</span></div>
                      ))}
                    </div>
                  )}

                  {/* Recommendations */}
                  {riskResult.recommendations?.length > 0 && (
                    <div style={s.card}>
                      <div style={s.sTitle}>💡 AI Recommendations</div>
                      {riskResult.recommendations.map((r: string, i: number) => (
                        <div key={i} style={s.recItem}><span>✓</span><span>{r}</span></div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          )}
          {!riskResult && <div style={{ ...s.card, color:'#718096', display:'flex', alignItems:'center', justifyContent:'center', flexDirection:'column', gap:12, minHeight:200 }}>
            <span style={{ fontSize:40 }}>🤖</span>
            <span style={{ fontSize:14 }}>Click "Run Risk Analysis" to get your personalized health risk assessment</span>
          </div>}
        </div>
      )}

      {/* ─── SLEEP ANALYSIS ──────────────────────────────── */}
      {tab === 'sleep' && (
        <div style={s.grid}>
          <div style={s.card}>
            <div style={s.sTitle}>😴 Sleep Pattern Analysis</div>
            <p style={{ fontSize:13, color:'#718096', marginBottom:20 }}>
              Analyzes your last 14 nights of sleep data from the Fitness tracker to identify patterns and issues.
            </p>
            <div style={{ background:'#f0fff4', padding:'14px', borderRadius:10, fontSize:13, color:'#166534', marginBottom:16 }}>
              💡 Make sure to log your sleep records in the Fitness section first for accurate analysis.
            </div>
            <button onClick={runSleepAnalysis} disabled={loading}
              style={{ ...s.btn, background:'#8b5cf6', color:'#fff', width:'100%', opacity: loading ? 0.6 : 1 }}>
              {loading ? '🤖 Analyzing sleep…' : '😴 Analyze My Sleep'}
            </button>
          </div>

          {sleepResult && (
            <div>
              {sleepResult.error
                ? <div style={{ ...s.card, color:'#dc2626' }}>❌ {sleepResult.error}</div>
                : <>
                  <div style={{ ...s.card, background:'#faf5ff', borderLeft:'5px solid #8b5cf6' }}>
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
                      <div>
                        <div style={{ fontSize:40, fontWeight:900, color:'#6d28d9', lineHeight:1 }}>
                          {sleepResult.quality_score?.toFixed(0)}
                        </div>
                        <div style={s.riskLabel}>Sleep Quality Score / 100</div>
                      </div>
                      <span style={{ padding:'4px 12px', borderRadius:20, fontSize:13, fontWeight:700,
                        background:'#ede9fe', color:'#6d28d9' }}>
                        {sleepResult.quality_rating}
                      </span>
                    </div>
                    <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:12, marginTop:16 }}>
                      {[
                        { label:'Avg Hours',    val: sleepResult.averages?.total_hours?.toFixed(1) + 'h' },
                        { label:'Deep Sleep',   val: sleepResult.averages?.deep_sleep_pct?.toFixed(1) + '%' },
                        { label:'REM Sleep',    val: sleepResult.averages?.rem_sleep_pct?.toFixed(1)  + '%' },
                        { label:'Awakenings',   val: sleepResult.averages?.awakenings?.toFixed(1) + '/night' },
                        { label:'Consistency',  val: sleepResult.consistency_score?.toFixed(0) + '/100' },
                        { label:'Sleep Debt',   val: sleepResult.sleep_debt_hours + 'h' },
                      ].map(({ label, val }) => (
                        <div key={label} style={{ textAlign:'center' as const }}>
                          <div style={{ fontSize:18, fontWeight:700 }}>{val}</div>
                          <div style={{ fontSize:11, color:'#718096' }}>{label}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                  {sleepResult.issues?.length > 0 && (
                    <div style={{ ...s.card, background:'#fff7ed' }}>
                      <div style={{ ...s.sTitle, color:'#c2410c' }}>⚠️ Detected Issues</div>
                      {sleepResult.issues.map((i: string, idx: number) => (
                        <div key={idx} style={s.alertItem}><span>⚠️</span><span style={{ fontSize:13 }}>{i}</span></div>
                      ))}
                    </div>
                  )}
                  <div style={s.card}>
                    <div style={s.sTitle}>💡 Sleep Recommendations</div>
                    {sleepResult.recommendations?.map((r: string, i: number) => (
                      <div key={i} style={s.recItem}><span>✓</span><span>{r}</span></div>
                    ))}
                    {sleepResult.recommended_bedtime && (
                      <div style={{ marginTop:12, padding:'10px', background:'#f0fff4', borderRadius:8, fontSize:13, color:'#166534' }}>
                        🌙 Recommended bedtime: <strong>{sleepResult.recommended_bedtime}</strong>
                      </div>
                    )}
                  </div>
                </>
              }
            </div>
          )}
          {!sleepResult && <div style={{ ...s.card, color:'#718096', display:'flex', alignItems:'center', justifyContent:'center', flexDirection:'column', gap:12, minHeight:200 }}>
            <span style={{ fontSize:40 }}>😴</span>
            <span style={{ fontSize:14 }}>Analyze your sleep patterns for personalized recommendations</span>
          </div>}
        </div>
      )}

      {/* ─── STRESS DETECTION ────────────────────────────── */}
      {tab === 'stress' && (
        <div style={s.grid}>
          <div style={s.card}>
            <div style={s.sTitle}>😤 Stress Level Detection</div>
            <p style={{ fontSize:13, color:'#718096', marginBottom:8 }}>Enter your current biometrics for a stress level estimation.</p>
            <div style={s.row3}>
              {[['hrv_ms','HRV (ms)'],['resting_hr','Resting HR (bpm)'],['sleep_score','Sleep Score'],
                ['sleep_hours','Sleep Hours'],['activity_minutes','Active Min'],['subjective_stress','Felt Stress (0-10)']].map(([k,l]) => (
                <div key={k}>
                  <label style={s.label}>{l}</label>
                  <input style={s.input} type="number" step="0.1"
                    value={(stressForm as any)[k]} onChange={e => setF(k, e.target.value)} />
                </div>
              ))}
            </div>
            <button onClick={runStressDetection} disabled={loading}
              style={{ ...s.btn, background:'#f59e0b', color:'#fff', marginTop:16, width:'100%', opacity: loading ? 0.6 : 1 }}>
              {loading ? '🤖 Detecting…' : '😤 Detect Stress Level'}
            </button>
          </div>

          {stressResult && (
            <div>
              {stressResult.error
                ? <div style={{ ...s.card, color:'#dc2626' }}>❌ {stressResult.error}</div>
                : <>
                  <div style={{ ...s.card, background:'#fefce8', borderLeft:'5px solid #fbbf24' }}>
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
                      <div>
                        <div style={{ fontSize:40, fontWeight:900, color:'#b45309', lineHeight:1 }}>
                          {stressResult.stress_score?.toFixed(1)} {stressResult.emoji}
                        </div>
                        <div style={s.riskLabel}>Stress Score / 100</div>
                      </div>
                      <span style={{ padding:'4px 12px', borderRadius:20, fontSize:13, fontWeight:700,
                        background:'#fef3c7', color:'#92400e', textTransform:'capitalize' as const }}>
                        {stressResult.stress_category}
                      </span>
                    </div>
                    {stressResult.hrv_note && (
                      <div style={{ marginTop:12, fontSize:13, color:'#78350f', padding:'8px', background:'rgba(255,255,255,0.5)', borderRadius:8 }}>
                        💓 {stressResult.hrv_note}
                      </div>
                    )}
                  </div>
                  {stressResult.primary_triggers?.length > 0 && (
                    <div style={s.card}>
                      <div style={s.sTitle}>🎯 Primary Stress Triggers</div>
                      <div style={{ display:'flex', gap:8, flexWrap:'wrap' as const }}>
                        {stressResult.primary_triggers.map((t: string) => (
                          <span key={t} style={{ padding:'4px 12px', borderRadius:20, background:'#fef3c7', color:'#92400e', fontSize:13, fontWeight:600 }}>
                            {t.replace(/_/g,' ')}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  <div style={s.card}>
                    <div style={s.sTitle}>💡 Stress Reduction Tips</div>
                    {stressResult.recommendations?.map((r: string, i: number) => (
                      <div key={i} style={s.recItem}><span>✓</span><span>{r}</span></div>
                    ))}
                  </div>
                </>
              }
            </div>
          )}
          {!stressResult && <div style={{ ...s.card, color:'#718096', display:'flex', alignItems:'center', justifyContent:'center', flexDirection:'column', gap:12, minHeight:200 }}>
            <span style={{ fontSize:40 }}>😤</span>
            <span style={{ fontSize:14 }}>Enter your biometrics to estimate your stress level</span>
          </div>}
        </div>
      )}

      {/* ─── HISTORY ─────────────────────────────────────── */}
      {tab === 'history' && (
        <div style={s.card}>
          <div style={s.sTitle}>📋 Prediction History</div>
          {history.length === 0
            ? <div style={{ color:'#718096', fontSize:14 }}>No AI predictions yet. Run an analysis to get started.</div>
            : history.map((h: any) => (
              <div key={h.id} style={s.histCard}>
                <div>
                  <div style={{ fontSize:14, fontWeight:600, color:'#1a202c', textTransform:'capitalize' }}>
                    {h.prediction_type?.replace(/_/g,' ')}
                  </div>
                  <div style={{ fontSize:12, color:'#718096', marginTop:2 }}>
                    {new Date(h.predicted_at).toLocaleString('en-US', { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' })}
                  </div>
                </div>
                <div style={{ display:'flex', alignItems:'center', gap:10 }}>
                  <span style={{ fontSize:16, fontWeight:700 }}>{h.risk_score?.toFixed(1) ?? '—'}</span>
                  {h.risk_level && renderRiskBadge(h.risk_level)}
                </div>
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
};

export default AIInsightsPage;
