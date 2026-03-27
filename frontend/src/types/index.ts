// HealthFit AI - TypeScript Type Definitions

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: 'patient' | 'doctor' | 'admin';
  age?: number;
  gender?: 'male' | 'female' | 'other';
  phone?: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  profile?: UserProfile;
}

export interface UserProfile {
  height_cm?: number;
  weight_kg?: number;
  bmi?: number;
  blood_type?: string;
  allergies?: string;
  medications?: string;
  medical_history?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  fitness_goal?: string;
  activity_level?: string;
}

export interface HealthMetric {
  id: number;
  user_id: number;
  metric_type: string;
  value: number;
  unit?: string;
  recorded_at: string;
  source: 'manual' | 'wearable' | 'device' | 'ai_estimated';
  notes?: string;
  is_normal?: boolean;
  status?: 'normal' | 'low' | 'high';
}

export interface OrganHealthScore {
  id: number;
  organ: string;
  score: number;
  risk_level: 'low' | 'moderate' | 'high' | 'critical';
  computed_at: string;
  factors?: Record<string, any>;
  recommendations?: string;
}

export interface Appointment {
  id: number;
  patient_id: number;
  doctor_id: number;
  patient_name?: string;
  doctor_name?: string;
  appointment_date: string;
  appointment_time: string;
  duration_min: number;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'no_show';
  type: 'in_person' | 'video_call' | 'phone';
  reason?: string;
  notes?: string;
  diagnosis?: string;
  prescription?: string;
  follow_up_date?: string;
  is_upcoming: boolean;
  created_at: string;
}

export interface Doctor {
  id: number;
  user_id: number;
  name: string;
  email?: string;
  specialization: string;
  license_number: string;
  hospital_affiliation?: string;
  years_experience: number;
  consultation_fee: number;
  rating: number;
  bio?: string;
  available_days: string[];
  slot_duration_min: number;
  avatar_url?: string;
}

export interface Meal {
  id: number;
  user_id: number;
  meal_name: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack' | 'pre_workout' | 'post_workout';
  calories?: number;
  protein_g?: number;
  carbohydrates_g?: number;
  fat_g?: number;
  fiber_g?: number;
  sugar_g?: number;
  serving_size?: string;
  ingredients?: string;
  logged_at: string;
  notes?: string;
}

export interface Workout {
  id: number;
  user_id: number;
  workout_name: string;
  workout_type: string;
  duration_min: number;
  calories_burned?: number;
  distance_km?: number;
  heart_rate_avg?: number;
  heart_rate_max?: number;
  intensity: 'low' | 'moderate' | 'high' | 'extreme';
  form_score?: number;
  form_feedback?: string;
  started_at: string;
  notes?: string;
}

export interface SleepRecord {
  id: number;
  user_id: number;
  sleep_date: string;
  bedtime?: string;
  wake_time?: string;
  total_hours?: number;
  deep_sleep_pct?: number;
  rem_sleep_pct?: number;
  awakenings?: number;
  sleep_score?: number;
  quality_rating?: 'poor' | 'fair' | 'good' | 'excellent';
  notes?: string;
}

export interface AIPrediction {
  id: number;
  prediction_type: string;
  model_name?: string;
  risk_score?: number;
  risk_level?: 'low' | 'moderate' | 'high' | 'critical';
  confidence?: number;
  recommendations?: string;
  predicted_at: string;
}

export interface HealthSummary {
  latest_metrics: Record<string, HealthMetric>;
  averages: Record<string, { avg: number; readings: number }>;
  organ_scores: Record<string, OrganHealthScore>;
  days_analyzed: number;
}

export interface NutritionSummary {
  date: string;
  by_type: Record<string, {
    meal_count: number;
    calories: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
  }>;
  totals: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    fiber: number;
  };
  targets: Record<string, number>;
  completion: Record<string, number>;
}

export interface ApiError {
  error: string;
  message?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export interface RiskPrediction {
  risk_level: 'low' | 'moderate' | 'high' | 'critical';
  risk_score: number;
  disease_risks?: Record<string, number>;
  alerts?: string[];
  recommendations?: string[];
  confidence?: number;
  model?: string;
}
