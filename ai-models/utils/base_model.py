"""
HealthFit AI - Base Model Utility
Shared base class for all AI models in the system.
Provides common save/load, feature scaling, and evaluation helpers.
"""
import os
import joblib
import numpy as np
from abc import ABC, abstractmethod
from datetime import datetime


class BaseHealthModel(ABC):
    """
    Abstract base class for all HealthFit AI models.
    Provides serialization, versioning, and common interface.
    """

    MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'saved_models')

    def __init__(self, model_name: str, version: str = '1.0'):
        self.model_name  = model_name
        self.version     = version
        self.model       = None
        self.scaler      = None
        self.is_trained  = False
        self.trained_at  = None
        self.feature_names: list[str] = []

        # Create model dir if it doesn't exist
        os.makedirs(self.MODEL_DIR, exist_ok=True)

    @property
    def model_path(self) -> str:
        return os.path.join(self.MODEL_DIR, f"{self.model_name}_v{self.version}.pkl")

    @property
    def scaler_path(self) -> str:
        return os.path.join(self.MODEL_DIR, f"{self.model_name}_scaler_v{self.version}.pkl")

    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> dict:
        """Train the model. Returns metrics dict."""
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Run inference. Returns predictions array."""
        pass

    def save(self) -> str:
        """Persist model and scaler to disk"""
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        joblib.dump({
            'model':         self.model,
            'version':       self.version,
            'feature_names': self.feature_names,
            'trained_at':    self.trained_at,
        }, self.model_path)
        if self.scaler:
            joblib.dump(self.scaler, self.scaler_path)
        print(f"✅ Saved {self.model_name} v{self.version} → {self.model_path}")
        return self.model_path

    def load(self) -> bool:
        """Load model from disk. Returns True if successful."""
        if not os.path.exists(self.model_path):
            print(f"⚠️  Model file not found: {self.model_path}")
            print(f"   Run scripts/train_models.py to generate it.")
            return False
        data = joblib.load(self.model_path)
        self.model         = data['model']
        self.version       = data.get('version', self.version)
        self.feature_names = data.get('feature_names', [])
        self.trained_at    = data.get('trained_at')
        self.is_trained    = True
        if os.path.exists(self.scaler_path):
            self.scaler = joblib.load(self.scaler_path)
        return True

    def preprocess(self, X: np.ndarray) -> np.ndarray:
        """Apply scaler if available"""
        if self.scaler is not None:
            return self.scaler.transform(X)
        return X

    def evaluate(self, X: np.ndarray, y_true: np.ndarray) -> dict:
        """Compute common evaluation metrics"""
        from sklearn.metrics import (accuracy_score, precision_score,
                                     recall_score, f1_score, roc_auc_score)
        y_pred = self.predict(X)
        metrics = {
            'accuracy':  round(accuracy_score(y_true, y_pred), 4),
            'precision': round(precision_score(y_true, y_pred, average='weighted', zero_division=0), 4),
            'recall':    round(recall_score(y_true, y_pred, average='weighted', zero_division=0), 4),
            'f1':        round(f1_score(y_true, y_pred, average='weighted', zero_division=0), 4),
        }
        try:
            if hasattr(self.model, 'predict_proba'):
                proba   = self.model.predict_proba(self.preprocess(X))
                auc     = roc_auc_score(y_true, proba, multi_class='ovr', average='weighted')
                metrics['auc'] = round(auc, 4)
        except Exception:
            pass
        return metrics

    def feature_importance(self) -> dict | None:
        """Return feature importances if supported by the model"""
        if hasattr(self.model, 'feature_importances_') and self.feature_names:
            imps = self.model.feature_importances_
            return {name: round(float(imp), 4)
                    for name, imp in zip(self.feature_names, imps)}
        return None

    def __repr__(self):
        status = f"trained @ {self.trained_at}" if self.is_trained else "not trained"
        return f"<{self.model_name} v{self.version} ({status})>"
