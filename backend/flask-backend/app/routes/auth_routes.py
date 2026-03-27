"""
HealthFit AI - Authentication Routes
Handles register, login, logout, and current user endpoints
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from datetime import datetime
from app import db
from app.models.user import User, UserProfile

auth_bp = Blueprint('auth', __name__)

# In-memory token blocklist (use Redis in production)
_blocklist = set()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.
    Body: { email, password, first_name, last_name, role?, date_of_birth?, gender?, phone? }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required = ['email', 'password', 'first_name', 'last_name']
    missing  = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
    
    # Check password length
    if len(data['password']) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email'].lower()).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Parse date_of_birth if provided
    dob = None
    if data.get('date_of_birth'):
        try:
            dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'date_of_birth must be YYYY-MM-DD format'}), 400
    
    # Create user
    user = User(
        email      = data['email'].lower().strip(),
        first_name = data['first_name'].strip(),
        last_name  = data['last_name'].strip(),
        role       = data.get('role', 'patient'),
        gender     = data.get('gender'),
        phone      = data.get('phone'),
        date_of_birth = dob,
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.flush()  # Get user.id before commit
    
    # Create empty profile
    profile = UserProfile(
        user_id        = user.id,
        height_cm      = data.get('height_cm'),
        weight_kg      = data.get('weight_kg'),
        fitness_goal   = data.get('fitness_goal', 'general_wellness'),
        activity_level = data.get('activity_level', 'moderately_active'),
    )
    db.session.add(profile)
    db.session.commit()
    
    # Generate tokens
    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message':      'Account created successfully',
        'user':         user.to_dict(include_profile=True),
        'access_token': access_token,
        'refresh_token': refresh_token,
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens.
    Body: { email, password }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email    = data.get('email', '').lower().strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Find user
    user = User.query.filter_by(email=email, is_active=True).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate tokens
    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message':       'Login successful',
        'user':          user.to_dict(include_profile=True),
        'access_token':  access_token,
        'refresh_token': refresh_token,
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Use refresh token to get a new access token"""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Invalidate the current JWT token"""
    jti = get_jwt()['jti']
    _blocklist.add(jti)
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get the currently authenticated user's data"""
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify({'user': user.to_dict(include_profile=True)}), 200


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update the current user's profile"""
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    data    = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update user fields
    updatable = ['first_name', 'last_name', 'phone', 'gender', 'avatar_url']
    for field in updatable:
        if field in data:
            setattr(user, field, data[field])
    
    if 'date_of_birth' in data and data['date_of_birth']:
        try:
            user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'date_of_birth must be YYYY-MM-DD'}), 400
    
    # Update profile fields
    if user.profile:
        profile_fields = ['height_cm', 'weight_kg', 'blood_type', 'allergies',
                          'medications', 'medical_history', 'fitness_goal',
                          'activity_level', 'emergency_contact_name', 'emergency_contact_phone']
        for field in profile_fields:
            if field in data:
                setattr(user.profile, field, data[field])
    
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'user': user.to_dict(include_profile=True)}), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change the current user's password"""
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    data    = request.get_json()
    
    if not user.check_password(data.get('current_password', '')):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    new_password = data.get('new_password', '')
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200
