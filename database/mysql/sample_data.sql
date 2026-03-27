-- ============================================================
-- HealthFit AI - Sample Data
-- Run AFTER schema.sql
-- All passwords are: password123 (hashed with bcrypt)
-- Admin password: admin123
-- ============================================================

USE healthfit_db;

-- ============================================================
-- USERS (passwords are bcrypt hashed)
-- patient@healthfit.com    : password123
-- doctor@healthfit.com     : password123
-- doctor2@healthfit.com    : password123
-- admin@healthfit.com      : admin123
-- ============================================================
INSERT INTO users (email, password_hash, first_name, last_name, role, date_of_birth, gender, phone) VALUES
('patient@healthfit.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkqTyuiUV/z3Fcy',  -- password123
 'Alex', 'Johnson', 'patient', '1990-05-15', 'male', '+1-555-0101'),

('patient2@healthfit.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkqTyuiUV/z3Fcy',
 'Sarah', 'Williams', 'patient', '1985-08-22', 'female', '+1-555-0102'),

('doctor@healthfit.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkqTyuiUV/z3Fcy',
 'Dr. Michael', 'Chen', 'doctor', '1975-03-10', 'male', '+1-555-0201'),

('doctor2@healthfit.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkqTyuiUV/z3Fcy',
 'Dr. Priya', 'Patel', 'doctor', '1980-11-05', 'female', '+1-555-0202'),

('admin@healthfit.com',
 '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  -- admin123
 'Admin', 'User', 'admin', '1988-01-01', 'other', '+1-555-0001');

-- ============================================================
-- USER PROFILES
-- ============================================================
INSERT INTO user_profiles (user_id, height_cm, weight_kg, blood_type, allergies, medications, fitness_goal, activity_level) VALUES
(1, 175.5, 78.0, 'A+',  'None', 'Vitamin D supplements', 'weight_loss', 'moderately_active'),
(2, 162.0, 62.5, 'O+',  'Peanuts', 'None', 'general_wellness', 'lightly_active'),
(3, 180.0, 82.0, 'B+',  'None', 'None', 'general_wellness', 'very_active'),
(4, 165.0, 60.0, 'AB-', 'Penicillin', 'None', 'general_wellness', 'very_active');

-- ============================================================
-- DOCTORS
-- ============================================================
INSERT INTO doctors (user_id, specialization, license_number, hospital_affiliation, years_experience, consultation_fee, rating, bio, available_days, slot_duration_min) VALUES
(3, 'Cardiology', 'MD-2010-001', 'HealthFit Medical Center', 15, 150.00, 4.80,
 'Board-certified cardiologist with 15 years of experience in preventive cardiology and heart health.',
 'monday,tuesday,wednesday,thursday,friday', 30),

(4, 'General Medicine & Nutrition', 'MD-2012-042', 'HealthFit Wellness Clinic', 12, 120.00, 4.90,
 'Specialist in integrative medicine, nutrition, and lifestyle medicine for chronic disease prevention.',
 'monday,wednesday,friday,saturday', 45);

-- ============================================================
-- HEALTH METRICS - Patient 1 (last 30 days of readings)
-- ============================================================
INSERT INTO health_metrics (user_id, metric_type, value, unit, recorded_at, source) VALUES
-- Heart Rate
(1, 'heart_rate', 72, 'bpm', DATE_SUB(NOW(), INTERVAL 30 DAY), 'manual'),
(1, 'heart_rate', 68, 'bpm', DATE_SUB(NOW(), INTERVAL 25 DAY), 'wearable'),
(1, 'heart_rate', 75, 'bpm', DATE_SUB(NOW(), INTERVAL 20 DAY), 'wearable'),
(1, 'heart_rate', 71, 'bpm', DATE_SUB(NOW(), INTERVAL 15 DAY), 'wearable'),
(1, 'heart_rate', 69, 'bpm', DATE_SUB(NOW(), INTERVAL 10 DAY), 'wearable'),
(1, 'heart_rate', 73, 'bpm', DATE_SUB(NOW(), INTERVAL 5 DAY),  'wearable'),
(1, 'heart_rate', 70, 'bpm', NOW(),                            'wearable'),

