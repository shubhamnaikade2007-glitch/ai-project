"""
HealthFit AI - Fitness Routes
Workout logging, exercise tracking, and fitness analytics
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import text
from app import db

fitness_bp = Blueprint('fitness', __name__)


@fitness_bp.route('/workouts', methods=['GET'])
@jwt_required()
def get_workouts():
    """
    Get workout history for the current user.
    Query params: days (default 30), workout_type, limit
    """
    user_id      = int(get_jwt_identity())
    days         = int(request.args.get('days', 30))
    workout_type = request.args.get('workout_type')
    limit        = int(request.args.get('limit', 50))

    since = datetime.utcnow() - timedelta(days=days)

    with db.engine.connect() as conn:
        params = {'user_id': user_id, 'since': since, 'limit': limit}
        extra  = ""
        if workout_type:
            extra = " AND workout_type = :workout_type"
            params['workout_type'] = workout_type

        result = conn.execute(text(f"""
            SELECT * FROM workouts
            WHERE user_id = :user_id
              AND started_at >= :since
              {extra}
            ORDER BY started_at DESC
            LIMIT :limit
        """), params)
        keys = result.keys()
        rows = result.fetchall()

    workouts = []
    for row in rows:
        w = dict(zip(keys, row))
        # Serialize non-JSON-native types
        for k in ['calories_burned', 'duration_min', 'sets_count', 'reps_count',
                  'heart_rate_avg', 'heart_rate_max']:
            if w.get(k) is not None:
                w[k] = int(w[k])
        for k in ['distance_km', 'weight_kg', 'form_score']:
            if w.get(k) is not None:
                w[k] = float(w[k])
        for k in ['started_at', 'completed_at']:
            if w.get(k) is not None:
                w[k] = w[k].isoformat()
        workouts.append(w)

    return jsonify({'workouts': workouts, 'count': len(workouts)}), 200


@fitness_bp.route('/workouts', methods=['POST'])
@jwt_required()
def log_workout():
    """
    Log a completed workout session.
    Body: { workout_name, workout_type, duration_min, calories_burned?, ... }
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['workout_name', 'workout_type', 'duration_min']
    missing  = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f'Missing: {", ".join(missing)}'}), 400

    valid_types = ['cardio','strength','flexibility','hiit','yoga','swimming',
                   'cycling','running','walking','sports','other']
    if data['workout_type'] not in valid_types:
        return jsonify({'error': f'workout_type must be one of: {valid_types}'}), 400

    started_at = datetime.utcnow()
    if data.get('started_at'):
        try:
            started_at = datetime.fromisoformat(data['started_at'])
        except ValueError:
            pass

    with db.engine.connect() as conn:
        result = conn.execute(text("""
            INSERT INTO workouts
                (user_id, workout_name, workout_type, duration_min, calories_burned,
                 distance_km, sets_count, reps_count, weight_kg,
                 heart_rate_avg, heart_rate_max, intensity,
                 form_score, form_feedback, exercises, notes, started_at)
            VALUES
                (:user_id, :workout_name, :workout_type, :duration_min, :calories_burned,
                 :distance_km, :sets_count, :reps_count, :weight_kg,
                 :heart_rate_avg, :heart_rate_max, :intensity,
                 :form_score, :form_feedback, :exercises, :notes, :started_at)
        """), {
            'user_id':       user_id,
            'workout_name':  data['workout_name'],
            'workout_type':  data['workout_type'],
            'duration_min':  data['duration_min'],
            'calories_burned': data.get('calories_burned'),
            'distance_km':   data.get('distance_km'),
            'sets_count':    data.get('sets_count'),
            'reps_count':    data.get('reps_count'),
            'weight_kg':     data.get('weight_kg'),
            'heart_rate_avg': data.get('heart_rate_avg'),
            'heart_rate_max': data.get('heart_rate_max'),
            'intensity':     data.get('intensity', 'moderate'),
            'form_score':    data.get('form_score'),
            'form_feedback': data.get('form_feedback'),
            'exercises':     str(data.get('exercises', [])),
            'notes':         data.get('notes'),
            'started_at':    started_at,
        })
        conn.commit()
        workout_id = result.lastrowid

    return jsonify({'message': 'Workout logged', 'workout_id': workout_id}), 201


@fitness_bp.route('/workouts/<int:workout_id>', methods=['DELETE'])
@jwt_required()
def delete_workout(workout_id: int):
    """Delete a workout entry"""
    user_id = int(get_jwt_identity())
    with db.engine.connect() as conn:
        result = conn.execute(
            text("DELETE FROM workouts WHERE id = :id AND user_id = :uid"),
            {'id': workout_id, 'uid': user_id}
        )
        conn.commit()
    if result.rowcount == 0:
        return jsonify({'error': 'Workout not found'}), 404
    return jsonify({'message': 'Workout deleted'}), 200


