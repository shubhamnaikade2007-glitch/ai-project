-- ============================================================
-- HealthFit AI - Complete MySQL Database Schema
-- Run with: mysql -u root -proot123 < schema.sql
-- ============================================================

-- Create and select database
CREATE DATABASE IF NOT EXISTS healthfit_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE healthfit_db;

-- ============================================================
-- USERS TABLE
-- Stores all user accounts (patients, doctors, admins)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name    VARCHAR(100) NOT NULL,
    last_name     VARCHAR(100) NOT NULL,
    role          ENUM('patient', 'doctor', 'admin') DEFAULT 'patient',
    date_of_birth DATE,
    gender        ENUM('male', 'female', 'other'),
    phone         VARCHAR(20),
    avatar_url    VARCHAR(500),
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role  (role)
);

-- ============================================================
-- USER PROFILES TABLE
-- Extended health profile information per user
-- ============================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    height_cm       DECIMAL(5,2),
    weight_kg       DECIMAL(5,2),
    blood_type      ENUM('A+','A-','B+','B-','AB+','AB-','O+','O-'),
    allergies       TEXT,
    medications     TEXT,
    medical_history TEXT,
    emergency_contact_name  VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    fitness_goal    ENUM('weight_loss','muscle_gain','endurance','flexibility','general_wellness') DEFAULT 'general_wellness',
    activity_level  ENUM('sedentary','lightly_active','moderately_active','very_active','extra_active') DEFAULT 'moderately_active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- DOCTORS TABLE
-- Doctor-specific information linked to users
-- ============================================================
CREATE TABLE IF NOT EXISTS doctors (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    user_id           INT NOT NULL UNIQUE,
    specialization    VARCHAR(200) NOT NULL,
    license_number    VARCHAR(100) NOT NULL UNIQUE,
    hospital_affiliation VARCHAR(300),
    years_experience  INT DEFAULT 0,
    consultation_fee  DECIMAL(10,2) DEFAULT 0.00,
    rating            DECIMAL(3,2) DEFAULT 0.00,
    bio               TEXT,
    available_days    SET('monday','tuesday','wednesday','thursday','friday','saturday','sunday'),
    slot_duration_min INT DEFAULT 30,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_specialization (specialization)
);

-- ============================================================
-- APPOINTMENTS TABLE
-- Patient-doctor appointment bookings
-- ============================================================
CREATE TABLE IF NOT EXISTS appointments (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,
    doctor_id       INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration_min    INT DEFAULT 30,
    status          ENUM('pending','confirmed','completed','cancelled','no_show') DEFAULT 'pending',
    type            ENUM('in_person','video_call','phone') DEFAULT 'in_person',
    reason          TEXT,
    notes           TEXT,
    diagnosis       TEXT,
    prescription    TEXT,
    follow_up_date  DATE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_patient  (patient_id),
    INDEX idx_doctor   (doctor_id),
    INDEX idx_date     (appointment_date),
    INDEX idx_status   (status)
);

