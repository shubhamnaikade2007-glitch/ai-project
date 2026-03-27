"""
HealthFit AI - Nutrition Routes
Meal logging, nutrition tracking, and AI-powered recommendations
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, date
from sqlalchemy import func, desc
from app import db

nutrition_bp = Blueprint('nutrition', __name__)

# We'll use the DB directly via SQLAlchemy text for the meal table
from sqlalchemy import text


def _meal_to_dict(row) -> dict:
    """Convert a meal DB row to dict"""
    return {
        'id':             row.id,
        'user_id':        row.user_id,
        'meal_name':      row.meal_name,
        'meal_type':      row.meal_type,
        'calories':       row.calories,
        'protein_g':      float(row.protein_g) if row.protein_g else None,
        'carbohydrates_g': float(row.carbohydrates_g) if row.carbohydrates_g else None,
        'fat_g':          float(row.fat_g) if row.fat_g else None,
        'fiber_g':        float(row.fiber_g) if row.fiber_g else None,
        'sugar_g':        float(row.sugar_g) if row.sugar_g else None,
        'serving_size':   row.serving_size,
        'ingredients':    row.ingredients,
        'logged_at':      row.logged_at.isoformat() if row.logged_at else None,
        'notes':          row.notes,
    }


@nutrition_bp.route('/meals', methods=['GET'])
@jwt_required()
def get_meals():
    """
    Get meal log for the current user.
    Query params: days (default 7), meal_type, date (YYYY-MM-DD)
    """
    user_id = int(get_jwt_identity())
    days    = int(request.args.get('days', 7))
    meal_type = request.args.get('meal_type')
    target_date = request.args.get('date')
    
    with db.engine.connect() as conn:
        params = {'user_id': user_id}
        
        if target_date:
            where = "WHERE user_id = :user_id AND DATE(logged_at) = :target_date"
            params['target_date'] = target_date
        else:
            since = datetime.utcnow() - timedelta(days=days)
            where = "WHERE user_id = :user_id AND logged_at >= :since"
            params['since'] = since
        
        if meal_type:
            where += " AND meal_type = :meal_type"
            params['meal_type'] = meal_type
        
        result = conn.execute(
            text(f"SELECT * FROM meals {where} ORDER BY logged_at DESC LIMIT 100"),
            params
        )
        meals = result.fetchall()
    
    meals_list = [dict(zip(result.keys(), row)) for row in meals]
    
    # Clean up decimal types for JSON serialization
    for m in meals_list:
        for key in ['protein_g', 'carbohydrates_g', 'fat_g', 'fiber_g', 'sugar_g', 'sodium_mg']:
            if m.get(key) is not None:
                m[key] = float(m[key])
        if m.get('logged_at'):
            m['logged_at'] = m['logged_at'].isoformat()
    
    return jsonify({'meals': meals_list, 'count': len(meals_list)}), 200


@nutrition_bp.route('/meals', methods=['POST'])
@jwt_required()
def log_meal():
    """
    Log a new meal.
    Body: { meal_name, meal_type, calories?, protein_g?, carbohydrates_g?, fat_g?, ... }
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('meal_name') or not data.get('meal_type'):
        return jsonify({'error': 'meal_name and meal_type are required'}), 400
    
    valid_types = ['breakfast', 'lunch', 'dinner', 'snack', 'pre_workout', 'post_workout']
    if data['meal_type'] not in valid_types:
        return jsonify({'error': f'meal_type must be one of: {valid_types}'}), 400
    
    logged_at = datetime.utcnow()
    if data.get('logged_at'):
        try:
            logged_at = datetime.fromisoformat(data['logged_at'])
        except ValueError:
            pass
    
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            INSERT INTO meals (user_id, meal_name, meal_type, calories,
                protein_g, carbohydrates_g, fat_g, fiber_g, sugar_g, sodium_mg,
                serving_size, ingredients, notes, logged_at)
            VALUES (:user_id, :meal_name, :meal_type, :calories,
                :protein_g, :carbohydrates_g, :fat_g, :fiber_g, :sugar_g, :sodium_mg,
                :serving_size, :ingredients, :notes, :logged_at)
        """), {
            'user_id':         user_id,
            'meal_name':       data['meal_name'],
            'meal_type':       data['meal_type'],
            'calories':        data.get('calories'),
            'protein_g':       data.get('protein_g'),
            'carbohydrates_g': data.get('carbohydrates_g'),
            'fat_g':           data.get('fat_g'),
            'fiber_g':         data.get('fiber_g'),
            'sugar_g':         data.get('sugar_g'),
            'sodium_mg':       data.get('sodium_mg'),
            'serving_size':    data.get('serving_size'),
            'ingredients':     data.get('ingredients'),
            'notes':           data.get('notes'),
            'logged_at':       logged_at,
        })
        conn.commit()
        meal_id = result.lastrowid
    
    return jsonify({
        'message': 'Meal logged successfully',
        'meal_id': meal_id,
    }), 201


@nutrition_bp.route('/meals/<int:meal_id>', methods=['DELETE'])
@jwt_required()
def delete_meal(meal_id: int):
    """Delete a meal log entry"""
    user_id = int(get_jwt_identity())
    
    with db.engine.connect() as conn:
        result = conn.execute(
            text("DELETE FROM meals WHERE id = :id AND user_id = :user_id"),
            {'id': meal_id, 'user_id': user_id}
        )
        conn.commit()
    
    if result.rowcount == 0:
        return jsonify({'error': 'Meal not found or access denied'}), 404
    
    return jsonify({'message': 'Meal deleted'}), 200


@nutrition_bp.route('/daily-summary', methods=['GET'])
@jwt_required()
def daily_summary():
    """
    Return nutrition totals for a specific day.
    Query param: date (YYYY-MM-DD, defaults to today)
    """
    user_id    = int(get_jwt_identity())
    target_date = request.args.get('date', date.today().isoformat())
    
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                meal_type,
                COUNT(*)                AS meal_count,
                SUM(calories)           AS total_calories,
                SUM(protein_g)          AS total_protein,
                SUM(carbohydrates_g)    AS total_carbs,
                SUM(fat_g)              AS total_fat,
                SUM(fiber_g)            AS total_fiber
            FROM meals
            WHERE user_id = :user_id AND DATE(logged_at) = :target_date
            GROUP BY meal_type
        """), {'user_id': user_id, 'target_date': target_date})
        rows = result.fetchall()
        keys = result.keys()
    
    by_type = {}
    totals  = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}
    
    for row in rows:
        r = dict(zip(keys, row))
        meal_type = r['meal_type']
        by_type[meal_type] = {
            'meal_count':    r['meal_count'],
            'calories':      float(r['total_calories'] or 0),
            'protein_g':     float(r['total_protein'] or 0),
            'carbs_g':       float(r['total_carbs'] or 0),
            'fat_g':         float(r['total_fat'] or 0),
            'fiber_g':       float(r['total_fiber'] or 0),
        }
        totals['calories'] += float(r['total_calories'] or 0)
        totals['protein']  += float(r['total_protein'] or 0)
        totals['carbs']    += float(r['total_carbs'] or 0)
        totals['fat']      += float(r['total_fat'] or 0)
        totals['fiber']    += float(r['total_fiber'] or 0)
    
    # Daily targets (simplified - would come from user profile in production)
    targets = {
        'calories': 2000, 'protein': 150, 'carbs': 250, 'fat': 65, 'fiber': 25
    }
    
    return jsonify({
        'date':     target_date,
        'by_type':  by_type,
        'totals':   totals,
        'targets':  targets,
        'completion': {
            k: round(totals[k] / targets[k] * 100, 1)
            for k in targets if targets[k] > 0
        },
    }), 200


