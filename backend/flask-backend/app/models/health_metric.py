"""
HealthFit AI - Health Metrics Database Models - FIXED ✅
SQLAlchemy models + Smartwatch sync methods
"""
from datetime import datetime
from app import db

METRIC_TYPES = {
    'heart_rate': {'unit': 'bpm', 'normal_min': 60, 'normal_max': 100},
    'blood_pressure_systolic': {'unit': 'mmHg', 'normal_min': 90, 'normal_max': 120},
    'blood_pressure_diastolic': {'unit': 'mmHg', 'normal_min': 60, 'normal_max': 80},
    'blood_glucose': {'unit': 'mg/dL', 'normal_min': 70, 'normal_max': 100},
    'bmi': {'unit': 'kg/m²', 'normal_min': 18.5, 'normal_max': 24.9},
    'steps_count': {'unit': 'steps', 'normal_min': 7500},
    'sleep_hours': {'unit': 'hours', 'normal_min': 7, 'normal_max': 9},
    'sleep_quality': {'unit': '/100', 'normal_min': 70},
    'calories_burned': {'unit': 'kcal'},
    'water_intake_ml': {'unit': 'ml', 'normal_min': 2000},
}


class HealthMetric(db.Model):
    __tablename__ = 'health_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    metric_type = db.Column(db.Enum(*METRIC_TYPES.keys()), nullable=False, index=True)
    value = db.Column(db.Numeric(10, 3), nullable=False)
    unit = db.Column(db.String(50))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    source = db.Column(db.Enum('manual', 'wearable', 'device', 'ai_estimated'), default='manual')
    notes = db.Column(db.String(500))
    
    user = db.relationship('User', back_populates='health_metrics')
    
    @classmethod
    def create_or_update(cls, user_id, metric_type, value, source='manual', recorded_at=None):
        """🔧 Smartwatch: Auto-add/update metric"""
        metric = cls.query.filter_by(
            user_id=user_id, metric_type=metric_type
        ).order_by(cls.recorded_at.desc()).first()
        
        if metric:
            metric.value = value
            metric.source = source
            metric.recorded_at = recorded_at or datetime.utcnow()
        else:
            metric = cls(
                user_id=user_id,
                metric_type=metric_type,
                value=float(value),
                source=source,
                recorded_at=recorded_at or datetime.utcnow()
            )
            db.session.add(metric)
        db.session.commit()
        return metric
    
    @property
    def is_normal(self) -> bool | None:
        meta = METRIC_TYPES.get(self.metric_type)
        if not meta: return None
        val = float(self.value)
        if meta['normal_min'] is not None and val < meta['normal_min']: return False
        if meta['normal_max'] is not None and val > meta['normal_max']: return False
        return True
    
    @property
    def status(self) -> str:
        meta = METRIC_TYPES.get(self.metric_type, {})
        val = float(self.value)
        if meta.get('normal_min') is not None and val < meta['normal_min']: return 'low'
        if meta.get('normal_max') is not None and val > meta['normal_max']: return 'high'
        return 'normal'
    
    def to_dict(self):
        return {
            'id': self.id,
            'metric_type': self.metric_type,
            'value': float(self.value),
            'unit': self.unit or METRIC_TYPES.get(self.metric_type, {}).get('unit'),
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'source': self.source,
            'status': self.status,
        }
    
    def __repr__(self):
        return f'<HealthMetric {self.metric_type}={self.value}>'

class OrganHealthScore(db.Model):
    __tablename__ = 'organ_health_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organ = db.Column(db.Enum('heart','liver','kidneys','lungs','brain','immune_system','digestive','overall'))
    score = db.Column(db.Numeric(5, 2), nullable=False)
    risk_level = db.Column(db.Enum('low','moderate','high','critical'), default='low')
    computed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'organ': self.organ,
            'score': float(self.score),
            'risk_level': self.risk_level,
        }

