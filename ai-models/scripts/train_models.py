"""
HealthFit AI - Model Training Script
Generates synthetic training data and trains all AI models.
Run with: python scripts/train_models.py
"""
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("\n" + "="*55)
print("  HealthFit AI - Model Training Script")
print("="*55)

# ─── 1. Health Risk Classifier ──────────────────────────────
print("\n[1/3] Training Health Risk Classifier (sklearn)...")
try:
    from sklearn_models.health_risk_classifier.health_risk_predictor import (
        HealthRiskPredictor, generate_synthetic_training_data
    )

    X, y = generate_synthetic_training_data(n=8000)
    print(f"  Generated {len(X)} training samples")
    print(f"  Label distribution: { {l: int(np.sum(y==l)) for l in ['low','moderate','high','critical']} }")

    predictor = HealthRiskPredictor()
    metrics   = predictor.train(X, y)
    print(f"  ✅ Trained! CV Accuracy: {metrics['cv_accuracy_mean']:.4f} ± {metrics['cv_accuracy_std']:.4f}")

    # Test prediction
    test_features = {
        'age': 55, 'bmi': 31.2, 'systolic': 145, 'diastolic': 92,
        'glucose': 115, 'heart_rate': 82, 'cholesterol_total': 240,
        'sleep_hours': 5.5, 'stress_level': 7, 'activity': 'sedentary',
    }
    result = predictor.predict_single(test_features)
    print(f"  Sample prediction: risk_level={result['risk_level']}, score={result['risk_score']}")

except Exception as e:
    print(f"  ❌ Health risk classifier training failed: {e}")

# ─── 2. Stress Detector ─────────────────────────────────────
print("\n[2/3] Training Stress Detector (sklearn GBM)...")
try:
    from tensorflow_models.stress_detector.stress_detector import train_sklearn

    rng = np.random.default_rng(42)
    n   = 5000
    X_stress = np.stack([
        rng.uniform(10, 100, n),   # hrv_ms
        rng.uniform(50, 120, n),   # resting_hr
        rng.uniform(20, 100, n),   # sleep_score
        rng.uniform(4, 10, n),     # sleep_hours
        rng.uniform(0, 90, n),     # activity_minutes
        rng.uniform(0, 10, n),     # subjective_stress
        rng.uniform(20, 100, n),   # recovery_score
    ], axis=1)

    # Stress score: high HR, low HRV, low sleep → high stress
    y_stress = np.clip(
        100 - X_stress[:, 0] * 0.5   # HRV negative contribution
        + (X_stress[:, 1] - 70) * 0.5  # HR positive contribution
        - X_stress[:, 3] * 3           # Sleep hours negative
        + X_stress[:, 5] * 5           # Subjective stress
        + rng.normal(0, 5, n),
        0, 100
    )

    metrics = train_sklearn(X_stress, y_stress)
    print(f"  ✅ Trained! R² Score: {metrics.get('r2_score', 'N/A')}")

except Exception as e:
    print(f"  ❌ Stress detector training failed: {e}")

# ─── 3. TensorFlow models (optional) ────────────────────────
print("\n[3/3] Training TensorFlow models (optional)...")
try:
    import tensorflow as tf
    print(f"  TensorFlow version: {tf.__version__}")

    from tensorflow_models.health_predictor.deep_health_predictor import (
        train as train_deep, INPUT_DIM, DISEASE_OUTPUTS
    )

    rng = np.random.default_rng(42)
    n   = 10000
    X_deep = rng.uniform(0, 1, (n, INPUT_DIM)).astype(np.float32)

    # Synthetic multi-label targets
    y_dict = {}
    for i, disease in enumerate(DISEASE_OUTPUTS):
        prob = np.clip(X_deep[:, i % INPUT_DIM] + rng.normal(0, 0.1, n), 0, 1)
        y_dict[disease] = (prob > 0.5).astype(np.float32)

    metrics = train_deep(X_deep, y_dict, epochs=5)
    print(f"  ✅ Deep model trained!")

except ImportError:
    print("  ⚠️  TensorFlow not installed — skipping deep models")
    print("  Install with: pip install tensorflow")
except Exception as e:
    print(f"  ❌ Deep model training failed: {e}")

print("\n" + "="*55)
print("  Training Complete!")
print("="*55)
print("\nModels saved to: ai-models/saved_models/")
print("Start AI service: python ai-models/api/main.py\n")
