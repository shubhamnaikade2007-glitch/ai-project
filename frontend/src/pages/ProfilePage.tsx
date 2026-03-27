// HealthFit AI - Profile Page
import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import AuthService from '../services/auth.service';
import { setUser } from '../store/slices/authSlice';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../store/store';

const s: Record<string, React.CSSProperties> = {
  page: { fontFamily: "'Segoe UI', system-ui, sans-serif", maxWidth: 800 },
  title: { fontSize: 22, fontWeight: 700, color: '#1a202c', marginBottom: 4 },
  sub: { fontSize: 14, color: '#718096', marginBottom: 24 },
  card: { background: '#fff', borderRadius: 16, padding: '28px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)', marginBottom: 24 },
  sTitle: { fontSize: 15, fontWeight: 700, color: '#1a202c', marginBottom: 20 },
  grid2: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 },
  label: { fontSize: 12, fontWeight: 600, color: '#4a5568', marginBottom: 5, display: 'block', marginTop: 14 },
  input: { width: '100%', padding: '10px 12px', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 14, boxSizing: 'border-box' as const, outline: 'none' },
  btn: { padding: '11px 24px', borderRadius: 10, border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 14 },
  btnPrimary: { background: '#2c5364', color: '#fff' },
  avatar: { width: 72, height: 72, borderRadius: '50%', background: 'linear-gradient(135deg,#4ade80,#2c5364)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28, fontWeight: 700, flexShrink: 0 },
  msgBox: { padding: '10px 16px', borderRadius: 8, fontSize: 13, marginTop: 12 },
  infoRow: { display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #f7fafc', fontSize: 14 },
  infoLabel: { color: '#718096', fontWeight: 500 },
  infoVal: { color: '#1a202c', fontWeight: 600 },
};

const ProfilePage: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { user } = useAuth();

  const [profileForm, setProfileForm] = useState({
    first_name: user?.first_name ?? '',
    last_name: user?.last_name ?? '',
    phone: user?.phone ?? '',
    gender: user?.gender ?? '',
    date_of_birth: '',
    height_cm: user?.profile?.height_cm?.toString() ?? '',
    weight_kg: user?.profile?.weight_kg?.toString() ?? '',
    blood_type: user?.profile?.blood_type ?? '',
    fitness_goal: user?.profile?.fitness_goal ?? 'general_wellness',
    activity_level: user?.profile?.activity_level ?? 'moderately_active',
    allergies: user?.profile?.allergies ?? '',
    medications: user?.profile?.medications ?? '',
    emergency_contact_name: user?.profile?.emergency_contact_name ?? '',
    emergency_contact_phone: user?.profile?.emergency_contact_phone ?? '',
  });

  const [pwForm, setPwForm] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [saving, setSaving] = useState(false);
  const [pwSaving, setPwSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const [pwMsg, setPwMsg] = useState('');

  const setF = (k: string, v: string) => setProfileForm(f => ({ ...f, [k]: v }));
  const setPW = (k: string, v: string) => setPwForm(f => ({ ...f, [k]: v }));

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true); setMsg('');
    try {
      const updated = await AuthService.updateProfile({
        ...profileForm,
        gender: profileForm.gender as 'male' | 'female' | 'other' | undefined,
        height_cm: profileForm.height_cm ? parseFloat(profileForm.height_cm) : undefined,
        weight_kg: profileForm.weight_kg ? parseFloat(profileForm.weight_kg) : undefined,
      });
      dispatch(setUser(updated));
      setMsg('✅ Profile updated!');
    } catch (e: any) {
      setMsg('❌ ' + (e.response?.data?.error || 'Failed'));
    }
    setSaving(false);
  };

  const handlePw = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pwForm.new_password !== pwForm.confirm_password) { setPwMsg('❌ Passwords do not match'); return; }
    setPwSaving(true); setPwMsg('');
    try {
      await AuthService.changePassword(pwForm.current_password, pwForm.new_password);
      setPwMsg('✅ Password changed!');
      setPwForm({ current_password: '', new_password: '', confirm_password: '' });
    } catch (e: any) { setPwMsg('❌ ' + (e.response?.data?.error || 'Failed')); }
    setPwSaving(false);
  };

  const initials = user ? `${user.first_name[0]}${user.last_name[0]}`.toUpperCase() : 'HF';

  return (
    <div style={s.page}>
      <div style={s.title}>👤 My Profile</div>
      <div style={s.sub}>Manage your personal information and health settings</div>

      {/* Avatar + quick stats */}
      <div style={s.card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 24 }}>
          <div style={s.avatar}>{initials}</div>
          <div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{user?.full_name}</div>
            <div style={{ fontSize: 14, color: '#718096' }}>{user?.email}</div>
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <span style={{ padding: '3px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600, background: '#dbeafe', color: '#1e40af' }}>{user?.role}</span>
              {user?.profile?.blood_type && <span style={{ padding: '3px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600, background: '#fee2e2', color: '#991b1b' }}>Blood: {user.profile.blood_type}</span>}
            </div>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12 }}>
          {[
            ['Age', user?.age ? `${user.age}y` : '—'],
            ['Height', user?.profile?.height_cm ? `${user.profile.height_cm}cm` : '—'],
            ['Weight', user?.profile?.weight_kg ? `${user.profile.weight_kg}kg` : '—'],
            ['BMI', user?.profile?.bmi ? user.profile.bmi.toFixed(1) : '—'],
          ].map(([label, val]) => (
            <div key={label} style={{ background: '#f7fafc', borderRadius: 10, padding: '12px', textAlign: 'center' as const }}>
              <div style={{ fontSize: 20, fontWeight: 800 }}>{val}</div>
              <div style={{ fontSize: 11, color: '#718096', marginTop: 3 }}>{label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Edit form */}
      <div style={s.card}>
        <div style={s.sTitle}>✏️ Edit Profile</div>
        <form onSubmit={handleSave}>
          <div style={s.grid2}>
            <div><label style={s.label}>First Name</label><input style={s.input} value={profileForm.first_name} onChange={e => setF('first_name', e.target.value)} required /></div>
            <div><label style={s.label}>Last Name</label><input style={s.input} value={profileForm.last_name} onChange={e => setF('last_name', e.target.value)} required /></div>
            <div><label style={s.label}>Phone</label><input style={s.input} type="tel" value={profileForm.phone} onChange={e => setF('phone', e.target.value)} /></div>
            <div><label style={s.label}>Gender</label>
              <select style={s.input} value={profileForm.gender} onChange={e => setF('gender', e.target.value)}>
                <option value="">Select</option>
                <option value="male">Male</option><option value="female">Female</option><option value="other">Other</option>
              </select>
            </div>
            <div><label style={s.label}>Date of Birth</label><input style={s.input} type="date" value={profileForm.date_of_birth} onChange={e => setF('date_of_birth', e.target.value)} /></div>
            <div><label style={s.label}>Blood Type</label>
              <select style={s.input} value={profileForm.blood_type} onChange={e => setF('blood_type', e.target.value)}>
                <option value="">Unknown</option>
                {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div><label style={s.label}>Height (cm)</label><input style={s.input} type="number" step="0.1" value={profileForm.height_cm} onChange={e => setF('height_cm', e.target.value)} /></div>
            <div><label style={s.label}>Weight (kg)</label><input style={s.input} type="number" step="0.1" value={profileForm.weight_kg} onChange={e => setF('weight_kg', e.target.value)} /></div>
            <div><label style={s.label}>Fitness Goal</label>
              <select style={s.input} value={profileForm.fitness_goal} onChange={e => setF('fitness_goal', e.target.value)}>
                {[['weight_loss', 'Weight Loss'], ['muscle_gain', 'Muscle Gain'], ['endurance', 'Endurance'], ['flexibility', 'Flexibility'], ['general_wellness', 'General Wellness']].map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>
            <div><label style={s.label}>Activity Level</label>
              <select style={s.input} value={profileForm.activity_level} onChange={e => setF('activity_level', e.target.value)}>
                {[['sedentary', 'Sedentary'], ['lightly_active', 'Lightly Active'], ['moderately_active', 'Moderately Active'], ['very_active', 'Very Active'], ['extra_active', 'Extra Active']].map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>
            <div><label style={s.label}>Allergies</label><textarea style={{ ...s.input, height: 60, resize: 'vertical' as const }} value={profileForm.allergies} onChange={e => setF('allergies', e.target.value)} /></div>
            <div><label style={s.label}>Medications</label><textarea style={{ ...s.input, height: 60, resize: 'vertical' as const }} value={profileForm.medications} onChange={e => setF('medications', e.target.value)} /></div>
            <div><label style={s.label}>Emergency Contact</label><input style={s.input} value={profileForm.emergency_contact_name} onChange={e => setF('emergency_contact_name', e.target.value)} /></div>
            <div><label style={s.label}>Emergency Phone</label><input style={s.input} type="tel" value={profileForm.emergency_contact_phone} onChange={e => setF('emergency_contact_phone', e.target.value)} /></div>
          </div>
          <button type="submit" style={{ ...s.btn, ...s.btnPrimary, marginTop: 20 }} disabled={saving}>
            {saving ? 'Saving…' : '💾 Save Profile'}
          </button>
          {msg && <div style={{ ...s.msgBox, background: msg.startsWith('✅') ? '#f0fff4' : '#fff5f5', color: msg.startsWith('✅') ? '#166534' : '#dc2626' }}>{msg}</div>}
        </form>
      </div>

      {/* Change password */}
      <div style={s.card}>
        <div style={s.sTitle}>🔐 Change Password</div>
        <form onSubmit={handlePw} style={{ maxWidth: 400 }}>
          <label style={s.label}>Current Password</label><input style={s.input} type="password" value={pwForm.current_password} onChange={e => setPW('current_password', e.target.value)} required />
          <label style={s.label}>New Password</label><input style={s.input} type="password" minLength={6} value={pwForm.new_password} onChange={e => setPW('new_password', e.target.value)} required />
          <label style={s.label}>Confirm New Password</label><input style={s.input} type="password" value={pwForm.confirm_password} onChange={e => setPW('confirm_password', e.target.value)} required />
          <button type="submit" style={{ ...s.btn, ...s.btnPrimary, marginTop: 16 }} disabled={pwSaving}>
            {pwSaving ? 'Updating…' : '🔐 Change Password'}
          </button>
          {pwMsg && <div style={{ ...s.msgBox, background: pwMsg.startsWith('✅') ? '#f0fff4' : '#fff5f5', color: pwMsg.startsWith('✅') ? '#166534' : '#dc2626' }}>{pwMsg}</div>}
        </form>
      </div>

      {/* Account info */}
      <div style={s.card}>
        <div style={s.sTitle}>ℹ️ Account Information</div>
        {[
          ['User ID', `#${user?.id}`],
          ['Email', user?.email],
          ['Role', user?.role],
          ['Status', user?.is_active ? '✅ Active' : '❌ Inactive'],
          ['Member Since', user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : '—'],
        ].map(([label, val]) => (
          <div key={label as string} style={s.infoRow}>
            <span style={s.infoLabel}>{label}</span>
            <span style={s.infoVal}>{val}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProfilePage;