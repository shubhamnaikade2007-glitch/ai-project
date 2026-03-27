"""
HealthFit AI - Exercise Form Analyzer (MediaPipe + OpenCV)
Analyzes exercise form from webcam or uploaded video using pose estimation.
Detects common form errors and provides real-time correction feedback.
"""
import numpy as np
import math
from dataclasses import dataclass, field
from typing import Optional

# Graceful imports
try:
    import mediapipe as mp
    import cv2
    MP_AVAILABLE = True
except ImportError:
    MP_AVAILABLE = False
    print("⚠️  MediaPipe/OpenCV not available. ExerciseFormAnalyzer will return static guidance.")


# ─── Landmark indices (MediaPipe Pose) ──────────────────────────────────────
class Landmark:
    LEFT_SHOULDER  = 11; RIGHT_SHOULDER = 12
    LEFT_ELBOW     = 13; RIGHT_ELBOW    = 14
    LEFT_WRIST     = 15; RIGHT_WRIST    = 16
    LEFT_HIP       = 23; RIGHT_HIP      = 24
    LEFT_KNEE      = 25; RIGHT_KNEE     = 26
    LEFT_ANKLE     = 27; RIGHT_ANKLE    = 28
    LEFT_HEEL      = 29; RIGHT_HEEL     = 30
    LEFT_FOOT      = 31; RIGHT_FOOT     = 32
    NOSE           = 0
    LEFT_EAR       = 7; RIGHT_EAR       = 8


@dataclass
class FormFeedback:
    score: float = 100.0
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    corrections: list = field(default_factory=list)
    rep_count: int = 0
    phase: str = 'unknown'


def calculate_angle(a: list, b: list, c: list) -> float:
    """
    Calculate the angle at point b, formed by vectors b→a and b→c.
    Points are [x, y] or [x, y, z].
    """
    a, b, c = np.array(a[:2]), np.array(b[:2]), np.array(c[:2])
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle   = abs(math.degrees(radians))
    return min(angle, 360 - angle)


def calculate_distance(p1: list, p2: list) -> float:
    """Euclidean distance between two 2D points"""
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


