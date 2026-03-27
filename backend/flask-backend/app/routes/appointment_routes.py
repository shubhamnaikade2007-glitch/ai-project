"""
HealthFit AI - Appointment Routes
Book, view, update, and cancel doctor appointments
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from app import db
from app.models.appointment import Appointment, Doctor
from app.models.user import User

appointment_bp = Blueprint('appointments', __name__)


@appointment_bp.route('/', methods=['GET'])
@jwt_required()
def get_appointments():
    """
    Get appointments for the current user.
    Patients see their own; doctors see their patient appointments.
    Query params: status, upcoming_only (bool), limit
    """
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    
    status       = request.args.get('status')
    upcoming     = request.args.get('upcoming_only', 'false').lower() == 'true'
    limit        = int(request.args.get('limit', 50))
    
    if user.role == 'doctor':
        query = Appointment.query.filter_by(doctor_id=user_id)
    else:
        query = Appointment.query.filter_by(patient_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if upcoming:
        query = query.filter(Appointment.appointment_date >= date.today())
    
    appointments = query.order_by(
        Appointment.appointment_date,
        Appointment.appointment_time
    ).limit(limit).all()
    
    return jsonify({
        'appointments': [a.to_dict() for a in appointments],
        'count': len(appointments),
    }), 200


@appointment_bp.route('/', methods=['POST'])
@jwt_required()
def book_appointment():
    """
    Book a new appointment.
    Body: { doctor_id, appointment_date, appointment_time, type, reason, duration_min? }
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required = ['doctor_id', 'appointment_date', 'appointment_time']
    missing  = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f'Missing: {", ".join(missing)}'}), 400
    
    # Validate doctor exists
    doctor = User.query.filter_by(id=data['doctor_id'], role='doctor').first()
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    # Parse date and time
    try:
        appt_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        appt_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
    except ValueError:
        return jsonify({'error': 'Date must be YYYY-MM-DD and time HH:MM'}), 400
    
    if appt_date < date.today():
        return jsonify({'error': 'Cannot book appointments in the past'}), 400
    
    # Check for scheduling conflict
    conflict = Appointment.query.filter_by(
        doctor_id        = data['doctor_id'],
        appointment_date = appt_date,
        appointment_time = appt_time,
    ).filter(Appointment.status.in_(['pending', 'confirmed'])).first()
    
    if conflict:
        return jsonify({'error': 'This time slot is already booked'}), 409
    
    appointment = Appointment(
        patient_id       = user_id,
        doctor_id        = data['doctor_id'],
        appointment_date = appt_date,
        appointment_time = appt_time,
        duration_min     = data.get('duration_min', 30),
        type             = data.get('type', 'in_person'),
        reason           = data.get('reason'),
        status           = 'pending',
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({
        'message':     'Appointment booked successfully',
        'appointment': appointment.to_dict(),
    }), 201


@appointment_bp.route('/<int:appt_id>', methods=['GET'])
@jwt_required()
def get_appointment(appt_id: int):
    """Get a single appointment by ID"""
    user_id = int(get_jwt_identity())
    user    = User.query.get(user_id)
    
    appt = Appointment.query.get_or_404(appt_id)
    
    # Check access
    if appt.patient_id != user_id and appt.doctor_id != user_id and user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({'appointment': appt.to_dict()}), 200


@appointment_bp.route('/<int:appt_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appt_id: int):
    """
    Update an appointment (status, notes, diagnosis, etc.)
    Patients can cancel; doctors can confirm/complete/add notes.
    """
    user_id = int(get_jwt_identity())
    user    = User.query.get(user_id)
    data    = request.get_json()
    
    appt = Appointment.query.get_or_404(appt_id)
    
    # Check access
    if appt.patient_id != user_id and appt.doctor_id != user_id and user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Patients can only cancel
    if user.role == 'patient':
        if data.get('status') and data['status'] != 'cancelled':
            return jsonify({'error': 'Patients can only cancel appointments'}), 403
    
    # Update allowed fields
    updatable = ['status', 'notes', 'diagnosis', 'prescription', 'reason', 'type']
    for field in updatable:
        if field in data:
            setattr(appt, field, data[field])
    
    if data.get('follow_up_date'):
        try:
            appt.follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'follow_up_date must be YYYY-MM-DD'}), 400
    
    db.session.commit()
    
    return jsonify({
        'message':     'Appointment updated',
        'appointment': appt.to_dict(),
    }), 200


@appointment_bp.route('/<int:appt_id>', methods=['DELETE'])
@jwt_required()
def cancel_appointment(appt_id: int):
    """Cancel (soft delete) an appointment"""
    user_id = int(get_jwt_identity())
    appt    = Appointment.query.get_or_404(appt_id)
    
    if appt.patient_id != user_id and appt.doctor_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    appt.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'message': 'Appointment cancelled'}), 200


@appointment_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    """Get list of all available doctors"""
    specialization = request.args.get('specialization')
    
    query = Doctor.query
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
    
    doctors = query.order_by(Doctor.rating.desc()).all()
    
    return jsonify({
        'doctors': [d.to_dict() for d in doctors],
        'count':   len(doctors),
    }), 200


@appointment_bp.route('/available-slots', methods=['GET'])
@jwt_required()
def get_available_slots():
    """
    Get available time slots for a doctor on a specific date.
    Query params: doctor_id (required), date (required, YYYY-MM-DD)
    """
    doctor_id = request.args.get('doctor_id', type=int)
    date_str  = request.args.get('date')
    
    if not doctor_id or not date_str:
        return jsonify({'error': 'doctor_id and date are required'}), 400
    
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'date must be YYYY-MM-DD'}), 400
    
    # Get doctor's slot duration
    doctor_info = Doctor.query.filter_by(user_id=doctor_id).first()
    slot_mins   = doctor_info.slot_duration_min if doctor_info else 30
    
    # Generate all possible slots (9 AM to 5 PM)
    all_slots = []
    for hour in range(9, 17):
        for minute in range(0, 60, slot_mins):
            all_slots.append(f"{hour:02d}:{minute:02d}")
    
    # Get booked slots
    booked = Appointment.query.filter_by(
        doctor_id        = doctor_id,
        appointment_date = target_date,
    ).filter(Appointment.status.in_(['pending', 'confirmed'])).all()
    
    booked_times = {str(a.appointment_time)[:5] for a in booked}
    
    available = [s for s in all_slots if s not in booked_times]
    
    return jsonify({
        'date':      date_str,
        'available': available,
        'booked':    list(booked_times),
    }), 200
