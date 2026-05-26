"""
Camera module for real-time video capture and processing.
Handles webcam input, frame buffering, and FPS management.
"""

import cv2
import threading
import time
from collections import deque


class Camera:
    """Manages real-time webcam capture and frame processing."""
    
    def __init__(self, camera_index=0, fps=30, width=1280, height=720):
        """
        Initialize camera.
        
        Args:
            camera_index: Index of camera to use (0 = default)
            fps: Target FPS
            width: Frame width
            height: Frame height
        """
        self.camera_index = camera_index
        self.target_fps = fps
        self.target_width = width
        self.target_height = height
        
        self.cap = None
        self.is_running = False
        self.thread = None
        
        # Frame buffer
        self.frame_queue = deque(maxlen=1)
        self.frame_lock = threading.Lock()
        
        # FPS tracking
        self.frame_times = deque(maxlen=30)
        self.current_fps = 0
        self.frame_count = 0
        
        # Available cameras
        self.available_cameras = self._detect_cameras()
    
    def _detect_cameras(self, max_index=10):
        """Detect available cameras."""
        available = []
        for i in range(max_index):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
            else:
                break
        return available
    
    def get_available_cameras(self):
        """Get list of available camera indices."""
        return self.available_cameras
    
    def initialize(self):
        """Initialize camera capture."""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"Failed to open camera {self.camera_index}")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer
            
            # Get actual properties
            self.actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def start(self):
        """Start camera thread."""
        if not self.cap:
            if not self.initialize():
                return False
        
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            time.sleep(0.5)  # Wait for thread to start
        
        return True
    
    def _capture_loop(self):
        """Main capture loop running in separate thread."""
        while self.is_running:
            ret, frame = self.cap.read()
            
            if ret:
                with self.frame_lock:
                    self.frame_queue.append(frame)
                    self.frame_count += 1
                
                # Update FPS
                current_time = time.time()
                self.frame_times.append(current_time)
                
                if len(self.frame_times) > 1:
                    fps_interval = self.frame_times[-1] - self.frame_times[0]
                    if fps_interval > 0:
                        self.current_fps = len(self.frame_times) / fps_interval
            else:
                print("Error reading frame from camera")
                time.sleep(0.01)
    
    def get_frame(self):
        """
        Get the latest frame from camera.
        
        Returns:
            Latest frame or None if not available
        """
        if not self.is_running:
            return None
        
        with self.frame_lock:
            if len(self.frame_queue) > 0:
                return self.frame_queue[-1].copy()
        
        return None
    
    def get_fps(self):
        """Get current FPS."""
        return self.current_fps
    
    def get_frame_count(self):
        """Get total frames captured."""
        return self.frame_count
    
    def get_resolution(self):
        """Get actual camera resolution."""
        if self.cap:
            return (self.actual_width, self.actual_height)
        return None
    
    def switch_camera(self, camera_index):
        """
        Switch to different camera.
        
        Args:
            camera_index: Index of camera to switch to
            
        Returns:
            True if successful
        """
        if camera_index not in self.available_cameras:
            print(f"Camera {camera_index} not available")
            return False
        
        was_running = self.is_running
        self.stop()
        
        self.camera_index = camera_index
        
        if was_running:
            return self.start()
        
        return True
    
    def stop(self):
        """Stop camera capture."""
        self.is_running = False
        
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None
        
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def take_snapshot(self):
        """Get current frame without processing."""
        return self.get_frame()
    
    def flip_frame(self, frame, flip_code=1):
        """
        Flip frame (mirror horizontally for selfie camera).
        
        Args:
            frame: Input frame
            flip_code: 1 for horizontal, 0 for vertical, -1 for both
            
        Returns:
            Flipped frame
        """
        return cv2.flip(frame, flip_code)
    
    def __del__(self):
        """Ensure camera is closed on deletion."""
        self.stop()


class FrameBuffer:
    """Thread-safe frame buffer for processing."""
    
    def __init__(self, maxsize=2):
        """Initialize frame buffer."""
        self.buffer = deque(maxlen=maxsize)
        self.lock = threading.Lock()
    
    def put(self, frame):
        """Add frame to buffer."""
        with self.lock:
            self.buffer.append(frame)
    
    def get(self):
        """Get latest frame from buffer."""
        with self.lock:
            if len(self.buffer) > 0:
                return self.buffer[-1]
        return None
    
    def get_all(self):
        """Get all frames in buffer."""
        with self.lock:
            return list(self.buffer)
    
    def clear(self):
        """Clear buffer."""
        with self.lock:
            self.buffer.clear()
    
    def size(self):
        """Get buffer size."""
        with self.lock:
            return len(self.buffer)
