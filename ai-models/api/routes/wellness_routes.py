"""
HealthFit AI - Wellness Routes (FastAPI)
Additional wellness-specific endpoints for the AI service.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class WellnessScoreRequest(BaseModel):
    sleep_score:     Optional[float] = 75
    activity_score:  Optional[float] = 60
    nutrition_score: Optional[float] = 70
    stress_score:    Optional[float] = 40   # lower = less stress
    hydration_score: Optional[float] = 65
    age:             Optional[int]   = 35


class BMIRequest(BaseModel):
    weight_kg: float
    height_cm: float
    age:       Optional[int]   = 30
    gender:    Optional[str]   = 'other'
    activity:  Optional[str]   = 'moderately_active'


@router.get('/wellness')
async def wellness_overview():
    return {'message': 'Wellness API v1.0', 'endpoints': [
        '/api/wellness-score', '/api/bmi-analysis',
        '/api/calorie-needs', '/api/hydration-needs',
    ]}


@router.post('/wellness-score')
async def compute_wellness_score(req: WellnessScoreRequest):
    """
    Compute a composite wellness score (0-100) from individual pillar scores.
    Weights: sleep 25%, activity 25%, nutrition 20%, stress 20%, hydration 10%
    """
    # Invert stress (lower raw score = less stress = better wellness)
    stress_wellness = 100 - req.stress_score

    composite = (
        req.sleep_score     * 0.25 +
        req.activity_score  * 0.25 +
        req.nutrition_score * 0.20 +
        stress_wellness     * 0.20 +
        req.hydration_score * 0.10
    )

    # Age-based adjustment (slight penalty for higher age risk)
    age_factor = max(0.85, 1 - (max(0, req.age - 40) * 0.002))
    composite  *= age_factor

    composite = round(min(max(composite, 0), 100), 1)

    if composite >= 85:   grade, emoji = 'Excellent', '🏆'
    elif composite >= 70: grade, emoji = 'Good', '💪'
    elif composite >= 55: grade, emoji = 'Fair', '📈'
    elif composite >= 40: grade, emoji = 'Needs Work', '⚠️'
    else:                 grade, emoji = 'Critical', '🚨'

    # Identify weakest pillar
    pillars = {
        'Sleep':      req.sleep_score,
        'Activity':   req.activity_score,
        'Nutrition':  req.nutrition_score,
        'Stress Mgmt': stress_wellness,
        'Hydration':  req.hydration_score,
    }
    weakest = min(pillars, key=pillars.get)

    return {
        'wellness_score': composite,
        'grade':          grade,
        'emoji':          emoji,
        'pillar_scores': {
            'sleep':       req.sleep_score,
            'activity':    req.activity_score,
            'nutrition':   req.nutrition_score,
            'stress_mgmt': stress_wellness,
            'hydration':   req.hydration_score,
        },
        'weakest_pillar': weakest,
        'top_recommendation': f'Focus on improving your {weakest.lower()} to boost overall wellness.',
    }


@router.post('/bmi-analysis')
async def bmi_analysis(req: BMIRequest):
    """
    Compute BMI and provide detailed body composition analysis.
    """
    height_m = req.height_cm / 100
    bmi      = round(req.weight_kg / (height_m ** 2), 2)

    # BMI category
    if bmi < 18.5:
        category, risk = 'Underweight', 'moderate'
    elif bmi < 25.0:
        category, risk = 'Normal weight', 'low'
    elif bmi < 30.0:
        category, risk = 'Overweight', 'moderate'
    elif bmi < 35.0:
        category, risk = 'Obese Class I', 'high'
    elif bmi < 40.0:
        category, risk = 'Obese Class II', 'high'
    else:
        category, risk = 'Obese Class III', 'critical'

    # Ideal weight range (BMI 18.5-24.9)
    ideal_min = round(18.5 * height_m ** 2, 1)
    ideal_max = round(24.9 * height_m ** 2, 1)
    weight_to_lose = round(max(0, req.weight_kg - ideal_max), 1)

    return {
        'bmi':               bmi,
        'category':          category,
        'health_risk':       risk,
        'ideal_weight_range': {'min_kg': ideal_min, 'max_kg': ideal_max},
        'weight_to_lose_kg': weight_to_lose,
        'recommendations':   _bmi_recommendations(bmi, req.gender),
    }


@router.post('/calorie-needs')
async def calorie_needs(req: BMIRequest):
    """
    Calculate daily calorie needs using Mifflin-St Jeor equation.
    """
    weight = req.weight_kg
    height = req.height_cm
    age    = req.age or 30

    # BMR
    if req.gender == 'female':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5

    activity_multipliers = {
        'sedentary':       1.2,
        'lightly_active':  1.375,
        'moderately_active': 1.55,
        'very_active':     1.725,
        'extra_active':    1.9,
    }
    mult  = activity_multipliers.get(req.activity or 'moderately_active', 1.55)
    tdee  = round(bmr * mult)

    return {
        'bmr':             round(bmr),
        'tdee':            tdee,
        'for_weight_loss': tdee - 500,   # ~0.5kg/week deficit
        'for_weight_gain': tdee + 300,   # lean bulk
        'for_maintenance': tdee,
        'protein_target_g': round(weight * 1.6),  # 1.6g/kg body weight
        'fat_target_g':     round(tdee * 0.25 / 9),
        'carb_target_g':    round((tdee - (weight * 1.6 * 4) - (tdee * 0.25)) / 4),
    }


@router.get('/hydration-needs')
async def hydration_needs(
    weight_kg: float = 70,
    activity_level: str = 'moderately_active',
    climate: str = 'temperate',
):
    """Calculate daily water intake recommendation"""
    base_ml = weight_kg * 35   # 35ml per kg body weight

    if activity_level in ('very_active', 'extra_active'):
        base_ml += 600
    elif activity_level == 'moderately_active':
        base_ml += 300

    if climate == 'hot': base_ml += 400
    elif climate == 'cold': base_ml -= 100

    base_ml = round(base_ml)

    return {
        'daily_ml':     base_ml,
        'daily_liters': round(base_ml / 1000, 2),
        'glasses_8oz':  round(base_ml / 240),
        'schedule': {
            'morning':   '500ml (2 glasses) within 30 min of waking',
            'pre_meal':  '250ml (1 glass) 30 min before each meal',
            'post_workout': '500ml per hour of exercise',
            'evening':   '250ml (1 glass) 1 hour before bed',
        },
    }


def _bmi_recommendations(bmi: float, gender: str) -> list:
    if bmi < 18.5:
        return [
            'Consult a doctor to rule out underlying conditions',
            'Increase caloric intake with nutrient-dense foods',
            'Include strength training to build lean muscle',
        ]
    elif bmi < 25:
        return [
            'Maintain current healthy weight',
            'Continue balanced diet and regular exercise',
            'Annual health screening recommended',
        ]
    elif bmi < 30:
        return [
            '500-calorie daily deficit for 0.5kg/week weight loss',
            'Increase daily steps to 10,000+',
            'Reduce processed foods and added sugars',
            'Strength training preserves muscle during weight loss',
        ]
    else:
        return [
            'Consult a doctor for personalized weight management plan',
            'Target 5-10% weight reduction for significant health benefits',
            'Start with low-impact exercise (walking, swimming)',
            'Consider referral to registered dietitian',
        ]
