"""
HealthFit AI - Health Metrics Routes
CRUD for health metrics, organ scores, and health summaries
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db
from app.models.health_metric import HealthMetric, OrganHealthScore, METRIC_TYPES

health_bp = Blueprint('health', __name__)


@health_bp.route('/metrics', methods=['GET'])
@jwt_required()
def get_metrics():
    """
    Get health metrics for the current user.
    Query params: metric_type, days (default 30), limit
    """
    user_id = int(get_jwt_identity())
    
    metric_type = request.args.get('metric_type')
    days        = int(request.args.get('days', 30))
    limit       = int(request.args.get('limit', 200))
    
    query = HealthMetric.query.filter_by(user_id=user_id)
    
    # Filter by type if specified
    if metric_type:
        query = query.filter_by(metric_type=metric_type)
    
    # Filter by date range
    since = datetime.utcnow() - timedelta(days=days)
    query = query.filter(HealthMetric.recorded_at >= since)
    
    metrics = query.order_by(desc(HealthMetric.recorded_at)).limit(limit).all()
    
    return jsonify({
        'metrics': [m.to_dict() for m in metrics],
        'count':   len(metrics),
    }), 200


@health_bp.route('/metrics', methods=['POST'])
@jwt_required()
def add_metric():
    """
    Add a new health metric reading.
    Body: { metric_type, value, unit?, source?, notes?, recorded_at? }
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    if not data.get('metric_type') or data.get('value') is None:
        return jsonify({'error': 'metric_type and value are required'}), 400
    
    if data['metric_type'] not in METRIC_TYPES:
        return jsonify({'error': f'Invalid metric_type. Valid: {list(METRIC_TYPES.keys())}'}), 400
    
    # Parse recorded_at if provided
    recorded_at = datetime.utcnow()
    if data.get('recorded_at'):
        try:
            recorded_at = datetime.fromisoformat(data['recorded_at'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'recorded_at must be ISO format'}), 400
    
    metric = HealthMetric(
        user_id     = user_id,
        metric_type = data['metric_type'],
        value       = float(data['value']),
        unit        = data.get('unit', METRIC_TYPES[data['metric_type']]['unit']),
        source      = data.get('source', 'manual'),
        notes       = data.get('notes'),
        recorded_at = recorded_at,
    )
    
    db.session.add(metric)
    db.session.commit()
    
    return jsonify({
        'message': 'Metric recorded successfully',
        'metric':  metric.to_dict(),
    }), 201


