"""
HealthFit AI - AI Models FastAPI Service
Standalone microservice exposing all AI models via REST API.
Run with: python api/main.py
Default port: 8001
"""
import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

# Add parent dir to path so we can import ai-models modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

app = FastAPI(
    title='HealthFit AI - Models Service',
    description='AI/ML inference service for health risk prediction, sleep analysis, and exercise form detection.',
    version='1.0.0',
)

# CORS for Flask backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5000', 'http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# ─── Import AI modules (lazy, with graceful fallback) ───────────────────────

def _try_import(module_path):
    try:
        import importlib.util
        spec   = importlib.util.spec_from_file_location('module', module_path)
        mod    = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        print(f"⚠️  Could not load {module_path}: {e}")
        return None

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
risk_mod    = _try_import(os.path.join(BASE, 'sklearn_models', 'health_risk_classifier', 'health_risk_predictor.py'))
sleep_mod   = _try_import(os.path.join(BASE, 'tensorflow_models', 'sleep_analyzer', 'sleep_analyzer.py'))
stress_mod  = _try_import(os.path.join(BASE, 'tensorflow_models', 'stress_detector', 'stress_detector.py'))
exercise_mod = _try_import(os.path.join(BASE, 'mediapipe_integration', 'exercise_analyzer', 'exercise_form_analyzer.py'))
food_mod    = _try_import(os.path.join(BASE, 'opencv_processing', 'food_scanner', 'food_scanner.py'))

# Register route blueprints
from api.routes.wellness_routes import router as wellness_router
app.include_router(wellness_router, prefix='/api')


# ─── Request / Response models ─────────────────────────────────────────────

class HealthRiskRequest(BaseModel):
    age:               Optional[float] = 30
    bmi:               Optional[float] = 22
    systolic:          Optional[float] = 120
    diastolic:         Optional[float] = 80
    heart_rate:        Optional[float] = 70
    glucose:           Optional[float] = 90
    cholesterol_total: Optional[float] = 190
    sleep_hours:       Optional[float] = 7
    stress_level:      Optional[float] = 3
    activity:          Optional[str]   = 'moderately_active'
    gender:            Optional[str]   = 'other'
    smoking:           Optional[float] = 0
    alcohol:           Optional[float] = 0


class SleepAnalysisRequest(BaseModel):
    sleep_data: Optional[List[dict]] = None


class StressDetectionRequest(BaseModel):
    hrv_ms:             Optional[float] = 45
    resting_hr:         Optional[float] = 70
    sleep_score:        Optional[float] = 75
    sleep_hours:        Optional[float] = 7
    activity_minutes:   Optional[float] = 30
    subjective_stress:  Optional[float] = 5
    recovery_score:     Optional[float] = 70


class ExerciseAnalysisRequest(BaseModel):
    exercise_type: Optional[str] = 'squat'
    keypoints:     Optional[List[dict]] = None
    workout_data:  Optional[dict] = None


class FoodScanRequest(BaseModel):
    image_base64: Optional[str] = None
    image_url:    Optional[str] = None


# ─── Endpoints ─────────────────────────────────────────────────────────────

@app.get('/')
async def root():
    return {
        'service': 'HealthFit AI Models API',
        'version': '1.0.0',
        'status':  'running',
        'endpoints': [
            '/api/predict-risk',
            '/api/analyze-sleep',
            '/api/detect-stress',
            '/api/analyze-exercise',
            '/api/scan-food',
            '/api/health',
        ],
    }


@app.get('/api/health')
async def health():
    return {
        'status':   'healthy',
        'modules': {
            'health_risk':   risk_mod is not None,
            'sleep_analyzer': sleep_mod is not None,
            'stress_detector': stress_mod is not None,
            'exercise_analyzer': exercise_mod is not None,
            'food_scanner':  food_mod is not None,
        },
    }


@app.post('/api/predict-risk')
async def predict_risk(req: HealthRiskRequest):
    """Run health risk prediction"""
    features = req.dict()
    if risk_mod:
        predictor = risk_mod.HealthRiskPredictor()
        if not predictor.load():
            # Model not trained yet — use rule-based
            return risk_mod._rule_based_predict(features)
        return predictor.predict_single(features)
    else:
        raise HTTPException(status_code=503, detail='Health risk model not available')


@app.post('/api/analyze-sleep')
async def analyze_sleep(req: SleepAnalysisRequest):
    """Analyze sleep patterns"""
    if sleep_mod:
        result = sleep_mod.analyze_sleep(req.sleep_data or [])
        return result
    raise HTTPException(status_code=503, detail='Sleep analyzer not available')


@app.post('/api/detect-stress')
async def detect_stress(req: StressDetectionRequest):
    """Detect stress level"""
    if stress_mod:
        result = stress_mod.detect_stress(req.dict())
        return result
    raise HTTPException(status_code=503, detail='Stress detector not available')


@app.post('/api/analyze-exercise')
async def analyze_exercise(req: ExerciseAnalysisRequest):
    """Analyze exercise form from keypoints"""
    if exercise_mod and req.keypoints:
        result = exercise_mod.analyze_exercise_from_keypoints(
            req.keypoints, req.exercise_type or 'squat'
        )
        return result
    # Return static guidance if no keypoints
    return {
        'form_score':  80.0,
        'exercise_type': req.exercise_type,
        'corrections': [
            f'Real-time analysis requires keypoint data from MediaPipe.',
            'Use the fitness page webcam feature for live form analysis.',
        ],
        'source': 'static_guidance',
    }


@app.post('/api/scan-food')
async def scan_food(req: FoodScanRequest):
    """Scan food image for nutritional info"""
    if food_mod and req.image_base64:
        scanner = food_mod.FoodScanner()
        result  = scanner.scan_from_base64(req.image_base64)
        return {
            'food_name':    result.food_name,
            'confidence':   round(result.confidence * 100, 1),
            'calories':     result.calories_per_serving,
            'macros': {
                'protein_g':       result.protein_g,
                'carbohydrates_g': result.carbohydrates_g,
                'fat_g':           result.fat_g,
                'fiber_g':         result.fiber_g,
            },
            'serving_size': result.serving_size,
            'health_score': result.health_score,
            'health_tags':  result.health_tags,
        }
    raise HTTPException(status_code=400, detail='image_base64 is required')


if __name__ == '__main__':
    port = int(os.environ.get('AI_API_PORT', 8001))
    print(f"""
    ╔══════════════════════════════════════╗
    ║   HealthFit AI - Models Service      ║
    ║   Running on http://localhost:{port}    ║
    ╚══════════════════════════════════════╝
    """)
    uvicorn.run('api.main:app', host='0.0.0.0', port=port, reload=True)