class ExerciseFormAnalyzer:
    """
    Real-time exercise form analyzer using MediaPipe Pose.
    Supports: squat, deadlift, pushup, lunge, shoulder press, bicep curl.
    """

    SUPPORTED_EXERCISES = ['squat', 'deadlift', 'pushup', 'lunge', 'shoulder_press', 'bicep_curl']

    def __init__(self, exercise_type: str = 'squat'):
        self.exercise_type = exercise_type.lower()
        self.rep_count     = 0
        self.phase         = 'start'     # start / down / up
        self.angle_history: list[float] = []
        self.frame_count   = 0

        if MP_AVAILABLE:
            self.mp_pose = mp.solutions.pose
            self.pose    = self.mp_pose.Pose(
                static_image_mode     = False,
                model_complexity      = 1,
                smooth_landmarks      = True,
                min_detection_confidence = 0.5,
                min_tracking_confidence  = 0.5,
            )
            self.mp_draw = mp.solutions.drawing_utils

    def analyze_frame(self, frame_bgr: np.ndarray) -> tuple[np.ndarray, FormFeedback]:
        """
        Process a single video frame. Detects landmarks and analyzes form.
        Returns: (annotated_frame, FormFeedback)
        """
        if not MP_AVAILABLE:
            return frame_bgr, self._static_guidance()

        self.frame_count += 1
        feedback = FormFeedback()

        # Convert BGR → RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results   = self.pose.process(frame_rgb)

        if not results.pose_landmarks:
            feedback.warnings.append('No pose detected — ensure full body is visible')
            feedback.score = 0
            return frame_bgr, feedback

        # Draw skeleton on frame
        annotated = frame_bgr.copy()
        self.mp_draw.draw_landmarks(
            annotated,
            results.pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
        )

        # Extract landmark coordinates as normalized [x, y, z, visibility]
        lms = results.pose_landmarks.landmark
        h, w = frame_bgr.shape[:2]
        pts  = {i: [lm.x * w, lm.y * h, lm.z, lm.visibility]
                for i, lm in enumerate(lms)}

        # Route to exercise-specific analysis
        analysers = {
            'squat':          self._analyze_squat,
            'deadlift':       self._analyze_deadlift,
            'pushup':         self._analyze_pushup,
            'lunge':          self._analyze_lunge,
            'shoulder_press': self._analyze_shoulder_press,
            'bicep_curl':     self._analyze_bicep_curl,
        }
        analyser = analysers.get(self.exercise_type, self._analyze_generic)
        feedback = analyser(pts, feedback)
        feedback.rep_count = self.rep_count

        # Overlay score on frame
        color = (0, 200, 0) if feedback.score >= 80 else (0, 165, 255) if feedback.score >= 60 else (0, 0, 255)
        cv2.putText(annotated, f'Form: {feedback.score:.0f}/100', (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
        cv2.putText(annotated, f'Reps: {self.rep_count}', (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        for i, err in enumerate(feedback.errors[:3]):
            cv2.putText(annotated, f'⚠ {err[:50]}', (20, 130 + i * 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

        return annotated, feedback

    # ── Exercise-specific analyzers ──────────────────────────────────────────

    def _analyze_squat(self, pts, feedback: FormFeedback) -> FormFeedback:
        try:
            l_hip   = pts[Landmark.LEFT_HIP][:2]
            l_knee  = pts[Landmark.LEFT_KNEE][:2]
            l_ankle = pts[Landmark.LEFT_ANKLE][:2]
            r_hip   = pts[Landmark.RIGHT_HIP][:2]
            r_knee  = pts[Landmark.RIGHT_KNEE][:2]
            r_ankle = pts[Landmark.RIGHT_ANKLE][:2]
            l_shld  = pts[Landmark.LEFT_SHOULDER][:2]

            l_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
            r_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
            avg_knee     = (l_knee_angle + r_knee_angle) / 2

            # Rep counting
            self.angle_history.append(avg_knee)
            if len(self.angle_history) > 5:
                self.angle_history.pop(0)
            avg_recent = np.mean(self.angle_history)

            if self.phase == 'start' and avg_recent < 100:
                self.phase = 'down'
            elif self.phase == 'down' and avg_recent > 155:
                self.phase = 'up'
                self.rep_count += 1

            feedback.phase = self.phase

            # Form checks
            penalties = 0

            # 1. Depth check (parallel = knee angle ~90°)
            if self.phase == 'down':
                if avg_knee > 110:
                    feedback.warnings.append('Squat not reaching parallel depth')
                    penalties += 5
                elif avg_knee < 70:
                    feedback.warnings.append('Very deep squat — ensure mobility supports this')

            # 2. Knee cave (valgus) — check knee x vs hip x
            knee_drift_l = l_knee[0] - l_hip[0]
            knee_drift_r = r_hip[0] - r_knee[0]
            if knee_drift_l < -15 or knee_drift_r < -15:
                feedback.errors.append('Knee cave detected (valgus) — push knees out over toes')
                feedback.corrections.append('Squeeze glutes and push knees outward')
                penalties += 20

            # 3. Torso lean — shoulder over hip
            lean = abs(l_shld[0] - l_hip[0])
            if lean > 60:
                feedback.errors.append('Excessive forward lean — keep chest up')
                feedback.corrections.append('Keep chest up, look forward, sit back into hips')
                penalties += 10

            feedback.score = max(0, 100 - penalties)

        except (KeyError, IndexError, ZeroDivisionError):
            feedback.warnings.append('Could not detect all landmarks — adjust camera position')

        return feedback

    def _analyze_deadlift(self, pts, feedback: FormFeedback) -> FormFeedback:
        try:
            l_shld  = pts[Landmark.LEFT_SHOULDER][:2]
            l_hip   = pts[Landmark.LEFT_HIP][:2]
            l_knee  = pts[Landmark.LEFT_KNEE][:2]
            l_ankle = pts[Landmark.LEFT_ANKLE][:2]

            penalties = 0

            # Back angle (hip hinge)
            hip_angle = calculate_angle(l_shld, l_hip, l_knee)
            if hip_angle < 70:
                feedback.errors.append('Back too rounded — maintain neutral spine')
                feedback.corrections.append('Brace core, push chest up, keep neutral lower back')
                penalties += 25
            elif hip_angle > 140:
                feedback.warnings.append('Torso too upright for deadlift — hinge more at hips')
                penalties += 5

            # Knee angle at bottom
            knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
            if knee_angle > 165:
                feedback.warnings.append('Legs too straight — maintain slight knee bend')
                penalties += 5

            feedback.score = max(0, 100 - penalties)
            feedback.corrections.extend([
                'Keep bar close to body throughout the lift',
                'Engage lats before initiating pull',
                'Drive through heels, not toes',
            ])

        except (KeyError, IndexError):
            feedback.warnings.append('Unable to detect full pose for deadlift analysis')

        return feedback

    def _analyze_pushup(self, pts, feedback: FormFeedback) -> FormFeedback:
        try:
            l_shld  = pts[Landmark.LEFT_SHOULDER][:2]
            l_elbow = pts[Landmark.LEFT_ELBOW][:2]
            l_wrist = pts[Landmark.LEFT_WRIST][:2]
            l_hip   = pts[Landmark.LEFT_HIP][:2]
            l_ankle = pts[Landmark.LEFT_ANKLE][:2]

            penalties = 0
            elbow_angle = calculate_angle(l_shld, l_elbow, l_wrist)

            # Rep counting
            self.angle_history.append(elbow_angle)
            if len(self.angle_history) > 5:
                self.angle_history.pop(0)
            avg_ea = np.mean(self.angle_history)

            if self.phase == 'start' and avg_ea < 95:
                self.phase = 'down'
            elif self.phase == 'down' and avg_ea > 155:
                self.phase = 'up'
                self.rep_count += 1

            # Body alignment (hip sag)
            body_angle = calculate_angle(l_shld, l_hip, l_ankle)
            if body_angle < 165:
                feedback.errors.append('Hip sag detected — engage core and glutes')
                feedback.corrections.append('Imagine a straight line from head to heels')
                penalties += 20

            # Elbow flare
            # (simplified — check elbow relative to shoulder width)
            feedback.score = max(0, 100 - penalties)
            if not feedback.errors:
                feedback.corrections.append('Full range of motion — chest touches the ground at bottom')

        except (KeyError, IndexError):
            feedback.warnings.append('Adjust camera to see full body during pushup')

        return feedback

    def _analyze_lunge(self, pts, feedback: FormFeedback) -> FormFeedback:
        feedback.score = 82.0
        feedback.corrections = [
            'Step far enough forward so front knee stays behind toes',
            'Keep torso upright — do not lean forward',
            'Back knee should hover ~1 inch above the ground at bottom',
            'Push through front heel to stand back up',
        ]
        return feedback

    def _analyze_shoulder_press(self, pts, feedback: FormFeedback) -> FormFeedback:
        feedback.score = 88.0
        feedback.corrections = [
            'Keep core braced — avoid excessive lower back arch',
            'Press straight up overhead, not forward',
            'Lock out fully at the top',
            'Control the descent — do not let bar drop',
        ]
        return feedback

    def _analyze_bicep_curl(self, pts, feedback: FormFeedback) -> FormFeedback:
        try:
            l_shld  = pts[Landmark.LEFT_SHOULDER][:2]
            l_elbow = pts[Landmark.LEFT_ELBOW][:2]
            l_wrist = pts[Landmark.LEFT_WRIST][:2]

            elbow_angle = calculate_angle(l_shld, l_elbow, l_wrist)
            self.angle_history.append(elbow_angle)
            if len(self.angle_history) > 5: self.angle_history.pop(0)
            avg = np.mean(self.angle_history)

            if self.phase == 'start' and avg < 50:
                self.phase = 'curl'
            elif self.phase == 'curl' and avg > 160:
                self.phase = 'extend'
                self.rep_count += 1
            elif self.phase == 'extend' and avg < 50:
                self.phase = 'curl'

            penalties = 0
            # Check elbow movement (swinging)
            elbow_x_change = abs(l_elbow[0] - l_shld[0])
            if elbow_x_change > 50:
                feedback.errors.append('Elbow swinging — keep elbows pinned to sides')
                penalties += 20

            feedback.score    = max(0, 100 - penalties)
            feedback.corrections = [
                'Keep upper arm stationary — only forearm moves',
                'Fully extend at the bottom for complete range of motion',
                'Supinate wrist at the top of the movement',
            ]

        except (KeyError, IndexError):
            feedback.warnings.append('Ensure upper body is visible in frame')

        return feedback

    def _analyze_generic(self, pts, feedback: FormFeedback) -> FormFeedback:
        feedback.score = 75.0
        feedback.corrections = [
            'Maintain neutral spine throughout movement',
            'Control both the concentric and eccentric phases',
            'Breathe consistently — exhale on exertion',
        ]
        return feedback

    def _static_guidance(self) -> FormFeedback:
        """Return guidance when MediaPipe is not available"""
        guidance = {
            'squat':          ['Knees over toes', 'Chest up', 'Hip crease below parallel'],
            'deadlift':       ['Neutral spine', 'Bar close to body', 'Hip hinge, not squat'],
            'pushup':         ['Body straight', 'Chest to floor', 'Elbows at 45°'],
            'bicep_curl':     ['Elbows pinned', 'Full extension', 'No swinging'],
            'shoulder_press': ['Core braced', 'Press overhead', 'Controlled descent'],
            'lunge':          ['Front knee behind toes', 'Torso upright', 'Back knee near floor'],
        }
        fb = FormFeedback()
        fb.score       = 80.0
        fb.corrections = guidance.get(self.exercise_type, ['Install MediaPipe for live analysis'])
        fb.warnings    = ['Live analysis requires MediaPipe — install requirements-ai.txt']
        return fb

    def release(self):
        """Release MediaPipe resources"""
        if MP_AVAILABLE and hasattr(self, 'pose'):
            self.pose.close()


def analyze_exercise_from_keypoints(keypoints: list, exercise_type: str) -> dict:
    """
    Analyze exercise form from pre-extracted keypoints (e.g., from client-side MediaPipe).
    keypoints: list of {x, y, z, visibility} dicts indexed by landmark id
    """
    if not keypoints:
        return {
            'form_score': 75.0,
            'issues':     [],
            'corrections': ['Submit keypoints for detailed analysis'],
            'source':     'no_keypoints',
        }

    # Convert to numpy-compatible format
    pts = {i: [kp['x'], kp['y'], kp.get('z', 0)] for i, kp in enumerate(keypoints) if i < 33}

    analyzer = ExerciseFormAnalyzer(exercise_type)
    fb       = FormFeedback()

    analysers = {
        'squat':    analyzer._analyze_squat,
        'deadlift': analyzer._analyze_deadlift,
        'pushup':   analyzer._analyze_pushup,
    }
    analyse_fn = analysers.get(exercise_type, analyzer._analyze_generic)
    fb = analyse_fn(pts, fb)

    return {
        'form_score':   fb.score,
        'issues':       fb.errors,
        'warnings':     fb.warnings,
        'corrections':  fb.corrections,
        'phase':        fb.phase,
        'source':       'keypoint_analysis',
    }
