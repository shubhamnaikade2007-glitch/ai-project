"""
HealthFit AI - Stress Detector (TensorFlow + Scikit-learn)
Multi-modal stress estimation combining HRV, sleep, activity, and self-reported data.
"""
import os
import numpy as np

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

try:
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    import joblib
    SK_AVAILABLE = True
except ImportError:
    SK_AVAILABLE = False

MODEL_PATH  = os.path.join(os.path.dirname(__file__), '..', '..', 'saved_models', 'stress_detector.pkl')
TF_PATH     = os.path.join(os.path.dirname(__file__), '..', '..', 'saved_models', 'stress_detector_tf.keras')

STRESS_FEATURES = [
    'hrv_ms',           # Heart rate variability (ms) — lower = more stress
    'resting_hr',       # Resting heart rate
    'sleep_score',      # 0-100
    'sleep_hours',      # Hours of sleep
    'activity_minutes', # Active minutes per day
    'subjective_stress',# Self-reported 0-10
    'recovery_score',   # 0-100 (from wearable)
]

STRESS_CATEGORIES = {
    (0,   25): ('minimal',  '😌'),
    (25,  45): ('mild',     '🙂'),
    (45,  65): ('moderate', '😐'),
    (65,  80): ('high',     '😟'),
    (80, 101): ('severe',   '😰'),
}


def build_stress_model():
    """
    Build a simple feedforward network for stress regression.
    Outputs a continuous stress score 0-100.
    """
    if not TF_AVAILABLE:
        raise RuntimeError("TensorFlow required.")

    model = keras.Sequential([
        keras.Input(shape=(len(STRESS_FEATURES),)),
        layers.Dense(64, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(16, activation='relu'),
        layers.Dense(1, activation='sigmoid', name='stress_score'),  # 0-1, scale by 100
    ], name='StressDetector')

    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model


def detect_stress(features: dict) -> dict:
    """
    Estimate stress level from a feature dictionary.
    Features (all optional with defaults):
      hrv_ms, resting_hr, sleep_score, sleep_hours,
      activity_minutes, subjective_stress, recovery_score
    """
    # Try sklearn model first (lighter weight)
    if SK_AVAILABLE and os.path.exists(MODEL_PATH):
        try:
            pkg    = joblib.load(MODEL_PATH)
            scaler = pkg['scaler']
            model  = pkg['model']
            X      = scaler.transform([_to_vector(features)])
            score  = float(model.predict(X)[0])
            source = 'sklearn_gbm'
        except Exception:
            score, source = _heuristic_stress(features)
    elif TF_AVAILABLE and os.path.exists(TF_PATH):
        try:
            model  = keras.models.load_model(TF_PATH)
            X      = np.array([_to_vector(features)], dtype=np.float32)
            score  = float(model.predict(X, verbose=0)[0][0]) * 100
            source = 'tensorflow'
        except Exception:
            score, source = _heuristic_stress(features)
    else:
        score, source = _heuristic_stress(features)

    score    = max(0.0, min(100.0, score))
    category, emoji = _get_category(score)

    # Identify triggers
    triggers = _identify_triggers(features)

    return {
        'stress_score':    round(score, 1),
        'stress_category': category,
        'emoji':           emoji,
        'primary_triggers': triggers,
        'hrv_note':        _hrv_interpretation(features.get('hrv_ms')),
        'recommendations': _stress_recommendations(category, triggers),
        'source':          source,
    }


def train_sklearn(X: np.ndarray, y: np.ndarray) -> dict:
    """Train the GBM stress regressor"""
    if not SK_AVAILABLE:
        return {'error': 'scikit-learn not available'}

    scaler = StandardScaler()
    X_sc   = scaler.fit_transform(X)

    model  = GradientBoostingRegressor(
        n_estimators=300, learning_rate=0.05,
        max_depth=4, random_state=42
    )
    model.fit(X_sc, y)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump({'model': model, 'scaler': scaler}, MODEL_PATH)

    train_score = model.score(X_sc, y)
    return {'r2_score': round(train_score, 4), 'saved_to': MODEL_PATH}


def _to_vector(f: dict) -> list:
    return [
        float(f.get('hrv_ms',            45)) / 100,
        float(f.get('resting_hr',        70)) / 200,
        float(f.get('sleep_score',       75)) / 100,
        float(f.get('sleep_hours',        7)) / 12,
        float(f.get('activity_minutes', 30)) / 120,
        float(f.get('subjective_stress',  5)) / 10,
        float(f.get('recovery_score',    70)) / 100,
    ]


def _heuristic_stress(f: dict) -> tuple:
    score = float(f.get('subjective_stress', 5)) * 8   # 0-80 base

    hrv     = f.get('hrv_ms')
    sleep_q = float(f.get('sleep_score', 75))
    hr      = float(f.get('resting_hr', 70))
    sleep_h = float(f.get('sleep_hours', 7))

    if hrv is not None:
        if float(hrv) < 20: score += 20
        elif float(hrv) < 40: score += 10
    if sleep_q < 50: score += 15
    elif sleep_q < 70: score += 8
    if hr > 90: score += 10
    elif hr > 80: score += 5
    if sleep_h < 6: score += 12

    return min(score, 100), 'heuristic'


def _get_category(score: float) -> tuple:
    for (lo, hi), (cat, emoji) in STRESS_CATEGORIES.items():
        if lo <= score < hi:
            return cat, emoji
    return 'severe', '😰'


def _identify_triggers(f: dict) -> list:
    triggers = []
    if float(f.get('sleep_hours', 7)) < 6.5:
        triggers.append('sleep_deprivation')
    if float(f.get('sleep_score', 75)) < 65:
        triggers.append('poor_sleep_quality')
    hrv = f.get('hrv_ms')
    if hrv is not None and float(hrv) < 30:
        triggers.append('low_hrv')
    if float(f.get('activity_minutes', 30)) < 15:
        triggers.append('physical_inactivity')
    if float(f.get('subjective_stress', 5)) >= 7:
        triggers.append('perceived_stress')
    return triggers or ['no_clear_trigger']


def _hrv_interpretation(hrv) -> str | None:
    if hrv is None: return None
    hrv = float(hrv)
    if hrv >= 60: return 'Excellent HRV — low physiological stress'
    if hrv >= 40: return 'Good HRV — manageable stress levels'
    if hrv >= 25: return 'Moderate HRV — some physiological stress present'
    return 'Low HRV — body under significant stress; consider rest day'


def _stress_recommendations(category: str, triggers: list) -> list:
    recs = []
    if 'sleep_deprivation' in triggers or 'poor_sleep_quality' in triggers:
        recs.append('Prioritize 7-9 hours of quality sleep — it is the #1 stress recovery tool')
    if 'physical_inactivity' in triggers:
        recs.append('Even a 20-minute walk significantly reduces cortisol levels')
    if 'low_hrv' in triggers:
        recs.append('Take a rest/recovery day — your nervous system needs it')

    if category in ('high', 'severe'):
        recs.extend([
            '4-7-8 breathing: inhale 4s, hold 7s, exhale 8s — repeat 4x',
            'Consider speaking with a mental health professional',
            'Schedule non-negotiable downtime into your day',
        ])
    else:
        recs.extend([
            '10 minutes of mindfulness or meditation daily',
            'Regular journaling to offload mental load',
            'Connect socially — meaningful connection reduces stress hormones',
        ])

    return recs[:5]
