"""
HealthFit AI - Health Risk Classifier (Scikit-learn)
A Random Forest classifier that predicts the overall health risk level
(low / moderate / high / critical) based on biometric features.
"""
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from ai_models.utils.base_model import BaseHealthModel


# Features the model expects
FEATURE_COLUMNS = [
    'age',
    'bmi',
    'systolic_bp',
    'diastolic_bp',
    'heart_rate',
    'blood_glucose',
    'cholesterol_total',
    'sleep_hours',
    'stress_level',
    'activity_score',    # encoded: sedentary=0, lightly=1, moderately=2, very=3, extra=4
    'smoking',           # 0 = no, 1 = yes
    'alcohol',           # 0-3 scale
]

RISK_LABELS = ['low', 'moderate', 'high', 'critical']


class HealthRiskPredictor(BaseHealthModel):
    """
    Random Forest-based health risk classifier.
    Predicts risk across 4 categories and provides per-disease risk breakdown.
    """

    def __init__(self):
        super().__init__(model_name='health_risk_classifier', version='2.0')
        self.label_encoder = LabelEncoder()
        self.feature_names = FEATURE_COLUMNS

    def _build_pipeline(self) -> Pipeline:
        """Build sklearn Pipeline with scaler + classifier"""
        return Pipeline([
            ('scaler', StandardScaler()),
            ('clf', RandomForestClassifier(
                n_estimators=200,
                max_depth=8,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1,
            )),
        ])

    def train(self, X: np.ndarray, y: np.ndarray) -> dict:
        """
        Train the classifier.
        X: array of shape (n_samples, len(FEATURE_COLUMNS))
        y: array of risk labels ('low', 'moderate', 'high', 'critical')
        """
        y_enc   = self.label_encoder.fit_transform(y)
        pipeline = self._build_pipeline()
        pipeline.fit(X, y_enc)
        self.model      = pipeline
        self.is_trained = True
        self.trained_at = datetime.utcnow().isoformat()

        # Cross-validation score
        cv_scores = cross_val_score(pipeline, X, y_enc, cv=5, scoring='accuracy')
        metrics   = {
            'cv_accuracy_mean': round(cv_scores.mean(), 4),
            'cv_accuracy_std':  round(cv_scores.std(), 4),
        }
        self.save()
        return metrics

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict risk labels for input array"""
        if not self.is_trained:
            self.load()
        y_enc = self.model.predict(X)
        return self.label_encoder.inverse_transform(y_enc)

    def predict_proba(self, X: np.ndarray) -> dict:
        """
        Predict probabilities for each risk class.
        Returns dict: { 'low': 0.7, 'moderate': 0.2, ... }
        """
        if not self.is_trained:
            self.load()
        proba   = self.model.predict_proba(X)[0]
        classes = self.label_encoder.classes_
        return {cls: round(float(prob), 4) for cls, prob in zip(classes, proba)}

    def predict_single(self, features: dict) -> dict:
        """
        Predict risk for a single patient record.
        features: dict with keys matching FEATURE_COLUMNS

        Returns full prediction with per-disease breakdown.
        """
        # Build feature vector with defaults for missing values
        row = [
            float(features.get('age',               30)),
            float(features.get('bmi',               22)),
            float(features.get('systolic',          120)),
            float(features.get('diastolic',          80)),
            float(features.get('heart_rate',         70)),
            float(features.get('glucose',            90)),
            float(features.get('cholesterol_total', 190)),
            float(features.get('sleep_hours',         7)),
            float(features.get('stress_level',        3)),
            _encode_activity(features.get('activity', 'moderately_active')),
            float(features.get('smoking',             0)),
            float(features.get('alcohol',             0)),
        ]
        X = np.array([row])

        try:
            label      = self.predict(X)[0]
            proba_dict = self.predict_proba(X)
        except Exception:
            # Model not available — use rule-based
            return _rule_based_predict(features)

        # Per-disease risk breakdown (simple heuristics layered on top)
        disease_risks = _calculate_disease_risks(features)

        overall_score = proba_dict.get('high', 0) * 60 + proba_dict.get('critical', 0) * 100 + \
                        proba_dict.get('moderate', 0) * 30

        return {
            'risk_level':     label,
            'risk_score':     round(overall_score, 1),
            'probabilities':  proba_dict,
            'disease_risks':  disease_risks,
            'alerts':         _generate_alerts(features, disease_risks),
            'recommendations': _generate_recommendations(features, disease_risks),
            'model':          'HealthRiskClassifier_v2',
            'confidence':     round(max(proba_dict.values()) * 100, 1),
        }


# ─── helpers ──────────────────────────────────────────────────────────────────

def _encode_activity(level: str) -> float:
    mapping = {
        'sedentary': 0, 'lightly_active': 1,
        'moderately_active': 2, 'very_active': 3, 'extra_active': 4,
    }
    return float(mapping.get(level, 2))


def _calculate_disease_risks(f: dict) -> dict:
    """Compute per-disease risk scores (0-100) from biometrics"""
    age      = float(f.get('age',       30))
    bmi      = float(f.get('bmi',       22))
    sys_bp   = float(f.get('systolic', 120))
    dia_bp   = float(f.get('diastolic', 80))
    glucose  = float(f.get('glucose',   90))
    hr       = float(f.get('heart_rate', 70))
    chol     = float(f.get('cholesterol_total', 190))

    # Cardiovascular
    cv = 0
    if sys_bp >= 140: cv += 35
    elif sys_bp >= 130: cv += 20
    elif sys_bp >= 120: cv += 8
    if chol >= 240: cv += 20
    elif chol >= 200: cv += 10
    if age > 60: cv += 15
    elif age > 45: cv += 8
    if hr > 100: cv += 10

    # Type 2 Diabetes
    diab = 0
    if glucose >= 126: diab += 50
    elif glucose >= 100: diab += 25
    if bmi >= 30: diab += 25
    elif bmi >= 25: diab += 12
    if age > 45: diab += 10

    # Hypertension
    htn = 0
    if sys_bp >= 140 or dia_bp >= 90: htn += 60
    elif sys_bp >= 130 or dia_bp >= 80: htn += 30
    elif sys_bp >= 120: htn += 15
    if bmi >= 30: htn += 15
    if age > 50: htn += 10

    # Obesity
    if bmi >= 40: obes = 90
    elif bmi >= 35: obes = 70
    elif bmi >= 30: obes = 50
    elif bmi >= 25: obes = 20
    else: obes = 5

    return {
        'cardiovascular': min(cv, 100),
        'diabetes':       min(diab, 100),
        'hypertension':   min(htn, 100),
        'obesity':        min(obes, 100),
    }


def _generate_alerts(f: dict, risks: dict) -> list[str]:
    alerts = []
    if risks.get('cardiovascular', 0) > 40:
        alerts.append('Elevated cardiovascular risk detected. Consult a cardiologist.')
    if float(f.get('systolic', 0)) >= 140:
        alerts.append(f"Blood pressure {f['systolic']}/{f.get('diastolic', '')} mmHg is Stage 2 hypertension.")
    if float(f.get('glucose', 0)) >= 126:
        alerts.append('Fasting glucose ≥126 mg/dL — diabetes screening recommended.')
    elif float(f.get('glucose', 0)) >= 100:
        alerts.append('Pre-diabetic fasting glucose range (100-125 mg/dL).')
    if float(f.get('bmi', 0)) >= 30:
        alerts.append(f"BMI {f['bmi']:.1f} is in the obese range.")
    return alerts


def _generate_recommendations(f: dict, risks: dict) -> list[str]:
    recs = []
    if risks.get('cardiovascular', 0) > 20:
        recs.extend(['150 min moderate cardio per week', 'Reduce sodium < 2,300 mg/day', 'DASH diet recommended'])
    if risks.get('diabetes', 0) > 20:
        recs.extend(['Monitor fasting glucose quarterly', 'Reduce added sugar and refined carbs'])
    if float(f.get('bmi', 22)) >= 25:
        recs.append('Target 5-10% weight reduction for significant health benefit')
    recs.extend(['7-9 hours quality sleep nightly', 'Annual comprehensive health panel'])
    return list(dict.fromkeys(recs))  # deduplicate while preserving order


def _rule_based_predict(f: dict) -> dict:
    """Pure rule-based fallback with no model dependency"""
    risks  = _calculate_disease_risks(f)
    overall = sum(risks.values()) / len(risks)
    if overall < 20: level = 'low'
    elif overall < 40: level = 'moderate'
    elif overall < 65: level = 'high'
    else: level = 'critical'
    return {
        'risk_level':      level,
        'risk_score':      round(overall, 1),
        'disease_risks':   risks,
        'alerts':          _generate_alerts(f, risks),
        'recommendations': _generate_recommendations(f, risks),
        'model':           'rule_based',
        'confidence':      70.0,
    }


def generate_synthetic_training_data(n: int = 5000) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic training data for the model.
    Called by scripts/train_models.py.
    """
    rng = np.random.default_rng(42)

    ages      = rng.integers(18, 80, n).astype(float)
    bmis      = rng.normal(26, 5, n).clip(15, 45)
    systolics = rng.normal(122, 18, n).clip(80, 200)
    diasts    = rng.normal(79, 12, n).clip(50, 130)
    hrs       = rng.normal(72, 12, n).clip(45, 130)
    glucoses  = rng.normal(95, 18, n).clip(60, 200)
    cholests  = rng.normal(195, 35, n).clip(120, 320)
    sleeps    = rng.normal(7, 1.2, n).clip(3, 10)
    stresses  = rng.uniform(0, 10, n)
    activities = rng.integers(0, 5, n).astype(float)
    smokings  = rng.choice([0, 1], n, p=[0.75, 0.25]).astype(float)
    alcohols  = rng.choice([0, 1, 2, 3], n, p=[0.5, 0.25, 0.15, 0.10]).astype(float)

    X = np.stack([ages, bmis, systolics, diasts, hrs, glucoses,
                  cholests, sleeps, stresses, activities, smokings, alcohols], axis=1)

    # Label based on heuristics
    labels = []
    for i in range(n):
        score = 0
        if systolics[i] >= 140: score += 3
        elif systolics[i] >= 130: score += 1
        if glucoses[i] >= 126: score += 3
        elif glucoses[i] >= 100: score += 1
        if bmis[i] >= 35: score += 2
        elif bmis[i] >= 30: score += 1
        if ages[i] > 60: score += 2
        if smokings[i] == 1: score += 2
        if cholests[i] >= 240: score += 2
        if sleeps[i] < 6: score += 1
        if stresses[i] > 7: score += 1

        if score >= 8:   labels.append('critical')
        elif score >= 5: labels.append('high')
        elif score >= 2: labels.append('moderate')
        else:            labels.append('low')

    return X, np.array(labels)
