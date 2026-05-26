"""
Main application for AI Meme Face Camera.
Coordinates all modules for real-time face detection and meme effects.
"""

import cv2
import threading
import time
from datetime import datetime

from .camera import Camera
from .face_detector import FaceDetector
from .expressions import ExpressionDetector
from .meme_modes import ModeManager
from .utils import (
    draw_text, draw_polygon, Colors, screenshot_frame,
    normalize_landmarks
)


class MemeCameraApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.camera = Camera(width=1280, height=720, fps=30)
        self.face_detector = FaceDetector()
        self.expression_detector = ExpressionDetector()
        self.mode_manager = ModeManager()
        
        self.is_running = False
        self.processing_thread = None
        
        # Processing settings
        self.show_landmarks = True
        self.show_expressions = True
        self.show_bbox = True
        
        # Current state
        self.current_frame = None
        self.current_faces = []
        self.current_expressions = None
        self.current_expression = "neutral"
        self.processed_frame = None
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = datetime.now()
    
    def start_camera(self):
        """Start the camera and processing."""
        if not self.camera.start():
            print("Failed to start camera")
            return False
        
        time.sleep(1)  # Wait for camera to initialize
        
        self.is_running = True
        self.processing_thread = threading.Thread(
            target=self._process_loop,
            daemon=True
        )
        self.processing_thread.start()
        
        print("Camera started successfully")
        return True
    
    def stop_camera(self):
        """Stop the camera and processing."""
        self.is_running = False
        
        if self.processing_thread:
            self.processing_thread.join(timeout=2)
            self.processing_thread = None
        
        self.camera.stop()
        print("Camera stopped")
    
    def _process_loop(self):
        """Main processing loop running in separate thread."""
        while self.is_running:
            try:
                # Get frame from camera
                frame = self.camera.get_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                self.current_frame = frame.copy()
                
                # Detect faces
                self.current_faces = self.face_detector.detect_faces(frame)
                
                # Process each face
                expressions_list = []
                for face in self.current_faces:
                    landmarks = face['landmarks_normalized']
                    expr = self.expression_detector.detect_all_expressions(
                        self.face_detector, landmarks
                    )
                    expressions_list.append(expr)
                
                if expressions_list:
                    self.current_expressions = expressions_list[0]
                    dominant_expr, strength = self.expression_detector.get_dominant_expression(
                        expressions_list[0]
                    )
                    self.current_expression = dominant_expr
                
                # Apply visualization
                self.processed_frame = self._visualize_frame(
                    frame,
                    self.current_faces,
                    expressions_list
                )
                
                # Apply meme mode
                if self.processed_frame is not None:
                    self.processed_frame = self.mode_manager.apply_mode(
                        self.processed_frame,
                        self.current_faces,
                        self.face_detector,
                        self.current_expressions
                    )
                
                self.frame_count += 1
                
            except Exception as e:
                print(f"Error in processing loop: {e}")
                time.sleep(0.01)
    
    def _visualize_frame(self, frame, faces, expressions_list):
        """Visualize frame with detections."""
        output = frame.copy()
        
        for i, face in enumerate(faces):
            landmarks = face['landmarks_normalized']
            
            # Draw face bounding box
            if self.show_bbox:
                bbox = self.face_detector.get_face_bbox(landmarks, frame.shape)
                if bbox:
                    x, y, w, h = bbox
                    cv2.rectangle(output, (x, y), (x+w, y+h), Colors.GREEN, 2)
            
            # Draw landmarks
            if self.show_landmarks:
                self._draw_facial_landmarks(output, landmarks)
            
            # Draw expression info
            if self.show_expressions and i < len(expressions_list):
                self._draw_expression_info(output, expressions_list[i],
                                          landmarks, i)
        
        # Draw FPS
        fps = self.camera.get_fps()
        draw_text(output, f"FPS: {fps:.1f}", (10, 30),
                 font_scale=0.8, color=Colors.GREEN,
                 bg_color=Colors.BLACK, thickness=1)
        
        # Draw face count
        draw_text(output, f"Faces: {len(faces)}", (10, 65),
                 font_scale=0.8, color=Colors.CYAN,
                 bg_color=Colors.BLACK, thickness=1)
        
        return output
    
    def _draw_facial_landmarks(self, frame, landmarks, color=Colors.LIGHT_GREEN):
        """Draw facial landmarks on frame."""
        for i, landmark in enumerate(landmarks):
            x = int(landmark[0])
            y = int(landmark[1])
            
            # Draw only every 4th landmark to avoid clutter
            if i % 4 == 0:
                cv2.circle(frame, (x, y), 2, color, 1)
    
    def _draw_expression_info(self, frame, expressions, landmarks, face_id=0):
        """Draw expression information on frame."""
        # Get face position for info placement
        bbox = self.face_detector.get_face_bbox(landmarks, frame.shape)
        if not bbox:
            return
        
        x, y, w, h = bbox
        info_y = y - 40
        
        # Blink detection
        if expressions['blink']['blink_detected']:
            draw_text(frame, "BLINK", (x, info_y),
                     font_scale=0.7, color=Colors.YELLOW,
                     thickness=2)
        
        # Smile detection
        if expressions['smile']['is_smiling']:
            smile_str = int(expressions['smile']['smile_strength'] * 100)
            draw_text(frame, f"SMILE: {smile_str}%", (x+100, info_y),
                     font_scale=0.7, color=Colors.MAGENTA,
                     thickness=2)
        
        # Mouth open
        if expressions['mouth_open']['is_open']:
            draw_text(frame, "MOUTH OPEN", (x+250, info_y),
                     font_scale=0.7, color=Colors.RED,
                     thickness=2)
        
        # Surprised
        if expressions['surprised']['is_surprised']:
            draw_text(frame, "SURPRISED!", (x, info_y+30),
                     font_scale=0.7, color=Colors.CYAN,
                     thickness=2)
        
        # Angry
        if expressions['angry']['is_angry']:
            draw_text(frame, "ANGRY!", (x+120, info_y+30),
                     font_scale=0.7, color=Colors.RED,
                     thickness=2)
        
        # Sleepy
        if expressions['sleepy']['is_sleepy']:
            draw_text(frame, "SLEEPY ALERT!", (x+220, info_y+30),
                     font_scale=0.7, color=Colors.YELLOW,
                     thickness=2)
    
    def get_processed_frame(self):
        """Get the latest processed frame."""
        return self.processed_frame
    
    def take_screenshot(self):
        """Take a screenshot of current frame."""
        if self.processed_frame is not None:
            filename = screenshot_frame(self.processed_frame, "screenshots")
            return filename
        return None
    
    def get_statistics(self):
        """Get application statistics."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'total_frames': self.frame_count,
            'elapsed_time': elapsed,
            'average_fps': self.frame_count / elapsed if elapsed > 0 else 0,
            'current_fps': self.camera.get_fps(),
            'faces_detected': len(self.current_faces),
            'current_expression': self.current_expression
        }
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_camera()
        self.face_detector.close()
        print("Application closed")


def main():
    """Main entry point."""
    import tkinter as tk
    from .ui import MemeCameraUI
    
    # Create application
    app = MemeCameraApp()
    
    # Create UI
    root = tk.Tk()
    ui = MemeCameraUI(root, app)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication interrupted")
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
