"""
HealthFit AI - Food Scanner (OpenCV + AI)
Analyzes food images to estimate nutritional content.
Uses OpenCV for preprocessing and a simple classification approach.
"""
import os
import numpy as np
from dataclasses import dataclass, field

try:
    import cv2
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


@dataclass
class FoodScanResult:
    food_name: str = 'Unknown food'
    confidence: float = 0.0
    calories_per_serving: int = 0
    protein_g: float = 0.0
    carbohydrates_g: float = 0.0
    fat_g: float = 0.0
    fiber_g: float = 0.0
    serving_size: str = '1 serving'
    color_profile: list = field(default_factory=list)
    health_score: float = 0.0
    health_tags: list = field(default_factory=list)


# Static food nutrient database (simplified)
# In production, integrate with USDA FoodData Central API
FOOD_DATABASE = {
    'salad':       FoodScanResult('Green Salad',           85,  50, 3.0,  8.0,  1.5, 2.5, '1 bowl (200g)'),
    'apple':       FoodScanResult('Apple',                 90,  95, 0.5, 25.0,  0.3, 4.4, '1 medium (182g)'),
    'banana':      FoodScanResult('Banana',                88, 105, 1.3, 27.0,  0.4, 3.1, '1 medium (118g)'),
    'chicken':     FoodScanResult('Grilled Chicken',       82, 165,31.0,  0.0,  3.6, 0.0, '100g'),
    'rice':        FoodScanResult('White Rice',            80, 206, 4.3, 44.5,  0.4, 0.6, '1 cup cooked (186g)'),
    'broccoli':    FoodScanResult('Broccoli',              92,  55, 3.7, 11.0,  0.6, 5.1, '1 cup (91g)'),
    'pizza':       FoodScanResult('Pizza Slice',           70, 285, 12.0, 36.0, 10.0, 2.0, '1 slice (107g)'),
    'burger':      FoodScanResult('Beef Burger',           60, 540, 34.0, 40.0, 27.0, 2.0, '1 burger (220g)'),
    'oatmeal':     FoodScanResult('Oatmeal',               88, 158, 6.0, 27.0,  3.2, 4.0, '1 cup cooked (234g)'),
    'eggs':        FoodScanResult('Scrambled Eggs',        85, 148,10.0,  1.6, 11.0, 0.0, '2 large eggs'),
    'salmon':      FoodScanResult('Salmon Fillet',         90, 208,20.0,  0.0, 13.0, 0.0, '100g'),
    'yogurt':      FoodScanResult('Greek Yogurt',          87, 100,17.0,  6.0,  0.7, 0.0, '170g'),
    'bread':       FoodScanResult('Whole Wheat Bread',     75, 128, 5.0, 25.0,  2.0, 3.0, '2 slices (56g)'),
    'avocado':     FoodScanResult('Avocado',               91, 160, 2.0,  9.0, 15.0, 7.0, 'half (100g)'),
}

# Color-based food recognition (dominant color → likely food category)
COLOR_FOOD_MAP = {
    'green':  ['salad', 'broccoli', 'avocado'],
    'yellow': ['banana', 'eggs', 'oatmeal'],
    'red':    ['apple', 'pizza'],
    'brown':  ['chicken', 'burger', 'bread'],
    'orange': ['salmon'],
    'white':  ['rice', 'yogurt', 'eggs'],
}