-- ============================================================
-- HEALTH METRICS TABLE
-- All measurable health readings (heart rate, BP, BMI, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS health_metrics (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    metric_type     ENUM(
                        'heart_rate',
                        'blood_pressure_systolic',
                        'blood_pressure_diastolic',
                        'blood_glucose',
                        'body_temperature',
                        'oxygen_saturation',
                        'bmi',
                        'weight',
                        'body_fat_percentage',
                        'cholesterol_total',
                        'cholesterol_hdl',
                        'cholesterol_ldl',
                        'triglycerides',
                        'sleep_hours',
                        'sleep_quality',
                        'stress_level',
                        'steps_count',
                        'calories_burned',
                        'water_intake_ml'
                    ) NOT NULL,
    value           DECIMAL(10,3) NOT NULL,
    unit            VARCHAR(50),
    recorded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source          ENUM('manual','wearable','device','ai_estimated') DEFAULT 'manual',
    notes           VARCHAR(500),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_metric  (user_id, metric_type),
    INDEX idx_recorded_at  (recorded_at),
    INDEX idx_metric_type  (metric_type)
);

-- ============================================================
-- ORGAN HEALTH SCORES TABLE
-- AI-computed organ/system health scores
-- ============================================================
CREATE TABLE IF NOT EXISTS organ_health_scores (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    organ           ENUM('heart','liver','kidneys','lungs','brain','immune_system','digestive','overall') NOT NULL,
    score           DECIMAL(5,2) NOT NULL CHECK (score BETWEEN 0 AND 100),
    risk_level      ENUM('low','moderate','high','critical') DEFAULT 'low',
    computed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    factors         JSON,          -- JSON object explaining score factors
    recommendations TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_organ (user_id, organ)
);

-- ============================================================
-- MEALS TABLE
-- Nutrition and food intake tracking
-- ============================================================
CREATE TABLE IF NOT EXISTS meals (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    meal_name       VARCHAR(300) NOT NULL,
    meal_type       ENUM('breakfast','lunch','dinner','snack','pre_workout','post_workout') NOT NULL,
    calories        INT,
    protein_g       DECIMAL(8,2),
    carbohydrates_g DECIMAL(8,2),
    fat_g           DECIMAL(8,2),
    fiber_g         DECIMAL(8,2),
    sugar_g         DECIMAL(8,2),
    sodium_mg       DECIMAL(8,2),
    vitamins        JSON,          -- {"vitamin_c": 45, "vitamin_d": 10, ...}
    minerals        JSON,          -- {"iron": 8, "calcium": 200, ...}
    serving_size    VARCHAR(100),
    ingredients     TEXT,
    image_url       VARCHAR(500),
    logged_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes           VARCHAR(500),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_meal (user_id),
    INDEX idx_meal_type (meal_type),
    INDEX idx_logged_at (logged_at)
);

-- ============================================================
-- WORKOUTS TABLE
-- Exercise sessions and fitness activities
-- ============================================================
CREATE TABLE IF NOT EXISTS workouts (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    workout_name    VARCHAR(300) NOT NULL,
    workout_type    ENUM('cardio','strength','flexibility','hiit','yoga','swimming','cycling','running','walking','sports','other') NOT NULL,
    duration_min    INT NOT NULL,
    calories_burned INT,
    distance_km     DECIMAL(8,3),
    sets_count      INT,
    reps_count      INT,
    weight_kg       DECIMAL(8,2),
    heart_rate_avg  INT,
    heart_rate_max  INT,
    intensity       ENUM('low','moderate','high','extreme') DEFAULT 'moderate',
    form_score      DECIMAL(5,2),   -- AI-analyzed form score 0-100
    form_feedback   TEXT,
    exercises       JSON,           -- Array of exercise objects
    started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP,
    notes           VARCHAR(500),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_workout  (user_id),
    INDEX idx_workout_type  (workout_type),
    INDEX idx_started_at    (started_at)
);

-- ============================================================
-- SLEEP RECORDS TABLE
-- Detailed sleep tracking data
-- ============================================================
CREATE TABLE IF NOT EXISTS sleep_records (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    sleep_date      DATE NOT NULL,
    bedtime         TIME,
    wake_time       TIME,
    total_hours     DECIMAL(4,2),
    deep_sleep_pct  DECIMAL(5,2),
    rem_sleep_pct   DECIMAL(5,2),
    light_sleep_pct DECIMAL(5,2),
    awakenings      INT DEFAULT 0,
    sleep_score     DECIMAL(5,2),    -- AI-computed 0-100
    quality_rating  ENUM('poor','fair','good','excellent'),
    factors         JSON,            -- {"noise": "low", "temperature": "comfortable"}
    notes           VARCHAR(500),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_sleep (user_id),
    INDEX idx_sleep_date (sleep_date)
);

-- ============================================================
-- AI PREDICTIONS TABLE
-- Stores all AI model predictions and risk assessments
-- ============================================================
CREATE TABLE IF NOT EXISTS ai_predictions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    prediction_type ENUM('health_risk','disease_risk','sleep_quality','stress_level','nutrition_gap','fitness_performance') NOT NULL,
    model_name      VARCHAR(100),
    input_data      JSON NOT NULL,
    prediction      JSON NOT NULL,    -- Full prediction output
    risk_score      DECIMAL(5,2),
    risk_level      ENUM('low','moderate','high','critical'),
    confidence      DECIMAL(5,2),
    recommendations TEXT,
    is_reviewed     BOOLEAN DEFAULT FALSE,
    reviewed_by     INT,
    predicted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_prediction (user_id),
    INDEX idx_prediction_type (prediction_type)
);

-- ============================================================
-- NOTIFICATIONS TABLE
-- In-app notifications and reminders
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    title           VARCHAR(300) NOT NULL,
    message         TEXT NOT NULL,
    type            ENUM('appointment','health_alert','medication','workout','nutrition','system','ai_insight') DEFAULT 'system',
    is_read         BOOLEAN DEFAULT FALSE,
    action_url      VARCHAR(500),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_notif  (user_id),
    INDEX idx_is_read     (is_read)
);

-- ============================================================
-- MEDICATION REMINDERS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS medication_reminders (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    medication_name VARCHAR(200) NOT NULL,
    dosage          VARCHAR(100),
    frequency       ENUM('once_daily','twice_daily','three_times_daily','weekly','as_needed') DEFAULT 'once_daily',
    reminder_times  JSON,           -- ["08:00", "20:00"]
    start_date      DATE,
    end_date        DATE,
    is_active       BOOLEAN DEFAULT TRUE,
    notes           VARCHAR(500),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- AUDIT LOG TABLE
-- Track important actions for security
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT,
    action      VARCHAR(200) NOT NULL,
    resource    VARCHAR(200),
    ip_address  VARCHAR(45),
    user_agent  VARCHAR(500),
    details     JSON,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_audit (user_id),
    INDEX idx_action     (action)
);
