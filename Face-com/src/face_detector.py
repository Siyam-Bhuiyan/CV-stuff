"""
Face detection and landmark tracking using MediaPipe Face Mesh.
Provides efficient real-time face and landmark detection.
"""

import mediapipe as mp
import numpy as np
from .utils import normalize_landmarks, calculate_distance


class FaceDetector:
    """Detects faces and extracts facial landmarks using MediaPipe."""
    
    def __init__(self, max_faces=2, min_detection_confidence=0.5):
        """
        Initialize the face detector.
        
        Args:
            max_faces: Maximum number of faces to detect
            min_detection_confidence: Confidence threshold for detection
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=max_faces,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5
        )
        
        # Define facial landmark indices for different regions
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 398, 373, 380]
        self.LEFT_EYEBROW = [70, 63, 105, 66, 107]
        self.RIGHT_EYEBROW = [336, 296, 334, 293, 300]
        
        self.MOUTH_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 17, 181, 91, 206]
        self.MOUTH_INNER = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 14, 178, 88, 95]
        
        self.NOSE = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.FACE_OUTLINE = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        
        self.FOREHEAD = [10, 109, 67, 103, 54, 21, 162, 127, 234, 132, 58]
        self.CHIN = [152, 148, 176, 149, 150, 136, 172, 58, 132, 93]
        
    def detect_faces(self, image):
        """
        Detect faces in the image.
        
        Args:
            image: BGR image from OpenCV
            
        Returns:
            List of detected faces with landmarks
        """
        # Convert BGR to RGB for MediaPipe
        rgb_image = image[..., ::-1]
        
        results = self.face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            return []
        
        faces = []
        for face_landmarks in results.multi_face_landmarks:
            faces.append({
                'landmarks': face_landmarks,
                'landmarks_normalized': normalize_landmarks(face_landmarks.landmark, image.shape)
            })
        
        return faces
    
    def get_face_bbox(self, landmarks_normalized, image_shape, padding=20):
        """
        Get bounding box from face landmarks.
        
        Args:
            landmarks_normalized: Normalized landmark coordinates
            image_shape: Shape of the image
            padding: Padding around the face
            
        Returns:
            (x, y, width, height) of bounding box
        """
        if not landmarks_normalized:
            return None
        
        x_coords = [l[0] for l in landmarks_normalized]
        y_coords = [l[1] for l in landmarks_normalized]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        x = max(0, int(x_min - padding))
        y = max(0, int(y_min - padding))
        w = min(image_shape[1] - x, int((x_max - x_min) + 2 * padding))
        h = min(image_shape[0] - y, int((y_max - y_min) + 2 * padding))
        
        return (x, y, w, h)
    
    def get_eye_region(self, landmarks_normalized, eye_type='left'):
        """
        Get eye region landmarks.
        
        Args:
            landmarks_normalized: All landmarks
            eye_type: 'left' or 'right'
            
        Returns:
            List of eye landmark coordinates
        """
        eye_indices = self.LEFT_EYE if eye_type == 'left' else self.RIGHT_EYE
        return [landmarks_normalized[i] for i in eye_indices]
    
    def get_mouth_region(self, landmarks_normalized):
        """
        Get mouth region landmarks.
        
        Args:
            landmarks_normalized: All landmarks
            
        Returns:
            Tuple of (outer_mouth, inner_mouth)
        """
        outer = [landmarks_normalized[i] for i in self.MOUTH_OUTER]
        inner = [landmarks_normalized[i] for i in self.MOUTH_INNER]
        return outer, inner
    
    def get_nose_region(self, landmarks_normalized):
        """Get nose landmarks."""
        return [landmarks_normalized[i] for i in self.NOSE]
    
    def get_jawline(self, landmarks_normalized):
        """Get jawline landmarks."""
        return [landmarks_normalized[i] for i in self.CHIN]
    
    def get_forehead(self, landmarks_normalized):
        """Get forehead region."""
        return [landmarks_normalized[i] for i in self.FOREHEAD]
    
    def get_face_outline(self, landmarks_normalized):
        """Get complete face outline."""
        return [landmarks_normalized[i] for i in self.FACE_OUTLINE]
    
    def get_head_pose(self, landmarks_normalized):
        """
        Estimate head pose (rotation) from landmarks.
        
        Args:
            landmarks_normalized: All landmarks
            
        Returns:
            Dict with euler angles (roll, pitch, yaw)
        """
        # Key points for pose estimation
        nose_tip = landmarks_normalized[4]
        chin = landmarks_normalized[152]
        left_eye = landmarks_normalized[33]
        right_eye = landmarks_normalized[263]
        
        # Calculate angles
        # Roll (tilt left-right)
        eye_vector = (right_eye[0] - left_eye[0], right_eye[1] - left_eye[1])
        roll = np.arctan2(eye_vector[1], eye_vector[0]) * 180 / np.pi
        
        # Pitch (nod up-down)
        nose_chin = (chin[1] - nose_tip[1], chin[0] - nose_tip[0])
        pitch = np.arctan2(nose_chin[0], nose_chin[1]) * 180 / np.pi
        
        # Yaw (turn left-right)
        nose_center_x = (left_eye[0] + right_eye[0]) / 2
        yaw = (nose_tip[0] - nose_center_x) * 10  # Scale for better visualization
        
        return {
            'roll': roll,
            'pitch': pitch,
            'yaw': yaw
        }
    
    def get_face_distance_to_camera(self, landmarks_normalized):
        """
        Estimate face distance to camera based on landmark spread.
        
        Args:
            landmarks_normalized: All landmarks
            
        Returns:
            Distance estimation (lower = closer)
        """
        # Use face width as proxy for distance
        left_eye = landmarks_normalized[33]
        right_eye = landmarks_normalized[263]
        face_width = calculate_distance(left_eye, right_eye)
        return 1.0 / max(face_width, 0.01)
    
    def close(self):
        """Close the face mesh detector."""
        self.face_mesh.close()


class FaceLandmarkIndices:
    """Predefined indices for important facial landmarks in MediaPipe Face Mesh."""
    
    # Eyes
    LEFT_EYE_CENTER = 33
    RIGHT_EYE_CENTER = 263
    
    # Nose
    NOSE_TIP = 4
    NOSE_ROOT = 1
    NOSE_LEFT = 98
    NOSE_RIGHT = 327
    
    # Mouth
    MOUTH_CENTER = 0
    MOUTH_LEFT = 61
    MOUTH_RIGHT = 291
    MOUTH_TOP = 13
    MOUTH_BOTTOM = 14
    
    # Face outline
    CHIN = 152
    JAW_LEFT = 178
    JAW_RIGHT = 397
    
    # Eyebrows
    LEFT_EYEBROW_INNER = 105
    LEFT_EYEBROW_OUTER = 70
    RIGHT_EYEBROW_INNER = 334
    RIGHT_EYEBROW_OUTER = 336
    
    # Cheeks
    LEFT_CHEEK = 50
    RIGHT_CHEEK = 280
