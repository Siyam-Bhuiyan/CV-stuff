"""
Utility functions for the Meme Face Camera application.
Includes helpers for drawing, calculations, and file management.
"""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import os


class Colors:
    """Color constants for drawing."""
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    YELLOW = (0, 255, 255)
    CYAN = (255, 255, 0)
    MAGENTA = (255, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    LIGHT_GREEN = (100, 255, 100)
    LIGHT_BLUE = (255, 200, 100)


def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points."""
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def calculate_ratio(distance1, distance2):
    """Calculate ratio of two distances safely."""
    if distance2 == 0:
        return 0
    return distance1 / distance2


def draw_text(image, text, position, font_scale=1.0, thickness=2,
              color=Colors.WHITE, bg_color=None, padding=5):
    """Draw text with optional background."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    x, y = position
    
    if bg_color is not None:
        # Draw background rectangle
        cv2.rectangle(image, (x - padding, y - text_size[1] - padding),
                     (x + text_size[0] + padding, y + padding), bg_color, -1)
    
    cv2.putText(image, text, (x, y), font, font_scale, color, thickness)


def draw_circle(image, center, radius, color=Colors.RED, thickness=2):
    """Draw a circle on the image."""
    cv2.circle(image, (int(center[0]), int(center[1])), radius, color, thickness)


def draw_line(image, pt1, pt2, color=Colors.GREEN, thickness=2):
    """Draw a line between two points."""
    cv2.line(image, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])),
            color, thickness)


def draw_polygon(image, points, color=Colors.YELLOW, thickness=2, filled=False):
    """Draw a polygon from a list of points."""
    if not points:
        return
    points = np.array([(int(p[0]), int(p[1])) for p in points], dtype=np.int32)
    if filled:
        cv2.fillPoly(image, [points], color)
    else:
        cv2.polylines(image, [points], True, color, thickness)


def draw_landmarks(image, landmarks, color=Colors.GREEN, thickness=1):
    """Draw all facial landmarks on the image."""
    if landmarks is None:
        return
    
    for landmark in landmarks:
        x, y = int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])
        cv2.circle(image, (x, y), 1, color, thickness)


def create_meme_text(text, font_size=80, width=800, bg_color=(0, 0, 0)):
    """Create a meme-style text image with white impact font."""
    height = 150
    image = np.ones((height, width, 3), dtype=np.uint8) * bg_color[0]
    
    font = cv2.FONT_HERSHEY_BOLD
    font_scale = min(2.0, width / (len(text) * 20))
    thickness = 3
    
    # Get text size
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    # Center text
    x = (width - text_size[0]) // 2
    y = (height + text_size[1]) // 2
    
    # Draw text with outline effect
    for adj_x in range(-2, 3):
        for adj_y in range(-2, 3):
            if adj_x != 0 or adj_y != 0:
                cv2.putText(image, text, (x + adj_x, y + adj_y), font,
                           font_scale, (0, 0, 0), thickness)
    
    cv2.putText(image, text, (x, y), font, font_scale, (255, 255, 255), thickness)
    
    return image


def blur_region(image, x, y, width, height, blur_strength=25):
    """Blur a specific region of the image."""
    if blur_strength % 2 == 0:
        blur_strength += 1
    
    x = max(0, x)
    y = max(0, y)
    x_end = min(image.shape[1], x + width)
    y_end = min(image.shape[0], y + height)
    
    region = image[y:y_end, x:x_end]
    blurred = cv2.blur(region, (blur_strength, blur_strength))
    image[y:y_end, x:x_end] = blurred


def sharpen_region(image, x, y, width, height):
    """Sharpen a specific region of the image."""
    x = max(0, x)
    y = max(0, y)
    x_end = min(image.shape[1], x + width)
    y_end = min(image.shape[0], y + height)
    
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    
    region = image[y:y_end, x:x_end]
    sharpened = cv2.filter2D(region, -1, kernel)
    image[y:y_end, x:x_end] = sharpened


def add_glow(image, center, radius, color=Colors.CYAN, intensity=0.3):
    """Add a glow effect around a point."""
    overlay = image.copy()
    cv2.circle(overlay, (int(center[0]), int(center[1])), radius, color, -1)
    cv2.addWeighted(image, 1 - intensity, overlay, intensity, 0, image)


def warp_face_region(image, src_points, dst_points):
    """Warp a region of the face using perspective transform."""
    try:
        src_points = np.float32(src_points)
        dst_points = np.float32(dst_points)
        
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        warped = cv2.warpPerspective(image, matrix, (image.shape[1], image.shape[0]))
        return warped
    except:
        return image


