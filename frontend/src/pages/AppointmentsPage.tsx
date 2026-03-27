// HealthFit AI - Appointments Page
import React, { useState, useEffect } from 'react';
import AppointmentService from '../services/appointment.service';
import { Appointment, Doctor } from '../types';

const s: Record<string, React.CSSProperties> = {
  page:      { fontFamily: "'Segoe UI', system-ui, sans-serif" },
  title:     { fontSize: 22, fontWeight: 700, color: '#1a202c', marginBottom: 4 },
  sub:       { fontSize: 14, color: '#718096', marginBottom: 24 },
  grid:      { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 },
  card:      { background: '#fff', borderRadius: 16, padding: '22px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)', marginBottom: 24 },
  sTitle:    { fontSize: 15, fontWeight: 700, color: '#1a202c', marginBottom: 16 },
  label:     { fontSize: 12, fontWeight: 600, color: '#4a5568', marginBottom: 5, display: 'block', marginTop: 12 },
  input:     { width: '100%', padding: '10px 12px', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 14, boxSizing: 'border-box' as const, outline: 'none' },
  btn:       { padding: '10px 20px', borderRadius: 8, border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 14 },
  btnPrimary: { background: '#2c5364', color: '#fff' },
  apptCard:  { background: '#f8fafc', borderRadius: 12, padding: '16px', marginBottom: 12, borderLeft: '4px solid #4ade80', position: 'relative' as const },
  apptHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 },
  apptTitle:  { fontSize: 15, fontWeight: 700, color: '#1a202c' },
  apptDate:   { fontSize: 13, color: '#4ade80', fontWeight: 600 },
  apptMeta:   { display: 'flex', gap: 10, flexWrap: 'wrap' as const, marginTop: 6 },
  tag:        { padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 600, background: '#e2e8f0', color: '#4a5568' },
  slotGrid:   { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, marginTop: 8 },
  slotBtn:    { padding: '8px', border: '1px solid #e2e8f0', borderRadius: 8, cursor: 'pointer', fontSize: 13, textAlign: 'center' as const, fontWeight: 500 },
  slotSel:    { background: '#2c5364', color: '#fff', borderColor: '#2c5364' },
  docCard:    { display: 'flex', gap: 12, padding: '12px', background: '#f8fafc', borderRadius: 10, marginBottom: 8, cursor: 'pointer', border: '2px solid transparent', transition: 'border-color 0.15s' },
  docAvatar:  { width: 44, height: 44, borderRadius: '50%', background: '#c7d2fe', color: '#3730a3', fontWeight: 700, fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
  docName:    { fontSize: 14, fontWeight: 600, color: '#1a202c' },
  docSpec:    { fontSize: 12, color: '#718096', marginTop: 2 },
  docMeta:    { fontSize: 12, color: '#4a5568', marginTop: 4, display: 'flex', gap: 10 },
  statusBadge: { padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700 },
};

const STATUS_COLORS: Record<string, React.CSSProperties> = {
  pending:   { background: '#fef3c7', color: '#b45309' },
  confirmed: { background: '#d1fae5', color: '#065f46' },
  completed: { background: '#dbeafe', color: '#1e40af' },
  cancelled: { background: '#fee2e2', color: '#991b1b' },
  no_show:   { background: '#f3f4f6', color: '#6b7280' },
};

