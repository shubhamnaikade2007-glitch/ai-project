"""
HealthFit AI - Sleep Analyzer (TensorFlow/Keras)
LSTM-based model to analyze sleep patterns over time and predict quality score.
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

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'saved_models', 'sleep_analyzer.keras')

# Features per night: [total_hours, deep_pct, rem_pct, awakenings, bedtime_hour, wake_hour]
SLEEP_FEATURE_DIM = 6
SEQUENCE_LENGTH   = 7   # 7 nights of history


def build_sleep_model() -> 'keras.Model':
    """
    LSTM model that processes 7-night sequences to predict sleep quality score (0-100).
    """
    if not TF_AVAILABLE:
        raise RuntimeError("TensorFlow required.")

    inputs = keras.Input(shape=(SEQUENCE_LENGTH, SLEEP_FEATURE_DIM), name='sleep_sequence')

    x = layers.LSTM(64, return_sequences=True, name='lstm_1')(inputs)
    x = layers.Dropout(0.2)(x)
    x = layers.LSTM(32, name='lstm_2')(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Dense(32, activation='relu', name='dense_1')(x)

    # Two outputs: quality score + classification
    score = layers.Dense(1, activation='sigmoid', name='quality_score')(x)  # 0-1 (scale by 100)
    categ = layers.Dense(4, activation='softmax', name='quality_class')(x)  # poor/fair/good/excellent

    model = keras.Model(inputs, [score, categ], name='SleepAnalyzer')
    model.compile(
        optimizer='adam',
        loss={'quality_score': 'mse', 'quality_class': 'categorical_crossentropy'},
        metrics={'quality_score': 'mae', 'quality_class': 'accuracy'},
    )
    return model


def analyze_sleep(sleep_records: list[dict]) -> dict:
    """
    Analyze a list of nightly sleep records.
    Each record: { total_hours, deep_sleep_pct, rem_sleep_pct, awakenings, bedtime, wake_time }
    Returns: quality assessment dict.
    """
    if not sleep_records:
        return {'error': 'No sleep records provided'}

    # Compute statistical features (works even without TF)
    records = sleep_records[-14:]   # Use last 14 nights max

    hours_list  = [r.get('total_hours', 7) or 7 for r in records]
    deep_list   = [r.get('deep_sleep_pct', 20) or 20 for r in records]
    rem_list    = [r.get('rem_sleep_pct', 25) or 25 for r in records]
    awake_list  = [r.get('awakenings', 1) or 1 for r in records]

    avg_hours   = np.mean(hours_list)
    avg_deep    = np.mean(deep_list)
    avg_rem     = np.mean(rem_list)
    avg_awake   = np.mean(awake_list)
    consistency = 100 - min(np.std(hours_list) * 20, 50)  # penalty for irregular schedule

    # Try LSTM model if available
    if TF_AVAILABLE and os.path.exists(MODEL_PATH) and len(records) >= SEQUENCE_LENGTH:
        try:
            model    = keras.models.load_model(MODEL_PATH)
            seq      = _records_to_sequence(records[-SEQUENCE_LENGTH:])
            preds    = model.predict(seq, verbose=0)
            score    = float(preds[0][0][0]) * 100
            class_idx = int(np.argmax(preds[1][0]))
            quality_labels = ['poor', 'fair', 'good', 'excellent']
            quality = quality_labels[class_idx]
            source  = 'lstm_model'
        except Exception as e:
            score, quality, source = _heuristic_score(avg_hours, avg_deep, avg_rem, avg_awake)
    else:
        score, quality, source = _heuristic_score(avg_hours, avg_deep, avg_rem, avg_awake)

    issues = _identify_issues(avg_hours, avg_deep, avg_rem, avg_awake, consistency)
    recommendations = _sleep_recommendations(avg_hours, avg_deep, avg_rem, issues)

    # Compute recommended bedtime based on average wake time
    # (simple heuristic: 7.5 hours before wake time)
    bedtime_hr = _recommend_bedtime(records)

    return {
        'quality_score':    round(score, 1),
        'quality_rating':   quality,
        'consistency_score': round(consistency, 1),
        'averages': {
            'total_hours':   round(avg_hours, 2),
            'deep_sleep_pct': round(avg_deep, 1),
            'rem_sleep_pct': round(avg_rem, 1),
            'awakenings':    round(avg_awake, 1),
        },
        'issues':          issues,
        'recommendations': recommendations,
        'recommended_bedtime': bedtime_hr,
        'sleep_debt_hours': round(max(0, (7.5 - avg_hours) * len(records)), 1),
        'source':          source,
        'nights_analyzed': len(records),
    }


def _heuristic_score(hours, deep, rem, awake) -> tuple:
    score = 100.0
    if hours < 6:   score -= 30
    elif hours < 7: score -= 15
    elif hours > 9: score -= 10
    if deep < 15:   score -= 20
    elif deep < 20: score -= 10
    if rem < 18:    score -= 20
    elif rem < 25:  score -= 8
    if awake > 3:   score -= 15
    elif awake > 1: score -= 5
    score = max(score, 0)
    if score >= 85: quality = 'excellent'
    elif score >= 70: quality = 'good'
    elif score >= 50: quality = 'fair'
    else: quality = 'poor'
    return score, quality, 'heuristic'


def _identify_issues(hours, deep, rem, awake, consistency) -> list[str]:
    issues = []
    if hours < 7: issues.append(f'Insufficient sleep (avg {hours:.1f}h — target 7-9h)')
    if deep < 15: issues.append('Low deep sleep — impacts physical recovery')
    if rem < 20:  issues.append('Low REM sleep — impacts memory and mood')
    if awake > 2: issues.append(f'Frequent awakenings (avg {awake:.1f}/night)')
    if consistency < 70: issues.append('Irregular sleep schedule detected')
    return issues


def _sleep_recommendations(hours, deep, rem, issues) -> list[str]:
    recs = []
    if hours < 7: recs.append('Go to bed 30-60 minutes earlier to increase total sleep time')
    if deep < 15: recs.extend(['Regular exercise improves deep sleep', 'Avoid alcohol — it suppresses deep sleep'])
    if rem < 20:  recs.extend(['Manage stress before bed', 'Avoid antihistamines/alcohol that suppress REM'])
    recs.extend([
        'Keep bedroom temperature between 65-68°F (18-20°C)',
        'Maintain the same wake time every day, even weekends',
        'Avoid screens 60 minutes before bed (use night mode if necessary)',
        'Consider magnesium supplement — linked to better sleep quality',
    ])
    return recs[:6]


def _recommend_bedtime(records) -> str:
    """Estimate ideal bedtime based on average wake time"""
    wake_hours = []
    for r in records:
        wt = r.get('wake_time')
        if isinstance(wt, str) and ':' in wt:
            try:
                wake_hours.append(int(wt.split(':')[0]))
            except ValueError:
                pass
    if not wake_hours:
        return '22:30'
    avg_wake = int(np.mean(wake_hours))
    bed_hour = (avg_wake - 8) % 24
    return f"{bed_hour:02d}:00"


def _records_to_sequence(records) -> np.ndarray:
    """Convert list of dicts to LSTM input shape (1, seq_len, features)"""
    seq = []
    for r in records:
        seq.append([
            float(r.get('total_hours', 7)) / 12,
            float(r.get('deep_sleep_pct', 20)) / 100,
            float(r.get('rem_sleep_pct', 25)) / 100,
            float(r.get('awakenings', 1)) / 10,
            0.9,   # bedtime normalized placeholder
            0.25,  # wake time normalized placeholder
        ])
    return np.array([seq], dtype=np.float32)
