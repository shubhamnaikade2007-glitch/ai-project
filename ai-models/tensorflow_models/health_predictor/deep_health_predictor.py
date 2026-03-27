"""
HealthFit AI - Deep Health Predictor (TensorFlow/Keras)
A deep neural network for multi-output health risk prediction.
Predicts risk probability across multiple disease categories simultaneously.
"""
import os
import numpy as np

# Graceful import — TensorFlow is large and may not be installed in all envs
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, callbacks, regularizers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️  TensorFlow not available. DeepHealthPredictor will use fallback mode.")

DISEASE_OUTPUTS = ['cardiovascular', 'diabetes', 'hypertension', 'obesity', 'metabolic_syndrome']
INPUT_DIM       = 15   # feature vector size

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'saved_models', 'deep_health_predictor.keras')


def build_model() -> 'keras.Model':
    """
    Build the multi-output deep learning model.
    Architecture: Shared encoder + per-disease output heads.
    """
    if not TF_AVAILABLE:
        raise RuntimeError("TensorFlow is required but not installed.")

    # Input layer
    inputs = keras.Input(shape=(INPUT_DIM,), name='health_features')

    # Shared encoder
    x = layers.Dense(256, activation='relu',
                     kernel_regularizer=regularizers.l2(1e-4), name='enc_1')(inputs)
    x = layers.BatchNormalization(name='bn_1')(x)
    x = layers.Dropout(0.3, name='drop_1')(x)

    x = layers.Dense(128, activation='relu',
                     kernel_regularizer=regularizers.l2(1e-4), name='enc_2')(x)
    x = layers.BatchNormalization(name='bn_2')(x)
    x = layers.Dropout(0.25, name='drop_2')(x)

    x = layers.Dense(64, activation='relu', name='enc_3')(x)
    x = layers.Dropout(0.2, name='drop_3')(x)

    # Per-disease output heads (binary probability)
    outputs = []
    for disease in DISEASE_OUTPUTS:
        branch = layers.Dense(32, activation='relu', name=f'{disease}_dense')(x)
        out    = layers.Dense(1, activation='sigmoid', name=disease)(branch)
        outputs.append(out)

    model = keras.Model(inputs=inputs, outputs=outputs, name='DeepHealthPredictor')

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss={d: 'binary_crossentropy' for d in DISEASE_OUTPUTS},
        metrics={d: ['accuracy', 'AUC'] for d in DISEASE_OUTPUTS},
    )
    return model


def train(X_train: np.ndarray, y_dict: dict, epochs: int = 50, batch_size: int = 64) -> dict:
    """
    Train the deep model.
    X_train: (n, INPUT_DIM)
    y_dict:  { 'cardiovascular': array, 'diabetes': array, ... }
    """
    if not TF_AVAILABLE:
        print("TensorFlow not available — skipping deep model training.")
        return {'error': 'TensorFlow not available'}

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    model = build_model()

    cb = [
        callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        callbacks.ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-6),
        callbacks.ModelCheckpoint(MODEL_PATH, save_best_only=True),
    ]

    history = model.fit(
        X_train, y_dict,
        epochs          = epochs,
        batch_size      = batch_size,
        validation_split = 0.15,
        callbacks        = cb,
        verbose          = 1,
    )

    # Extract final metrics
    final_metrics = {}
    for k, v in history.history.items():
        final_metrics[k] = round(float(v[-1]), 4)

    model.save(MODEL_PATH)
    print(f"✅ Deep model saved → {MODEL_PATH}")
    return final_metrics


def predict(features: dict) -> dict:
    """
    Run inference on a single patient feature dict.
    Returns per-disease risk probabilities.
    """
    feature_vector = _features_to_array(features)

    if TF_AVAILABLE and os.path.exists(MODEL_PATH):
        model    = keras.models.load_model(MODEL_PATH)
        preds    = model.predict(feature_vector, verbose=0)
        return {
            disease: {
                'probability': round(float(preds[i][0][0]), 4),
                'risk_level':  _prob_to_level(float(preds[i][0][0])),
            }
            for i, disease in enumerate(DISEASE_OUTPUTS)
        }
    else:
        # Fallback: heuristic predictions
        return _heuristic_predict(features)


def _features_to_array(f: dict) -> np.ndarray:
    """Convert feature dict → normalized numpy array"""
    activity_map = {'sedentary': 0, 'lightly_active': 1,
                    'moderately_active': 2, 'very_active': 3, 'extra_active': 4}
    row = [
        float(f.get('age', 30))               / 100,
        float(f.get('bmi', 22))               / 50,
        float(f.get('systolic', 120))          / 200,
        float(f.get('diastolic', 80))          / 150,
        float(f.get('heart_rate', 70))         / 200,
        float(f.get('glucose', 90))            / 300,
        float(f.get('cholesterol_total', 190)) / 400,
        float(f.get('cholesterol_hdl', 55))    / 100,
        float(f.get('cholesterol_ldl', 110))   / 250,
        float(f.get('triglycerides', 130))     / 500,
        float(f.get('sleep_hours', 7))         / 12,
        float(f.get('stress_level', 3))        / 10,
        float(activity_map.get(f.get('activity', 'moderately_active'), 2)) / 4,
        float(f.get('smoking', 0)),
        float(f.get('alcohol', 0))             / 3,
    ]
    return np.array([row], dtype=np.float32)


def _prob_to_level(p: float) -> str:
    if p < 0.20: return 'low'
    if p < 0.45: return 'moderate'
    if p < 0.70: return 'high'
    return 'critical'


def _heuristic_predict(f: dict) -> dict:
    """Rule-based fallback when TF model is unavailable"""
    sys_bp  = float(f.get('systolic', 120))
    glucose = float(f.get('glucose', 90))
    bmi     = float(f.get('bmi', 22))
    chol    = float(f.get('cholesterol_total', 190))
    age     = float(f.get('age', 30))

    def level_and_prob(score):
        p = min(score / 100, 1.0)
        return {'probability': round(p, 4), 'risk_level': _prob_to_level(p)}

    cv_score = (
        (20 if sys_bp >= 140 else 10 if sys_bp >= 130 else 0) +
        (15 if chol >= 240 else 8 if chol >= 200 else 0) +
        (10 if age > 60 else 5 if age > 45 else 0)
    )
    db_score = (
        (50 if glucose >= 126 else 25 if glucose >= 100 else 0) +
        (20 if bmi >= 30 else 10 if bmi >= 25 else 0)
    )
    return {
        'cardiovascular':    level_and_prob(cv_score),
        'diabetes':          level_and_prob(db_score),
        'hypertension':      level_and_prob(20 if sys_bp >= 140 else 10 if sys_bp >= 130 else 5),
        'obesity':           level_and_prob(80 if bmi >= 35 else 50 if bmi >= 30 else 20 if bmi >= 25 else 5),
        'metabolic_syndrome': level_and_prob((cv_score + db_score) / 2),
    }
