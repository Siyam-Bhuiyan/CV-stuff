"""
Configuration file for AI Meme Face Camera
Customize settings here without modifying core code.
"""

# Camera Settings
CAMERA_INDEX = 0  # Default camera (0 = built-in)
CAMERA_WIDTH = 1280  # Frame width
CAMERA_HEIGHT = 720  # Frame height
CAMERA_FPS = 30  # Target frames per second
FLIP_CAMERA = True  # Mirror for selfie cameras

# Face Detection Settings
MAX_FACES = 2  # Maximum faces to detect simultaneously
MIN_DETECTION_CONFIDENCE = 0.5  # MediaPipe confidence threshold
MIN_TRACKING_CONFIDENCE = 0.5  # Tracking confidence

# Expression Detection Thresholds
EAR_THRESHOLD = 0.18  # Eye Aspect Ratio - blink detection
MOUTH_OPEN_THRESHOLD = 0.5  # Mouth Aspect Ratio
SMILE_THRESHOLD = 0.2  # Smile detection sensitivity
ANGRY_THRESHOLD = 0.15  # Anger detection
SURPRISED_THRESHOLD = 0.3  # Surprise detection
SLEEPY_THRESHOLD = 0.16  # Sleepy/drowsy detection

# UI Settings
UI_WIDTH = 1400
UI_HEIGHT = 900
UI_THEME = "dark"  # Theme: "dark" or "light"
SHOW_LANDMARKS = True  # Show facial landmarks by default
SHOW_EXPRESSIONS = True  # Show expression labels
SHOW_BBOX = True  # Show face bounding box

# Performance Settings
FRAME_BUFFER_SIZE = 1  # Size of frame buffer (1 = minimal latency)
LANDMARK_SKIP = 4  # Draw every Nth landmark (1 = all, 4 = sparse)
FPS_DISPLAY = True  # Show FPS counter
FPS_UPDATE_INTERVAL = 1  # Update FPS every N frames

# Screenshot Settings
SCREENSHOT_DIR = "screenshots"
SCREENSHOT_FORMAT = "png"  # Format: png, jpg, bmp
SCREENSHOT_QUALITY = 95  # JPEG quality (1-100)

# Sound Settings
ENABLE_SOUNDS = False  # Enable sound effects (requires pygame)
SOUND_VOLUME = 0.5  # Volume (0.0 - 1.0)
SOUNDS_DIR = "sounds"

# Meme Mode Settings
DEFAULT_MODE = "gigachad"  # Default meme mode at startup
MODE_TRANSITION_SPEED = 0.2  # Speed of effect transitions
ENABLE_MODE_ROTATION = True  # Auto-rotate modes

# Graphics Settings
ENABLE_ANTI_ALIASING = True  # Smooth edges
EFFECT_INTENSITY = 1.0  # Effect intensity multiplier (0.5 - 2.0)
ENABLE_BLUR_EFFECTS = True  # Allow blur effects
ENABLE_GLOW_EFFECTS = True  # Allow glow effects

# Debug Settings
DEBUG_MODE = False  # Show debug information
LOG_FPS = False  # Log FPS to console
LOG_LANDMARKS = False  # Log landmark data
LOG_EXPRESSIONS = False  # Log expression data

# Color Settings (BGR format)
PRIMARY_COLOR = (0, 255, 0)  # Green
SECONDARY_COLOR = (0, 255, 255)  # Cyan
HIGHLIGHT_COLOR = (255, 0, 0)  # Blue
WARNING_COLOR = (0, 0, 255)  # Red
TEXT_COLOR = (255, 255, 255)  # White
BG_COLOR = (0, 0, 0)  # Black

# Advanced Settings
USE_GPU = True  # Use GPU if available
MULTITHREADING = True  # Use multithreading for processing
OPTIMIZE_PERFORMANCE = True  # Enable performance optimizations
SMOOTH_TRACKING = True  # Smooth landmark tracking

# Keyboard Shortcuts (Future Implementation)
SHORTCUTS_ENABLED = True
SHORTCUT_START_STOP = 'space'
SHORTCUT_SCREENSHOT = 's'
SHORTCUT_NEXT_MODE = 'm'
SHORTCUT_PREV_MODE = 'n'
SHORTCUT_TOGGLE_LANDMARKS = 'l'
SHORTCUT_FULLSCREEN = 'f'
SHORTCUT_EXIT = 'escape'