@fitness_bp.route('/stats', methods=['GET'])
@jwt_required()
def fitness_stats():
    """
    Return aggregate fitness statistics for the current user.
    Query params: days (default 30)
    """
    user_id = int(get_jwt_identity())
    days    = int(request.args.get('days', 30))
    since   = datetime.utcnow() - timedelta(days=days)

    with db.engine.connect() as conn:
        # Totals
        totals = conn.execute(text("""
            SELECT
                COUNT(*)                AS total_workouts,
                SUM(duration_min)       AS total_minutes,
                SUM(calories_burned)    AS total_calories,
                SUM(distance_km)        AS total_distance,
                AVG(form_score)         AS avg_form_score
            FROM workouts
            WHERE user_id = :uid AND started_at >= :since
        """), {'uid': user_id, 'since': since}).fetchone()

        # By type
        by_type = conn.execute(text("""
            SELECT workout_type, COUNT(*) AS count, SUM(duration_min) AS minutes
            FROM workouts
            WHERE user_id = :uid AND started_at >= :since
            GROUP BY workout_type
        """), {'uid': user_id, 'since': since}).fetchall()

        # Weekly breakdown
        weekly = conn.execute(text("""
            SELECT
                WEEK(started_at) AS week_num,
                COUNT(*) AS workouts,
                SUM(duration_min) AS minutes,
                SUM(calories_burned) AS calories
            FROM workouts
            WHERE user_id = :uid AND started_at >= :since
            GROUP BY WEEK(started_at)
            ORDER BY week_num
        """), {'uid': user_id, 'since': since}).fetchall()

    def safe_float(v):
        return float(v) if v is not None else 0.0

    return jsonify({
        'period_days': days,
        'totals': {
            'workouts':      int(totals[0] or 0),
            'minutes':       safe_float(totals[1]),
            'calories':      safe_float(totals[2]),
            'distance_km':   safe_float(totals[3]),
            'avg_form_score': safe_float(totals[4]),
        },
        'by_type': [
            {'type': r[0], 'count': int(r[1]), 'minutes': safe_float(r[2])}
            for r in by_type
        ],
        'weekly': [
            {'week': int(r[0]), 'workouts': int(r[1]),
             'minutes': safe_float(r[2]), 'calories': safe_float(r[3])}
            for r in weekly
        ],
    }), 200


@fitness_bp.route('/sleep', methods=['GET'])
@jwt_required()
def get_sleep():
    """Get sleep records for the current user"""
    user_id = int(get_jwt_identity())
    days    = int(request.args.get('days', 14))
    since   = datetime.utcnow() - timedelta(days=days)

    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT * FROM sleep_records
            WHERE user_id = :uid AND sleep_date >= :since
            ORDER BY sleep_date DESC
        """), {'uid': user_id, 'since': since.date()})
        keys = result.keys()
        rows = result.fetchall()

    records = []
    for row in rows:
        r = dict(zip(keys, row))
        for k in ['total_hours', 'deep_sleep_pct', 'rem_sleep_pct',
                  'light_sleep_pct', 'sleep_score']:
            if r.get(k) is not None:
                r[k] = float(r[k])
        if r.get('sleep_date'):
            r['sleep_date'] = r['sleep_date'].isoformat()
        if r.get('created_at'):
            r['created_at'] = r['created_at'].isoformat()
        records.append(r)

    return jsonify({'sleep_records': records, 'count': len(records)}), 200


@fitness_bp.route('/sleep', methods=['POST'])
@jwt_required()
def log_sleep():
    """Log a sleep record"""
    user_id = int(get_jwt_identity())
    data    = request.get_json()

    if not data or not data.get('sleep_date'):
        return jsonify({'error': 'sleep_date is required'}), 400

    with db.engine.connect() as conn:
        result = conn.execute(text("""
            INSERT INTO sleep_records
                (user_id, sleep_date, bedtime, wake_time, total_hours,
                 deep_sleep_pct, rem_sleep_pct, light_sleep_pct,
                 awakenings, sleep_score, quality_rating, notes)
            VALUES
                (:user_id, :sleep_date, :bedtime, :wake_time, :total_hours,
                 :deep_sleep_pct, :rem_sleep_pct, :light_sleep_pct,
                 :awakenings, :sleep_score, :quality_rating, :notes)
        """), {
            'user_id':        user_id,
            'sleep_date':     data['sleep_date'],
            'bedtime':        data.get('bedtime'),
            'wake_time':      data.get('wake_time'),
            'total_hours':    data.get('total_hours'),
            'deep_sleep_pct': data.get('deep_sleep_pct'),
            'rem_sleep_pct':  data.get('rem_sleep_pct'),
            'light_sleep_pct': data.get('light_sleep_pct'),
            'awakenings':     data.get('awakenings', 0),
            'sleep_score':    data.get('sleep_score'),
            'quality_rating': data.get('quality_rating'),
            'notes':          data.get('notes'),
        })
        conn.commit()

    return jsonify({'message': 'Sleep record logged', 'id': result.lastrowid}), 201