@health_bp.route('/metrics/batch', methods=['POST'])
@jwt_required()
def add_metrics_batch():
    """
    Add multiple metrics at once (e.g. from wearable sync).
    Body: { metrics: [{ metric_type, value, ... }, ...] }
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json()
    
    if not data or 'metrics' not in data:
        return jsonify({'error': 'metrics array is required'}), 400
    
    added   = []
    errors  = []
    
    for i, m in enumerate(data['metrics']):
        if m.get('metric_type') not in METRIC_TYPES or m.get('value') is None:
            errors.append({'index': i, 'error': 'Invalid metric_type or missing value'})
            continue
        
        metric = HealthMetric(
            user_id     = user_id,
            metric_type = m['metric_type'],
            value       = float(m['value']),
            unit        = m.get('unit', METRIC_TYPES[m['metric_type']]['unit']),
            source      = m.get('source', 'wearable'),
            notes       = m.get('notes'),
        )
        db.session.add(metric)
        added.append(metric)
    
    db.session.commit()
    
    return jsonify({
        'added':  len(added),
        'errors': errors,
        'metrics': [m.to_dict() for m in added],
    }), 201


@health_bp.route('/metrics/latest', methods=['GET'])
@jwt_required()
def get_latest_metrics():
    """
    Get the most recent reading for each metric type.
    Returns a dict keyed by metric_type.
    """
    user_id = int(get_jwt_identity())
    
    # Subquery: max recorded_at per metric_type
    subq = (
        db.session.query(
            HealthMetric.metric_type,
            func.max(HealthMetric.recorded_at).label('max_at')
        )
        .filter_by(user_id=user_id)
        .group_by(HealthMetric.metric_type)
        .subquery()
    )
    
    # Join to get full rows
    latest = (
        db.session.query(HealthMetric)
        .join(subq, (HealthMetric.metric_type == subq.c.metric_type) &
                    (HealthMetric.recorded_at == subq.c.max_at))
        .filter(HealthMetric.user_id == user_id)
        .all()
    )
    
    return jsonify({
        'latest': {m.metric_type: m.to_dict() for m in latest}
    }), 200


@health_bp.route('/metrics/<int:metric_id>', methods=['DELETE'])
@jwt_required()
def delete_metric(metric_id):
    """Delete a specific metric reading"""
    user_id = int(get_jwt_identity())
    metric  = HealthMetric.query.filter_by(id=metric_id, user_id=user_id).first_or_404()
    db.session.delete(metric)
    db.session.commit()
    return jsonify({'message': 'Metric deleted'}), 200


@health_bp.route('/organ-scores', methods=['GET'])
@jwt_required()
def get_organ_scores():
    """Get AI-computed organ health scores for the current user"""
    user_id = int(get_jwt_identity())
    scores  = OrganHealthScore.query.filter_by(user_id=user_id).all()
    return jsonify({'scores': [s.to_dict() for s in scores]}), 200


@health_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_health_summary():
    """
    Return a comprehensive health summary for the dashboard.
    Includes latest metrics, trends, and scores.
    """
    user_id = int(get_jwt_identity())
    days    = int(request.args.get('days', 7))
    
    # Get latest metrics
    subq = (
        db.session.query(
            HealthMetric.metric_type,
            func.max(HealthMetric.recorded_at).label('max_at')
        )
        .filter_by(user_id=user_id)
        .group_by(HealthMetric.metric_type)
        .subquery()
    )
    latest_metrics = (
        db.session.query(HealthMetric)
        .join(subq, (HealthMetric.metric_type == subq.c.metric_type) &
                    (HealthMetric.recorded_at == subq.c.max_at))
        .filter(HealthMetric.user_id == user_id)
        .all()
    )
    
    # Average metrics over the last `days`
    since  = datetime.utcnow() - timedelta(days=days)
    avgs   = (
        db.session.query(
            HealthMetric.metric_type,
            func.avg(HealthMetric.value).label('avg_val'),
            func.count(HealthMetric.id).label('readings')
        )
        .filter(HealthMetric.user_id == user_id, HealthMetric.recorded_at >= since)
        .group_by(HealthMetric.metric_type)
        .all()
    )
    
    # Organ scores
    organ_scores = OrganHealthScore.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'latest_metrics': {m.metric_type: m.to_dict() for m in latest_metrics},
        'averages':       {a.metric_type: {'avg': round(float(a.avg_val), 2), 'readings': a.readings} for a in avgs},
        'organ_scores':   {s.organ: s.to_dict() for s in organ_scores},
        'days_analyzed':  days,
    }), 200


@health_bp.route('/trends/<metric_type>', methods=['GET'])
@jwt_required()
def get_trend(metric_type: str):
    """
    Get trend data for a specific metric over time.
    Returns data formatted for charting.
    """
    user_id = int(get_jwt_identity())
    
    if metric_type not in METRIC_TYPES:
        return jsonify({'error': f'Invalid metric_type'}), 400
    
    days  = int(request.args.get('days', 30))
    since = datetime.utcnow() - timedelta(days=days)
    
    readings = (
        HealthMetric.query
        .filter_by(user_id=user_id, metric_type=metric_type)
        .filter(HealthMetric.recorded_at >= since)
        .order_by(HealthMetric.recorded_at)
        .all()
    )
    
    meta = METRIC_TYPES[metric_type]
    
    return jsonify({
        'metric_type':  metric_type,
        'unit':         meta['unit'],
        'normal_range': {'min': meta['normal_min'], 'max': meta['normal_max']},
        'data':         [{'date': r.recorded_at.isoformat(), 'value': float(r.value), 'status': r.status} for r in readings],
        'count':        len(readings),
    }), 200