const AppointmentsPage: React.FC = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [doctors, setDoctors]           = useState<Doctor[]>([]);
  const [slots, setSlots]               = useState<string[]>([]);
  const [loading, setLoading]           = useState(true);
  const [saving, setSaving]             = useState(false);
  const [msg, setMsg]                   = useState('');
  const [tab, setTab]                   = useState<'upcoming'|'past'|'book'>('upcoming');
  const [form, setForm]                 = useState({
    doctor_id: '', appointment_date: '', appointment_time: '',
    type: 'in_person', reason: '',
  });

  const load = async () => {
    setLoading(true);
    try {
      const [aData, dData] = await Promise.all([
        AppointmentService.getAppointments({ limit: 50 }),
        AppointmentService.getDoctors(),
      ]);
      setAppointments(aData.appointments);
      setDoctors(dData.doctors);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  // Load slots when doctor + date change
  useEffect(() => {
    if (form.doctor_id && form.appointment_date) {
      AppointmentService.getAvailableSlots(parseInt(form.doctor_id), form.appointment_date)
        .then(d => setSlots(d.available))
        .catch(() => setSlots([]));
    }
  }, [form.doctor_id, form.appointment_date]);

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  const handleBook = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.appointment_time) { setMsg('❌ Please select a time slot'); return; }
    setSaving(true); setMsg('');
    try {
      await AppointmentService.bookAppointment({
        doctor_id:        parseInt(form.doctor_id),
        appointment_date: form.appointment_date,
        appointment_time: form.appointment_time,
        type:             form.type as any,
        reason:           form.reason,
      });
      setMsg('✅ Appointment booked!');
      setForm({ doctor_id: '', appointment_date: '', appointment_time: '', type: 'in_person', reason: '' });
      setSlots([]);
      await load();
      setTab('upcoming');
    } catch (e: any) {
      setMsg('❌ ' + (e.response?.data?.error || 'Booking failed'));
    }
    setSaving(false);
  };

  const handleCancel = async (id: number) => {
    if (!window.confirm('Cancel this appointment?')) return;
    try {
      await AppointmentService.cancelAppointment(id);
      setMsg('Appointment cancelled.');
      await load();
    } catch {}
  };

  const upcoming = appointments.filter(a => a.is_upcoming && a.status !== 'cancelled');
  const past      = appointments.filter(a => !a.is_upcoming || a.status === 'completed' || a.status === 'cancelled');

  const today = new Date().toISOString().split('T')[0];

  return (
    <div style={s.page}>
      <div style={s.title}>📅 Appointments</div>
      <div style={s.sub}>Schedule and manage your doctor consultations</div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {([['upcoming', '📅 Upcoming'], ['past', '📋 Past'], ['book', '➕ Book New']] as const).map(([t, l]) => (
          <button key={t} onClick={() => setTab(t)} style={{
            padding: '8px 18px', borderRadius: 8, border: 'none', cursor: 'pointer',
            fontSize: 13, fontWeight: 600,
            background: tab === t ? '#2c5364' : '#f7fafc',
            color: tab === t ? '#fff' : '#4a5568',
          }}>{l}</button>
        ))}
      </div>

      {msg && (
        <div style={{ padding: '10px 16px', borderRadius: 8, marginBottom: 16, fontSize: 13,
          background: msg.startsWith('✅') ? '#f0fff4' : '#fff5f5',
          color: msg.startsWith('✅') ? '#166534' : '#dc2626' }}>
          {msg}
        </div>
      )}

      {/* Upcoming tab */}
      {tab === 'upcoming' && (
        <div>
          {loading ? <div style={{ color: '#718096' }}>Loading…</div>
            : upcoming.length === 0
              ? <div style={{ ...s.card, color: '#718096', textAlign: 'center', padding: 40 }}>
                  No upcoming appointments. <button onClick={() => setTab('book')} style={{ color: '#2c5364', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}>Book one now →</button>
                </div>
              : upcoming.map(appt => (
                <div key={appt.id} style={{ ...s.apptCard, borderLeftColor: '#4ade80' }}>
                  <div style={s.apptHeader}>
                    <div>
                      <div style={s.apptTitle}>{appt.doctor_name || 'Doctor'}</div>
                      <div style={s.apptDate}>
                        📅 {new Date(appt.appointment_date + 'T00:00:00').toLocaleDateString('en-US', {weekday:'long',month:'long',day:'numeric'})} at {appt.appointment_time?.slice(0,5)}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                      <span style={{ ...s.statusBadge, ...STATUS_COLORS[appt.status] }}>{appt.status}</span>
                      <button onClick={() => handleCancel(appt.id)}
                        style={{ padding: '4px 12px', borderRadius: 6, border: '1px solid #e53e3e', color: '#e53e3e', background: 'none', cursor: 'pointer', fontSize: 12 }}>
                        Cancel
                      </button>
                    </div>
                  </div>
                  <div style={s.apptMeta}>
                    <span style={s.tag}>🏥 {appt.type?.replace('_',' ')}</span>
                    <span style={s.tag}>⏱ {appt.duration_min} min</span>
                  </div>
                  {appt.reason && <div style={{ fontSize: 13, color: '#4a5568', marginTop: 8 }}>📝 {appt.reason}</div>}
                </div>
              ))
          }
        </div>
      )}

      {/* Past tab */}
      {tab === 'past' && (
        <div>
          {past.length === 0
            ? <div style={{ color: '#718096', fontSize: 14 }}>No past appointments.</div>
            : past.map(appt => (
              <div key={appt.id} style={{ ...s.apptCard, borderLeftColor: '#e2e8f0' }}>
                <div style={s.apptHeader}>
                  <div>
                    <div style={s.apptTitle}>{appt.doctor_name || 'Doctor'}</div>
                    <div style={{ fontSize: 13, color: '#718096' }}>
                      {new Date(appt.appointment_date + 'T00:00:00').toLocaleDateString('en-US', {year:'numeric',month:'short',day:'numeric'})} · {appt.appointment_time?.slice(0,5)}
                    </div>
                  </div>
                  <span style={{ ...s.statusBadge, ...STATUS_COLORS[appt.status] }}>{appt.status}</span>
                </div>
                {appt.diagnosis && <div style={{ fontSize: 13, color: '#4a5568', marginTop: 8 }}>🩺 <strong>Diagnosis:</strong> {appt.diagnosis}</div>}
                {appt.prescription && <div style={{ fontSize: 13, color: '#4a5568', marginTop: 4 }}>💊 <strong>Prescription:</strong> {appt.prescription}</div>}
              </div>
            ))
          }
        </div>
      )}

      {/* Book tab */}
      {tab === 'book' && (
        <div style={s.grid}>
          {/* Doctor list */}
          <div style={s.card}>
            <div style={s.sTitle}>👨‍⚕️ Choose a Doctor</div>
            {doctors.map(doc => (
              <div key={doc.id} onClick={() => set('doctor_id', String(doc.user_id))}
                style={{ ...s.docCard, borderColor: form.doctor_id === String(doc.user_id) ? '#2c5364' : 'transparent' }}>
                <div style={s.docAvatar}>{doc.name?.split(' ').slice(-1)[0]?.[0] ?? 'D'}</div>
                <div style={{ flex: 1 }}>
                  <div style={s.docName}>{doc.name}</div>
                  <div style={s.docSpec}>{doc.specialization}</div>
                  <div style={s.docMeta}>
                    <span>⭐ {doc.rating}</span>
                    <span>💼 {doc.years_experience}y exp</span>
                    <span>💵 ${doc.consultation_fee}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Booking form */}
          <div style={s.card}>
            <div style={s.sTitle}>📋 Booking Details</div>
            <form onSubmit={handleBook}>
              <label style={s.label}>Date</label>
              <input style={s.input} type="date" min={today}
                value={form.appointment_date} onChange={e => set('appointment_date', e.target.value)} required />

              {slots.length > 0 && (
                <>
                  <label style={s.label}>Available Time Slots</label>
                  <div style={s.slotGrid}>
                    {slots.map(slot => (
                      <button key={slot} type="button"
                        onClick={() => set('appointment_time', slot)}
                        style={{ ...s.slotBtn, ...(form.appointment_time === slot ? s.slotSel : {}) }}>
                        {slot}
                      </button>
                    ))}
                  </div>
                </>
              )}

              <label style={s.label}>Appointment Type</label>
              <select style={s.input} value={form.type} onChange={e => set('type', e.target.value)}>
                <option value="in_person">In Person</option>
                <option value="video_call">Video Call</option>
                <option value="phone">Phone</option>
              </select>

              <label style={s.label}>Reason for Visit</label>
              <textarea style={{ ...s.input, height: 80, resize: 'vertical' as const }}
                placeholder="Describe your concern…"
                value={form.reason} onChange={e => set('reason', e.target.value)} />

              <button type="submit"
                style={{ ...s.btn, ...s.btnPrimary, marginTop: 16, width: '100%' }}
                disabled={saving || !form.doctor_id || !form.appointment_date || !form.appointment_time}>
                {saving ? 'Booking…' : '📅 Confirm Booking'}
              </button>
            </form>
            {msg && (
              <div style={{ marginTop: 12, fontSize: 13,
                color: msg.startsWith('✅') ? '#166534' : '#dc2626' }}>
                {msg}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AppointmentsPage;