-- Blood Pressure
(1, 'blood_pressure_systolic',  128, 'mmHg', DATE_SUB(NOW(), INTERVAL 30 DAY), 'device'),
(1, 'blood_pressure_diastolic',  82, 'mmHg', DATE_SUB(NOW(), INTERVAL 30 DAY), 'device'),
(1, 'blood_pressure_systolic',  125, 'mmHg', DATE_SUB(NOW(), INTERVAL 15 DAY), 'device'),
(1, 'blood_pressure_diastolic',  80, 'mmHg', DATE_SUB(NOW(), INTERVAL 15 DAY), 'device'),
(1, 'blood_pressure_systolic',  122, 'mmHg', NOW(),                            'device'),
(1, 'blood_pressure_diastolic',  78, 'mmHg', NOW(),                            'device'),

-- Blood Glucose
(1, 'blood_glucose', 95.0, 'mg/dL', DATE_SUB(NOW(), INTERVAL 20 DAY), 'device'),
(1, 'blood_glucose', 98.5, 'mg/dL', DATE_SUB(NOW(), INTERVAL 10 DAY), 'device'),
(1, 'blood_glucose', 92.0, 'mg/dL', NOW(),                            'device'),

-- Body Temperature
(1, 'body_temperature', 36.6, '°C', NOW(), 'device'),

-- Oxygen Saturation
(1, 'oxygen_saturation', 98.0, '%', NOW(), 'wearable'),

-- BMI (calculated)
(1, 'bmi', 25.3, 'kg/m²', DATE_SUB(NOW(), INTERVAL 30 DAY), 'manual'),
(1, 'bmi', 25.1, 'kg/m²', NOW(),                            'manual'),

-- Weight
(1, 'weight', 78.5, 'kg', DATE_SUB(NOW(), INTERVAL 30 DAY), 'manual'),
(1, 'weight', 78.0, 'kg', NOW(),                            'manual'),

-- Steps
(1, 'steps_count', 7500, 'steps', DATE_SUB(NOW(), INTERVAL 5 DAY), 'wearable'),
(1, 'steps_count', 8200, 'steps', DATE_SUB(NOW(), INTERVAL 4 DAY), 'wearable'),
(1, 'steps_count', 6800, 'steps', DATE_SUB(NOW(), INTERVAL 3 DAY), 'wearable'),
(1, 'steps_count', 9100, 'steps', DATE_SUB(NOW(), INTERVAL 2 DAY), 'wearable'),
(1, 'steps_count', 7700, 'steps', DATE_SUB(NOW(), INTERVAL 1 DAY), 'wearable'),

-- Sleep
(1, 'sleep_hours', 7.5, 'hours', DATE_SUB(NOW(), INTERVAL 5 DAY), 'wearable'),
(1, 'sleep_hours', 6.8, 'hours', DATE_SUB(NOW(), INTERVAL 4 DAY), 'wearable'),
(1, 'sleep_hours', 8.2, 'hours', DATE_SUB(NOW(), INTERVAL 3 DAY), 'wearable'),
(1, 'sleep_hours', 7.0, 'hours', DATE_SUB(NOW(), INTERVAL 2 DAY), 'wearable'),

-- Stress Level
(1, 'stress_level', 3.2, '/10', DATE_SUB(NOW(), INTERVAL 5 DAY), 'ai_estimated'),
(1, 'stress_level', 4.5, '/10', DATE_SUB(NOW(), INTERVAL 3 DAY), 'ai_estimated'),
(1, 'stress_level', 2.8, '/10', NOW(),                           'ai_estimated'),