class FoodScanner:
    """
    Analyzes food images using color analysis and dominant color classification.
    For production use, integrate with a trained food classification CNN.
    """

    def __init__(self):
        self.last_scan = None

    def scan_image(self, image_input) -> FoodScanResult:
        """
        Scan a food image and estimate nutritional content.
        image_input: numpy array (BGR), file path string, or bytes
        """
        # Load image
        img = self._load_image(image_input)
        if img is None:
            return self._unknown_food()

        # Preprocess
        img_processed = self._preprocess(img)

        # Get dominant colors
        colors = self._extract_dominant_colors(img_processed)

        # Match to food via color profile
        result = self._identify_food(img_processed, colors)
        result.color_profile = colors
        result.health_score  = self._calculate_health_score(result)
        result.health_tags   = self._get_health_tags(result)

        self.last_scan = result
        return result

    def scan_from_base64(self, b64_string: str) -> FoodScanResult:
        """Scan from base64 encoded image string"""
        import base64
        try:
            img_bytes = base64.b64decode(b64_string.split(',')[-1])  # strip data URI prefix
            img_array = np.frombuffer(img_bytes, dtype=np.uint8)
            if CV_AVAILABLE:
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                return self.scan_image(img)
        except Exception as e:
            print(f"Base64 decode error: {e}")
        return self._unknown_food()

    def _load_image(self, source) -> np.ndarray | None:
        if isinstance(source, np.ndarray):
            return source
        if isinstance(source, str) and os.path.exists(source):
            if CV_AVAILABLE:
                return cv2.imread(source)
        if isinstance(source, bytes):
            if CV_AVAILABLE:
                arr = np.frombuffer(source, dtype=np.uint8)
                return cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return None

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        """Resize, denoise, and normalize the image"""
        if not CV_AVAILABLE:
            return img
        img = cv2.resize(img, (224, 224))
        img = cv2.GaussianBlur(img, (3, 3), 0)
        return img

    def _extract_dominant_colors(self, img: np.ndarray) -> list[str]:
        """Extract top 3 dominant color names from image"""
        if not CV_AVAILABLE:
            return ['unknown']

        # Convert to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pixels  = img_rgb.reshape(-1, 3).astype(np.float32)

        # Simple k-means with k=3
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(pixels, 3, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

        # Sort by cluster size
        unique, counts = np.unique(labels, return_counts=True)
        sorted_idx     = np.argsort(-counts)
        dominant       = centers[sorted_idx]

        color_names = [self._rgb_to_color_name(c) for c in dominant]
        return color_names

    def _rgb_to_color_name(self, rgb: np.ndarray) -> str:
        """Map an RGB value to a color category name"""
        r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
        if g > r and g > b and g > 80:
            return 'green'
        if r > g and r > b:
            if r > 150:
                return 'red' if b < 80 else 'pink'
            return 'brown'
        if r > 150 and g > 150 and b < 80:
            return 'yellow'
        if r > 180 and g > 120 and b < 80:
            return 'orange'
        if r > 150 and g > 150 and b > 150:
            return 'white'
        return 'brown'

    def _identify_food(self, img: np.ndarray, colors: list[str]) -> FoodScanResult:
        """
        Match detected colors to likely food items.
        In production, replace with CNN classifier.
        """
        candidates = {}
        for color in colors:
            for food_key in COLOR_FOOD_MAP.get(color, []):
                candidates[food_key] = candidates.get(food_key, 0) + 1

        if not candidates:
            return self._unknown_food()

        best_key = max(candidates, key=candidates.get)
        result   = FOOD_DATABASE.get(best_key, self._unknown_food())

        # Confidence based on color match strength
        result.confidence = min(candidates[best_key] / 3 * 0.7 + 0.3, 0.95)
        return result

    def _unknown_food(self) -> FoodScanResult:
        return FoodScanResult(
            food_name='Unknown food item',
            confidence=0.0,
            calories_per_serving=200,
            protein_g=8.0,
            carbohydrates_g=25.0,
            fat_g=8.0,
            serving_size='estimate',
            health_score=60.0,
            health_tags=['unidentified'],
        )

    def _calculate_health_score(self, r: FoodScanResult) -> float:
        """
        Simple nutrient-density health score (0-100).
        High protein, high fiber = good. High fat = moderate penalty.
        """
        score = 50.0
        if r.calories_per_serving > 0:
            protein_density = r.protein_g / r.calories_per_serving * 400
            score += min(protein_density * 10, 20)
        score += min(r.fiber_g * 4, 20)
        if r.calories_per_serving > 400: score -= 10
        if r.fat_g > 20: score -= 10
        if r.carbohydrates_g > 40 and r.fiber_g < 3: score -= 5
        return round(max(0, min(score, 100)), 1)

    def _get_health_tags(self, r: FoodScanResult) -> list[str]:
        tags = []
        if r.protein_g >= 15: tags.append('high_protein')
        if r.fiber_g >= 4:    tags.append('high_fiber')
        if r.fat_g <= 5:      tags.append('low_fat')
        if r.calories_per_serving <= 100: tags.append('low_calorie')
        if r.calories_per_serving >= 400: tags.append('calorie_dense')
        if r.carbohydrates_g >= 30 and r.fiber_g >= 5: tags.append('complex_carbs')
        return tags


def scan_food_from_path(image_path: str) -> dict:
    """Convenience function for scanning a food image file"""
    scanner = FoodScanner()
    result  = scanner.scan_image(image_path)
    return {
        'food_name':           result.food_name,
        'confidence':          round(result.confidence * 100, 1),
        'calories_per_serving': result.calories_per_serving,
        'macros': {
            'protein_g':       result.protein_g,
            'carbohydrates_g': result.carbohydrates_g,
            'fat_g':           result.fat_g,
            'fiber_g':         result.fiber_g,
        },
        'serving_size':  result.serving_size,
        'health_score':  result.health_score,
        'health_tags':   result.health_tags,
        'color_profile': result.color_profile,
    }
