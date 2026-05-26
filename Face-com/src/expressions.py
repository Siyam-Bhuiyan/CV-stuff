"""
Facial expression detection and recognition.
Detects: smiling, mouth open, blinking, surprised, angry, sleepy.
Uses landmark-based distance calculations and ratios.
"""

from .utils import calculate_distance, calculate_ratio, get_eye_aspect_ratio, get_mouth_aspect_ratio


class ExpressionDetector:
    """Detects and classifies facial expressions."""
    
    def __init__(self):
        """Initialize expression detector with thresholds."""
        # Blink detection
        self.EAR_THRESHOLD = 0.18  # Eye Aspect Ratio threshold
        self.BLINK_FRAMES = 3  # Frames to confirm blink
        
        # Mouth
        self.MOUTH_OPEN_THRESHOLD = 0.5  # Mouth Aspect Ratio threshold
        self.SMILE_THRESHOLD = 0.2
        
        # Expression thresholds
        self.ANGRY_THRESHOLD = 0.15
        self.SURPRISED_THRESHOLD = 0.3
        self.SLEEPY_THRESHOLD = 0.16
        
        # State tracking
        self.prev_ear_left = 0
        self.prev_ear_right = 0
        self.blink_counter_left = 0
        self.blink_counter_right = 0
        self.total_blinks = 0
        self.blink_detected = False
        self.prev_blink_detected = False
        self.sleepy_counter = 0
        self.sleepy_triggered = False
    
    def detect_blink(self, left_eye, right_eye):
        """
        Detect eye blink using Eye Aspect Ratio (EAR).
        
        Args:
            left_eye: Left eye landmarks
            right_eye: Right eye landmarks
            
        Returns:
            Dict with blink information
        """
        # Calculate EAR for both eyes
        ear_left = get_eye_aspect_ratio(left_eye)
        ear_right = get_eye_aspect_ratio(right_eye)
        avg_ear = (ear_left + ear_right) / 2
        
        # Detect blink (EAR falls below threshold)
        is_blink = avg_ear < self.EAR_THRESHOLD
        
        # Count consecutive blink frames
        if is_blink:
            self.blink_counter_left += 1
            self.blink_counter_right += 1
        else:
            # Blink finished
            if self.blink_counter_left >= self.BLINK_FRAMES:
                self.total_blinks += 1
                self.blink_detected = True
            else:
                self.blink_detected = False
            
            self.blink_counter_left = 0
            self.blink_counter_right = 0
        
        self.prev_ear_left = ear_left
        self.prev_ear_right = ear_right
        
        return {
            'is_blinking': is_blink,
            'blink_detected': self.blink_detected,
            'total_blinks': self.total_blinks,
            'ear_left': ear_left,
            'ear_right': ear_right,
            'avg_ear': avg_ear
        }
    
    def detect_mouth_open(self, mouth_outer, mouth_inner):
        """
        Detect if mouth is open using Mouth Aspect Ratio (MAR).
        
        Args:
            mouth_outer: Outer mouth landmarks
            mouth_inner: Inner mouth landmarks
            
        Returns:
            Dict with mouth information
        """
        mar = get_mouth_aspect_ratio(mouth_outer)
        is_open = mar > self.MOUTH_OPEN_THRESHOLD
        
        return {
            'is_open': is_open,
            'mouth_ratio': mar
        }
    
    def detect_smile(self, mouth_outer, mouth_inner, left_eye, right_eye):
        """
        Detect smile by analyzing mouth and eye region.
        
        Args:
            mouth_outer: Outer mouth landmarks
            mouth_inner: Inner mouth landmarks
            left_eye: Left eye landmarks
            right_eye: Right eye landmarks
            
        Returns:
            Dict with smile information
        """
        if not mouth_outer or len(mouth_outer) < 2:
            return {'is_smiling': False, 'smile_strength': 0}
        
        # Horizontal stretch of mouth corners
        mouth_left = mouth_outer[0]
        mouth_right = mouth_outer[6] if len(mouth_outer) > 6 else mouth_outer[-1]
        mouth_horizontal = calculate_distance(mouth_left, mouth_right)
        
        # Vertical height of mouth (should be small when smiling)
        if len(mouth_outer) > 15:
            mouth_top = mouth_outer[2]
            mouth_bottom = mouth_outer[14]
            mouth_vertical = calculate_distance(mouth_top, mouth_bottom)
        else:
            mouth_vertical = 1
        
        # Calculate smile ratio
        smile_ratio = calculate_ratio(mouth_horizontal, mouth_vertical + 0.001)
        
        # Eyes aspect ratio (eyes narrow when smiling - crows feet)
        left_eye_height = calculate_distance(left_eye[1], left_eye[5]) if len(left_eye) > 5 else 0
        left_eye_width = calculate_distance(left_eye[0], left_eye[3]) if len(left_eye) > 3 else 1
        right_eye_height = calculate_distance(right_eye[1], right_eye[5]) if len(right_eye) > 5 else 0
        right_eye_width = calculate_distance(right_eye[0], right_eye[3]) if len(right_eye) > 3 else 1
        
        eye_ratio_left = calculate_ratio(left_eye_height, left_eye_width)
        eye_ratio_right = calculate_ratio(right_eye_height, right_eye_width)
        avg_eye_ratio = (eye_ratio_left + eye_ratio_right) / 2
        
        # Combined smile metric
        is_smiling = smile_ratio > self.SMILE_THRESHOLD and avg_eye_ratio < 0.5
        smile_strength = min(smile_ratio, 1.0)
        
        return {
            'is_smiling': is_smiling,
            'smile_strength': smile_strength,
            'smile_ratio': smile_ratio,
            'eye_ratio': avg_eye_ratio
        }
    
    def detect_surprised(self, left_eye, right_eye, mouth_outer):
        """
        Detect surprised expression (wide eyes + open mouth).
        
        Args:
            left_eye: Left eye landmarks
            right_eye: Right eye landmarks
            mouth_outer: Outer mouth landmarks
            
        Returns:
            Dict with surprise information
        """
        # Wide eyes (high EAR)
        ear_left = get_eye_aspect_ratio(left_eye)
        ear_right = get_eye_aspect_ratio(right_eye)
        avg_ear = (ear_left + ear_right) / 2
        eyes_wide = avg_ear > 0.4
        
        # Open mouth
        mar = get_mouth_aspect_ratio(mouth_outer)
        mouth_open = mar > self.MOUTH_OPEN_THRESHOLD
        
        is_surprised = eyes_wide and mouth_open
        surprise_strength = (min(avg_ear, 1.0) + min(mar, 1.0)) / 2
        
        return {
            'is_surprised': is_surprised,
            'surprise_strength': surprise_strength,
            'eyes_wide': eyes_wide,
            'mouth_open': mouth_open
        }
    
    def detect_angry(self, left_eyebrow, right_eyebrow, left_eye, right_eye):
        """
        Detect angry expression (furrowed brows + narrow eyes).
        
        Args:
            left_eyebrow: Left eyebrow landmarks
            right_eyebrow: Right eyebrow landmarks
            left_eye: Left eye landmarks
            right_eye: Right eye landmarks
            
        Returns:
            Dict with anger information
        """
        # Eyebrow position (lowered = angry)
        if len(left_eyebrow) > 0 and len(right_eyebrow) > 0:
            left_brow_center_y = sum(p[1] for p in left_eyebrow) / len(left_eyebrow)
            right_brow_center_y = sum(p[1] for p in right_eyebrow) / len(right_eyebrow)
            left_eye_y = left_eye[0][1] if len(left_eye) > 0 else 0
            right_eye_y = right_eye[0][1] if len(right_eye) > 0 else 0
            
            # Brows closer to eyes = angry
            left_brow_distance = left_brow_center_y - left_eye_y
            right_brow_distance = right_brow_center_y - right_eye_y
            avg_brow_distance = (left_brow_distance + right_brow_distance) / 2
            brows_lowered = avg_brow_distance < -0.05
        else:
            brows_lowered = False
        
        # Narrow eyes (low EAR)
        ear_left = get_eye_aspect_ratio(left_eye)
        ear_right = get_eye_aspect_ratio(right_eye)
        avg_ear = (ear_left + ear_right) / 2
        eyes_narrow = avg_ear < self.ANGRY_THRESHOLD
        
        is_angry = brows_lowered and eyes_narrow
        anger_strength = 1.0 - min(avg_ear, 1.0)
        
        return {
            'is_angry': is_angry,
            'anger_strength': anger_strength,
            'brows_lowered': brows_lowered,
            'eyes_narrow': eyes_narrow
        }
    
    def detect_sleepy(self, left_eye, right_eye):
        """
        Detect sleepy/drowsy expression (consistently low EAR).
        
        Args:
            left_eye: Left eye landmarks
            right_eye: Right eye landmarks
            
        Returns:
            Dict with sleepy information
        """
        # Calculate EAR
        ear_left = get_eye_aspect_ratio(left_eye)
        ear_right = get_eye_aspect_ratio(right_eye)
        avg_ear = (ear_left + ear_right) / 2
        
        # Accumulate sleepy frames
        if avg_ear < self.SLEEPY_THRESHOLD:
            self.sleepy_counter += 1
        else:
            self.sleepy_counter = max(0, self.sleepy_counter - 2)
        
        # Trigger alert after 10 frames of low EAR
        is_sleepy = self.sleepy_counter > 10
        if is_sleepy and not self.sleepy_triggered:
            self.sleepy_triggered = True
        elif not is_sleepy:
            self.sleepy_triggered = False
        
        return {
            'is_sleepy': is_sleepy,
            'sleepy_level': min(self.sleepy_counter / 30, 1.0),
            'sleepy_triggered': self.sleepy_triggered,
            'avg_ear': avg_ear
        }
    
    def detect_all_expressions(self, face_detector, landmarks_normalized):
        """
        Detect all expressions at once.
        
        Args:
            face_detector: FaceDetector instance
            landmarks_normalized: Normalized landmarks
            
        Returns:
            Dict with all expression detections
        """
        # Get facial regions
        left_eye = face_detector.get_eye_region(landmarks_normalized, 'left')
        right_eye = face_detector.get_eye_region(landmarks_normalized, 'right')
        mouth_outer, mouth_inner = face_detector.get_mouth_region(landmarks_normalized)
        left_eyebrow = [landmarks_normalized[i] for i in face_detector.LEFT_EYEBROW]
        right_eyebrow = [landmarks_normalized[i] for i in face_detector.RIGHT_EYEBROW]
        
        # Detect all expressions
        expressions = {
            'blink': self.detect_blink(left_eye, right_eye),
            'mouth_open': self.detect_mouth_open(mouth_outer, mouth_inner),
            'smile': self.detect_smile(mouth_outer, mouth_inner, left_eye, right_eye),
            'surprised': self.detect_surprised(left_eye, right_eye, mouth_outer),
            'angry': self.detect_angry(left_eyebrow, right_eyebrow, left_eye, right_eye),
            'sleepy': self.detect_sleepy(left_eye, right_eye)
        }
        
        return expressions
    
    def get_dominant_expression(self, expressions):
        """
        Determine the dominant/most prominent expression.
        
        Args:
            expressions: Dict of all detected expressions
            
        Returns:
            Tuple of (expression_name, confidence)
        """
        scores = {
            'happy': expressions['smile'].get('smile_strength', 0),
            'surprised': expressions['surprised'].get('surprise_strength', 0) if expressions['surprised'].get('is_surprised') else 0,
            'angry': expressions['angry'].get('anger_strength', 0) if expressions['angry'].get('is_angry') else 0,
            'sleepy': expressions['sleepy'].get('sleepy_level', 0) if expressions['sleepy'].get('is_sleepy') else 0,
            'neutral': 0.5
        }
        
        # Normalize scores
        max_score = max(scores.values())
        if max_score > 0:
            dominant = max(scores, key=scores.get)
            return dominant, scores[dominant]
        
        return 'neutral', 0.5
    
    def reset(self):
        """Reset expression tracking counters."""
        self.blink_counter_left = 0
        self.blink_counter_right = 0
        self.sleepy_counter = 0
        self.sleepy_triggered = False
