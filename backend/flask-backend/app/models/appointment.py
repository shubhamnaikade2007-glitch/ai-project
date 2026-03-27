"""
HealthFit AI - Appointment Database Model
SQLAlchemy model for the appointments table
"""
from datetime import datetime
from app import db


class Appointment(db.Model):
    """
    Represents a scheduled appointment between a patient and doctor.
    Supports in-person, video, and phone consultations.
    """
    __tablename__ = 'appointments'
    
    id               = db.Column(db.Integer, primary_key=True)
    patient_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    doctor_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    appointment_date = db.Column(db.Date, nullable=False, index=True)
    appointment_time = db.Column(db.Time, nullable=False)
    duration_min     = db.Column(db.Integer, default=30)
    status           = db.Column(
        db.Enum('pending', 'confirmed', 'completed', 'cancelled', 'no_show'),
        default='pending', index=True
    )
    type             = db.Column(db.Enum('in_person', 'video_call', 'phone'), default='in_person')
    reason           = db.Column(db.Text)
    notes            = db.Column(db.Text)
    diagnosis        = db.Column(db.Text)
    prescription     = db.Column(db.Text)
    follow_up_date   = db.Column(db.Date)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('User', foreign_keys=[patient_id], back_populates='patient_appointments')
    doctor  = db.relationship('User', foreign_keys=[doctor_id])
    
    @property
    def is_upcoming(self) -> bool:
        """Check if appointment is in the future"""
        today = datetime.utcnow().date()
        return self.appointment_date > today or (
            self.appointment_date == today and
            self.appointment_time > datetime.utcnow().time()
        )
    
    def to_dict(self, include_names: bool = True) -> dict:
        data = {
            'id':               self.id,
            'patient_id':       self.patient_id,
            'doctor_id':        self.doctor_id,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': str(self.appointment_time) if self.appointment_time else None,
            'duration_min':     self.duration_min,
            'status':           self.status,
            'type':             self.type,
            'reason':           self.reason,
            'notes':            self.notes,
            'diagnosis':        self.diagnosis,
            'prescription':     self.prescription,
            'follow_up_date':   self.follow_up_date.isoformat() if self.follow_up_date else None,
            'is_upcoming':      self.is_upcoming,
            'created_at':       self.created_at.isoformat() if self.created_at else None,
        }
        if include_names:
            if self.patient:
                data['patient_name'] = self.patient.full_name
            if self.doctor:
                data['doctor_name'] = self.doctor.full_name
        return data
    
    def __repr__(self):
        return f'<Appointment patient={self.patient_id} doctor={self.doctor_id} date={self.appointment_date}>'


class Doctor(db.Model):
    """
    Doctor-specific information, linked to a User with role='doctor'.
    """
    __tablename__ = 'doctors'
    
    id                   = db.Column(db.Integer, primary_key=True)
    user_id              = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    specialization       = db.Column(db.String(200), nullable=False, index=True)
    license_number       = db.Column(db.String(100), unique=True, nullable=False)
    hospital_affiliation = db.Column(db.String(300))
    years_experience     = db.Column(db.Integer, default=0)
    consultation_fee     = db.Column(db.Numeric(10, 2), default=0)
    rating               = db.Column(db.Numeric(3, 2), default=0)
    bio                  = db.Column(db.Text)
    available_days       = db.Column(db.String(200))   # comma-separated
    slot_duration_min    = db.Column(db.Integer, default=30)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = db.relationship('User', foreign_keys=[user_id])
    
    def to_dict(self) -> dict:
        data = {
            'id':                   self.id,
            'user_id':              self.user_id,
            'specialization':       self.specialization,
            'license_number':       self.license_number,
            'hospital_affiliation': self.hospital_affiliation,
            'years_experience':     self.years_experience,
            'consultation_fee':     float(self.consultation_fee) if self.consultation_fee else 0,
            'rating':               float(self.rating) if self.rating else 0,
            'bio':                  self.bio,
            'available_days':       self.available_days.split(',') if self.available_days else [],
            'slot_duration_min':    self.slot_duration_min,
        }
        if self.user:
            data['name']      = self.user.full_name
            data['email']     = self.user.email
            data['avatar_url'] = self.user.avatar_url
        return data
    
    def __repr__(self):
        return f'<Doctor user_id={self.user_id} spec={self.specialization}>'