@nutrition_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """
    AI-powered meal recommendations based on user's nutritional data.
    Analyzes recent meals and provides personalized suggestions.
    """
    user_id = int(get_jwt_identity())
    
    # Calculate last 7 days averages
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                AVG(calories)           AS avg_calories,
                AVG(protein_g)          AS avg_protein,
                AVG(carbohydrates_g)    AS avg_carbs,
                AVG(fat_g)              AS avg_fat,
                AVG(fiber_g)            AS avg_fiber
            FROM meals
            WHERE user_id = :user_id
            AND logged_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """), {'user_id': user_id})
        row = result.fetchone()
    
    if not row or not row[0]:
        avg_cals = 0
    else:
        avg_cals = float(row[0] or 0)
    
    # Generate rule-based recommendations (in production, call AI API)
    recommendations = []
    
    if avg_cals < 1500:
        recommendations.append({
            'type': 'calorie_deficit',
            'priority': 'high',
            'title': 'Increase Caloric Intake',
            'message': 'Your average daily calories are below recommended levels. Consider adding nutrient-dense snacks.',
            'suggestions': ['Avocado toast with eggs', 'Greek yogurt with granola', 'Almond butter with banana'],
        })
    elif avg_cals > 2500:
        recommendations.append({
            'type': 'calorie_surplus',
            'priority': 'medium',
            'title': 'Moderate Caloric Intake',
            'message': 'Your calorie intake is slightly elevated. Focus on portion control.',
            'suggestions': ['Increase vegetable portions', 'Choose lean proteins', 'Reduce processed foods'],
        })
    
    # Static recommendations always included
    recommendations.extend([
        {
            'type': 'hydration',
            'priority': 'medium',
            'title': 'Stay Hydrated',
            'message': 'Aim for 8 glasses (2L) of water daily. Proper hydration improves metabolism and energy.',
            'suggestions': ['Lemon water in morning', 'Herbal teas', 'Water-rich fruits like watermelon'],
        },
        {
            'type': 'meal_timing',
            'priority': 'low',
            'title': 'Optimize Meal Timing',
            'message': 'Eating every 3-4 hours maintains stable blood sugar and energy levels.',
            'suggestions': ['Have breakfast within 1 hour of waking', 'Eat dinner 2-3 hours before bed'],
        },
        {
            'type': 'protein',
            'priority': 'medium',
            'title': 'Protein at Every Meal',
            'message': 'Including protein at each meal supports muscle maintenance and keeps you fuller longer.',
            'suggestions': ['Grilled chicken', 'Legumes and beans', 'Cottage cheese', 'Eggs'],
        },
    ])
    
    return jsonify({'recommendations': recommendations}), 200
