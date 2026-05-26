"""
AI Meme Face Camera Application
A real-time face detection and meme effect application using MediaPipe and OpenCV.
"""

__version__ = "1.0.0"
__author__ = "AI Developer"
__description__ = "Real-time AI Meme Face Camera with facial expression detection"

from .camera import Camera, FrameBuffer
from .face_detector import FaceDetector, FaceLandmarkIndices
from .expressions import ExpressionDetector
from .meme_modes import ModeManager, GigachadMode, TrollMode, LaserEyesMode
from .utils import Colors, calculate_distance, draw_text, screenshot_frame

__all__ = [
    'Camera',
    'FrameBuffer',
    'FaceDetector',
    'FaceLandmarkIndices',
    'ExpressionDetector',
    'ModeManager',
    'Colors',
    'calculate_distance',
    'draw_text',
    'screenshot_frame'
]