def create_laser_effect(image, start_point, end_point, length=100):
    """Create a laser beam effect from start to end point."""
    # Calculate direction
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    
    dist = np.sqrt(dx**2 + dy**2)
    if dist == 0:
        return
    
    # Normalize and extend
    dx = (dx / dist) * length
    dy = (dy / dist) * length
    
    laser_end = (int(start_point[0] + dx), int(start_point[1] + dy))
    
    # Draw laser with glow
    for i in range(20, 0, -1):
        alpha = i / 20
        color_intensity = int(255 * alpha)
        cv2.line(image, start_point, laser_end,
                (0, 255, int(255 * (1 - alpha))), max(1, i // 5))


def screenshot_frame(frame, output_dir="screenshots"):
    """Save a screenshot of the current frame."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = output_path / f"meme_shot_{timestamp}.png"
    
    success = cv2.imwrite(str(filename), frame)
    return str(filename) if success else None


def get_fps(frame_count, start_time):
    """Calculate current FPS."""
    elapsed = (datetime.now() - start_time).total_seconds()
    if elapsed < 0.1:
        return 0
    return frame_count / elapsed


def normalize_landmarks(landmarks, image_shape):
    """Convert normalized landmarks to pixel coordinates."""
    h, w = image_shape[:2]
    normalized = []
    for landmark in landmarks:
        x = int(landmark.x * w)
        y = int(landmark.y * h)
        z = landmark.z  # Depth
        normalized.append((x, y, z))
    return normalized


def get_eye_aspect_ratio(eye_landmarks):
    """Calculate eye aspect ratio for blink detection."""
    if len(eye_landmarks) < 6:
        return 0
    
    # Distance between vertical landmarks
    vertical1 = calculate_distance(eye_landmarks[1], eye_landmarks[5])
    vertical2 = calculate_distance(eye_landmarks[2], eye_landmarks[4])
    
    # Distance between horizontal landmarks
    horizontal = calculate_distance(eye_landmarks[0], eye_landmarks[3])
    
    ear = (vertical1 + vertical2) / (2 * horizontal)
    return ear


def get_mouth_aspect_ratio(mouth_landmarks):
    """Calculate mouth aspect ratio for open mouth detection."""
    if len(mouth_landmarks) < 20:
        return 0
    
    # Top to bottom distance
    vertical = calculate_distance(mouth_landmarks[2], mouth_landmarks[16])
    
    # Left to right distance
    horizontal = calculate_distance(mouth_landmarks[0], mouth_landmarks[12])
    
    mar = vertical / horizontal if horizontal > 0 else 0
    return mar


def overlay_image(bg_image, overlay_image, x, y, alpha=0.7):
    """Overlay one image on top of another with transparency."""
    try:
        # Ensure overlay fits within bounds
        x = max(0, x)
        y = max(0, y)
        
        y_end = min(bg_image.shape[0], y + overlay_image.shape[0])
        x_end = min(bg_image.shape[1], x + overlay_image.shape[1])
        
        overlay_height = y_end - y
        overlay_width = x_end - x
        
        if overlay_height <= 0 or overlay_width <= 0:
            return
        
        # Resize overlay if needed
        if overlay_image.shape[0] != overlay_height or overlay_image.shape[1] != overlay_width:
            resized = cv2.resize(overlay_image, (overlay_width, overlay_height))
        else:
            resized = overlay_image
        
        # Apply alpha blending
        bg_region = bg_image[y:y_end, x:x_end]
        cv2.addWeighted(resized, alpha, bg_region, 1 - alpha, 0, bg_region)
        
    except Exception as e:
        print(f"Error overlaying image: {e}")


def create_gradient(width, height, color1=(255, 0, 0), color2=(0, 0, 255)):
    """Create a gradient image between two colors."""
    image = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        ratio = i / height
        color = tuple(int(color1[j] * (1 - ratio) + color2[j] * ratio) for j in range(3))
        image[i, :] = color
    return image


def create_checkerboard(width, height, square_size=20, color1=(200, 200, 200), color2=(100, 100, 100)):
    """Create a checkerboard pattern."""
    image = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(0, height, square_size):
        for j in range(0, width, square_size):
            if ((i // square_size) + (j // square_size)) % 2 == 0:
                image[i:i+square_size, j:j+square_size] = color1
            else:
                image[i:i+square_size, j:j+square_size] = color2
    return image
