"""
HealthFit AI - User Database Model
SQLAlchemy model for the users and user_profiles tables
"""
from datetime import datetime
import bcrypt
from app import db


class User(db.Model):
    """
    Represents a user account (patient, doctor, or admin).
    Handles authentication and basic profile data.
    """
    __tablename__ = 'users'
    
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name    = db.Column(db.String(100), nullable=False)
    last_name     = db.Column(db.String(100), nullable=False)
    role          = db.Column(db.Enum('patient', 'doctor', 'admin'), default='patient')
    date_of_birth = db.Column(db.Date)
    gender        = db.Column(db.Enum('male', 'female', 'other'))
    phone         = db.Column(db.String(20))
    avatar_url    = db.Column(db.String(500))
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile       = db.relationship('UserProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    health_metrics = db.relationship('HealthMetric', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')
    patient_appointments = db.relationship('Appointment', foreign_keys='Appointment.patient_id', back_populates='patient', lazy='dynamic')
    
    def set_password(self, password: str) -> None:
        """Hash and store a password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int | None:
        """Calculate age from date_of_birth"""
        if not self.date_of_birth:
            return None
        today = datetime.utcnow().date()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    def to_dict(self, include_profile: bool = False) -> dict:
        """Serialize user to a dictionary"""
        data = {
            'id':         self.id,
            'email':      self.email,
            'first_name': self.first_name,
            'last_name':  self.last_name,
            'full_name':  self.full_name,
            'role':       self.role,
            'age':        self.age,
            'gender':     self.gender,
            'phone':      self.phone,
            'avatar_url': self.avatar_url,
            'is_active':  self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_profile and self.profile:
            data['profile'] = self.profile.to_dict()
        return data
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class UserProfile(db.Model):
    """
    Extended health profile for a user.
    Stores physical stats, medical history, and fitness goals.
    """
    __tablename__ = 'user_profiles'
    
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    height_cm       = db.Column(db.Numeric(5, 2))
    weight_kg       = db.Column(db.Numeric(5, 2))
    blood_type      = db.Column(db.Enum('A+','A-','B+','B-','AB+','AB-','O+','O-'))
    allergies       = db.Column(db.Text)
    medications     = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    emergency_contact_name  = db.Column(db.String(200))
    emergency_contact_phone = db.Column(db.String(20))
    fitness_goal    = db.Column(db.Enum('weight_loss','muscle_gain','endurance','flexibility','general_wellness'), default='general_wellness')
    activity_level  = db.Column(db.Enum('sedentary','lightly_active','moderately_active','very_active','extra_active'), default='moderately_active')
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship back to user
    user = db.relationship('User', back_populates='profile')
    
    @property
    def bmi(self) -> float | None:
        """Calculate BMI from height and weight"""
        if self.height_cm and self.weight_kg and float(self.height_cm) > 0:
            height_m = float(self.height_cm) / 100
            return round(float(self.weight_kg) / (height_m ** 2), 2)
        return None
    
    def to_dict(self) -> dict:
        return {
            'height_cm':       float(self.height_cm) if self.height_cm else None,
            'weight_kg':       float(self.weight_kg) if self.weight_kg else None,
            'bmi':             self.bmi,
            'blood_type':      self.blood_type,
            'allergies':       self.allergies,
            'medications':     self.medications,
            'medical_history': self.medical_history,
            'emergency_contact_name':  self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'fitness_goal':    self.fitness_goal,
            'activity_level':  self.activity_level,
        }
    
    def __repr__(self):
        return f'<UserProfile user_id={self.user_id}>'