-- Patient 2 metrics
(2, 'heart_rate',              75, 'bpm',  NOW(), 'wearable'),
(2, 'blood_pressure_systolic', 118, 'mmHg', NOW(), 'device'),
(2, 'blood_pressure_diastolic', 76, 'mmHg', NOW(), 'device'),
(2, 'blood_glucose',           88.0, 'mg/dL', NOW(), 'device'),
(2, 'oxygen_saturation',       99.0, '%', NOW(), 'wearable'),
(2, 'bmi',                     23.8, 'kg/m²', NOW(), 'manual'),
(2, 'sleep_hours',             8.5, 'hours', NOW(), 'wearable');

-- ============================================================
-- ORGAN HEALTH SCORES - Patient 1
-- ============================================================
INSERT INTO organ_health_scores (user_id, organ, score, risk_level, factors, recommendations) VALUES
(1, 'heart',         78.5, 'low',      '{"bp_trend":"improving","hr_variability":"good","exercise":"moderate"}', 'Maintain current exercise routine. Monitor BP weekly.'),
(1, 'liver',         85.0, 'low',      '{"alcohol":"none","diet":"balanced","bmi":"slightly_high"}', 'Continue healthy diet. Annual liver function test recommended.'),
(1, 'kidneys',       88.2, 'low',      '{"hydration":"adequate","glucose":"normal","protein_intake":"normal"}', 'Stay well hydrated. Keep blood glucose in normal range.'),
(1, 'lungs',         90.0, 'low',      '{"smoking":"non_smoker","exercise":"regular","o2_sat":"98%"}', 'Excellent lung health. Continue cardiovascular exercise.'),
(1, 'brain',         82.0, 'low',      '{"sleep":"adequate","stress":"moderate","cognitive_load":"normal"}', 'Improve sleep consistency. Practice stress management techniques.'),
(1, 'overall',       84.7, 'low',      '{"composite_score":84.7}', 'Overall good health. Focus on reducing stress and losing 5kg.'),
(2, 'overall',       91.0, 'low',      '{"composite_score":91.0}', 'Excellent health status. Maintain current lifestyle.');

-- ============================================================
-- APPOINTMENTS
-- ============================================================
INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, type, reason, notes) VALUES
(1, 3, DATE_ADD(CURDATE(), INTERVAL 3 DAY),  '10:00:00', 'confirmed', 'in_person',
 'Annual cardiac checkup and blood pressure review',
 'Patient reports occasional mild headaches. Follow up on BP management.'),

(1, 4, DATE_ADD(CURDATE(), INTERVAL 7 DAY),  '14:30:00', 'pending', 'video_call',
 'Nutrition consultation for weight management',
 'Review 30-day food diary and create meal plan.'),

(2, 4, DATE_ADD(CURDATE(), INTERVAL 1 DAY),  '09:00:00', 'confirmed', 'in_person',
 'General wellness checkup',
 NULL),

(1, 3, DATE_SUB(CURDATE(), INTERVAL 30 DAY), '11:00:00', 'completed', 'in_person',
 'Initial cardiac assessment',
 'BP slightly elevated. Lifestyle changes recommended. Follow up in 1 month.'),

(1, 3, DATE_SUB(CURDATE(), INTERVAL 60 DAY), '10:00:00', 'completed', 'in_person',
 'Routine checkup',
 'All vitals normal. Encouraged to increase physical activity.');

-- ============================================================
-- MEALS - Patient 1 (last 7 days)
-- ============================================================
INSERT INTO meals (user_id, meal_name, meal_type, calories, protein_g, carbohydrates_g, fat_g, fiber_g, logged_at) VALUES
(1, 'Oatmeal with berries and almonds', 'breakfast', 380, 12.0, 58.0, 12.0, 8.0, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(1, 'Grilled chicken salad',           'lunch',     420, 38.0, 22.0, 18.0, 6.0, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(1, 'Salmon with quinoa and broccoli', 'dinner',    520, 45.0, 38.0, 16.0, 7.0, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(1, 'Greek yogurt with honey',         'snack',     180, 12.0, 24.0,  4.0, 0.0, DATE_SUB(NOW(), INTERVAL 2 DAY)),

(1, 'Scrambled eggs with whole wheat toast', 'breakfast', 350, 18.0, 36.0, 14.0, 4.0, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(1, 'Turkey and avocado wrap',         'lunch',     460, 32.0, 42.0, 18.0, 8.0, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(1, 'Beef stir fry with vegetables',   'dinner',    480, 35.0, 35.0, 16.0, 5.0, DATE_SUB(NOW(), INTERVAL 1 DAY)),

(1, 'Smoothie bowl',                   'breakfast', 320, 10.0, 55.0,  8.0, 6.0, NOW()),
(1, 'Lentil soup with bread',          'lunch',     380, 18.0, 58.0,  6.0, 12.0, NOW()),

(2, 'Avocado toast with eggs',         'breakfast', 400, 16.0, 38.0, 20.0, 7.0, NOW()),
(2, 'Caesar salad with chicken',       'lunch',     380, 32.0, 18.0, 20.0, 4.0, NOW());

-- ============================================================
-- WORKOUTS - Patient 1 (last 2 weeks)
-- ============================================================
INSERT INTO workouts (user_id, workout_name, workout_type, duration_min, calories_burned, heart_rate_avg, heart_rate_max, intensity, form_score, form_feedback, started_at) VALUES
(1, 'Morning Run',            'running',  35, 320, 145, 168, 'moderate', 88.5, 'Good stride length. Slightly forward lean detected - work on posture.', DATE_SUB(NOW(), INTERVAL 7 DAY)),
(1, 'Upper Body Strength',    'strength', 45, 280, 128, 155, 'moderate', 92.0, 'Excellent form on bench press. Watch elbow alignment during curls.', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(1, 'HIIT Cardio Session',    'hiit',     30, 380, 162, 182, 'high',     85.5, 'Good energy maintenance. Left knee slightly inward on jump squats.', DATE_SUB(NOW(), INTERVAL 5 DAY)),
(1, 'Evening Walk',           'walking',  45, 180,  98, 115, 'low',      95.0, 'Great posture throughout.', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(1, 'Full Body Strength',     'strength', 55, 310, 132, 158, 'moderate', 90.0, 'Squat depth excellent. Minor hip shift on deadlifts - check video.', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(1, 'Cycling',                'cycling',  40, 350, 140, 165, 'moderate', 94.0, 'Good cadence maintained throughout session.', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(1, 'Yoga Flow',              'yoga',     50, 150, 85,  105, 'low',      97.5, 'Beautiful form. Great flexibility improvement from last session.', DATE_SUB(NOW(), INTERVAL 1 DAY));

-- ============================================================
-- SLEEP RECORDS - Patient 1 (last 7 days)
-- ============================================================
INSERT INTO sleep_records (user_id, sleep_date, bedtime, wake_time, total_hours, deep_sleep_pct, rem_sleep_pct, light_sleep_pct, awakenings, sleep_score, quality_rating) VALUES
(1, DATE_SUB(CURDATE(), INTERVAL 7 DAY), '22:30:00', '06:00:00', 7.5, 20.0, 25.0, 55.0, 1, 82.0, 'good'),
(1, DATE_SUB(CURDATE(), INTERVAL 6 DAY), '23:15:00', '06:30:00', 7.25, 18.0, 22.0, 60.0, 2, 75.0, 'good'),
(1, DATE_SUB(CURDATE(), INTERVAL 5 DAY), '22:00:00', '06:30:00', 8.5, 24.0, 28.0, 48.0, 0, 91.0, 'excellent'),
(1, DATE_SUB(CURDATE(), INTERVAL 4 DAY), '00:30:00', '07:00:00', 6.5, 14.0, 20.0, 66.0, 3, 62.0, 'fair'),
(1, DATE_SUB(CURDATE(), INTERVAL 3 DAY), '22:45:00', '06:15:00', 7.5, 21.0, 26.0, 53.0, 1, 83.0, 'good'),
(1, DATE_SUB(CURDATE(), INTERVAL 2 DAY), '23:00:00', '06:30:00', 7.5, 19.0, 24.0, 57.0, 2, 78.0, 'good'),
(1, DATE_SUB(CURDATE(), INTERVAL 1 DAY), '22:15:00', '06:30:00', 8.25, 23.0, 27.0, 50.0, 0, 89.0, 'excellent');

-- ============================================================
-- AI PREDICTIONS - Patient 1
-- ============================================================
INSERT INTO ai_predictions (user_id, prediction_type, model_name, input_data, prediction, risk_score, risk_level, confidence, recommendations) VALUES
(1, 'health_risk', 'HealthRiskClassifier_v2',
 '{"age":34,"bmi":25.1,"systolic":122,"diastolic":78,"heart_rate":70,"glucose":92,"activity":"moderate"}',
 '{"cardiovascular_risk":0.12,"diabetes_risk":0.08,"hypertension_risk":0.18,"overall_risk":"low"}',
 18.5, 'low', 87.3,
 'Maintain current blood pressure trend. Increase daily steps to 10,000. Consider reducing sodium intake.'),

(1, 'sleep_quality', 'SleepAnalyzer_v1',
 '{"avg_hours":7.5,"deep_pct":21.0,"rem_pct":25.5,"awakenings":1.3,"consistency_score":72}',
 '{"quality":"good","recommended_bedtime":"22:30","sleep_debt_hours":0.5,"quality_score":80.0}',
 20.0, 'low', 91.0,
 'Sleep quality is good. Avoid screens 1 hour before bed. Maintain consistent sleep schedule for better deep sleep.'),

(1, 'stress_level', 'StressDetector_v1',
 '{"hr_variability":45,"sleep_quality":80,"activity_level":6,"subjective_stress":3}',
 '{"stress_score":3.2,"stress_category":"mild","primary_triggers":["work_schedule","sleep_consistency"]}',
 32.0, 'low', 85.0,
 'Mild stress detected. Daily 10-minute meditation recommended. Consider journaling before bed.');

-- ============================================================
-- NOTIFICATIONS - Patient 1
-- ============================================================
INSERT INTO notifications (user_id, title, message, type, is_read) VALUES
(1, 'Appointment Reminder', 'You have an appointment with Dr. Chen in 3 days at 10:00 AM.', 'appointment', FALSE),
(1, 'Health Goal Achieved! 🎉', 'Congratulations! You hit your step goal of 9,000 steps yesterday.', 'health_alert', FALSE),
(1, 'AI Health Insight', 'Your cardiovascular health score improved by 3% this week. Keep it up!', 'ai_insight', TRUE),
(1, 'Nutrition Reminder', 'You haven\'t logged lunch yet today. Don\'t forget to track your meals!', 'nutrition', FALSE),
(1, 'Sleep Pattern Alert', 'Your sleep schedule was irregular last night. Try to maintain consistent sleep times.', 'health_alert', TRUE),
(2, 'Appointment Tomorrow', 'Reminder: appointment with Dr. Patel tomorrow at 9:00 AM.', 'appointment', FALSE);

-- ============================================================
-- MEDICATION REMINDERS - Patient 1
-- ============================================================
INSERT INTO medication_reminders (user_id, medication_name, dosage, frequency, reminder_times, start_date, is_active) VALUES
(1, 'Vitamin D3', '2000 IU', 'once_daily', '["08:00"]', CURDATE(), TRUE),
(1, 'Omega-3 Fish Oil', '1000mg', 'twice_daily', '["08:00", "20:00"]', CURDATE(), TRUE);
