"""
GUI Interface for the Meme Face Camera application.
Uses tkinter with modern styling.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import cv2
from PIL import Image, ImageTk
import numpy as np
from datetime import datetime


class MemeCameraUI:
    """Main UI window for the Meme Face Camera application."""
    
    def __init__(self, root, app):
        """
        Initialize UI.
        
        Args:
            root: Tkinter root window
            app: Main application instance
        """
        self.root = root
        self.app = app
        
        self.root.title("🎭 AI Meme Face Camera")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1a1a1a")
        
        # Configure styles
        self.setup_styles()
        
        # Main layout
        self.create_widgets()
        
        # Update thread
        self.running = True
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
    
    def setup_styles(self):
        """Setup custom styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Dark theme colors
        style.configure('TButton', background='#2a2a2a', foreground='#ffffff',
                       borderwidth=1, focuscolor='none')
        style.map('TButton', background=[('active', '#3a3a3a')])
        
        style.configure('TLabel', background='#1a1a1a', foreground='#ffffff')
        style.configure('TFrame', background='#1a1a1a')
        style.configure('TCombobox', fieldbackground='#2a2a2a', background='#2a2a2a',
                       foreground='#ffffff')
    
    def create_widgets(self):
        """Create UI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Video display area (left side)
        video_frame = ttk.LabelFrame(main_frame, text="📹 Camera Feed", padding=10)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.video_label = ttk.Label(video_frame, background='#000000')
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Control panel (right side)
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        control_frame.pack_propagate(False)
        
        # Create control sections
        self.create_control_section(control_frame)
    
    def create_control_section(self, parent):
        """Create control panel sections."""
        # Camera controls
        camera_frame = ttk.LabelFrame(parent, text="🎥 Camera", padding=10)
        camera_frame.pack(fill=tk.X, padx=5, pady=5)
        
        button_frame = ttk.Frame(camera_frame)
        button_frame.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(button_frame, text="▶ Start",
                                   command=self.on_start_camera)
        self.start_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹ Stop",
                                  command=self.on_stop_camera, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Camera selection
        ttk.Label(camera_frame, text="Camera:").pack(anchor=tk.W, pady=(10, 0))
        self.camera_combo = ttk.Combobox(camera_frame, state='readonly', width=15)
        self.camera_combo.pack(fill=tk.X, pady=5)
        self.camera_combo.bind('<<ComboboxSelected>>', self.on_camera_changed)
        
        # Meme modes
        mode_frame = ttk.LabelFrame(parent, text="😂 Meme Modes", padding=10)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(mode_frame, text="Select Mode:").pack(anchor=tk.W)
        self.mode_combo = ttk.Combobox(mode_frame, state='readonly', width=15)
        self.mode_combo.pack(fill=tk.X, pady=5)
        self.mode_combo.bind('<<ComboboxSelected>>', self.on_mode_changed)
        
        mode_nav_frame = ttk.Frame(mode_frame)
        mode_nav_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(mode_nav_frame, text="⬅ Prev",
                  command=self.on_prev_mode).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(mode_nav_frame, text="Next ➡",
                  command=self.on_next_mode).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Face detection controls
        face_frame = ttk.LabelFrame(parent, text="👤 Face Detection", padding=10)
        face_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.landmarks_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(face_frame, text="Show Landmarks",
                       variable=self.landmarks_var,
                       command=self.on_landmarks_toggled).pack(anchor=tk.W)
        
        self.expression_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(face_frame, text="Show Expressions",
                       variable=self.expression_var,
                       command=self.on_expressions_toggled).pack(anchor=tk.W)
        
        self.bbox_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(face_frame, text="Show Face Box",
                       variable=self.bbox_var).pack(anchor=tk.W)
        
        # Screenshot and recording
        capture_frame = ttk.LabelFrame(parent, text="📸 Capture", padding=10)
        capture_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(capture_frame, text="📷 Screenshot",
                  command=self.on_screenshot).pack(fill=tk.X, pady=2)
        
        # Display information
        info_frame = ttk.LabelFrame(parent, text="ℹ️ Info", padding=10)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.fps_label = ttk.Label(info_frame, text="FPS: --")
        self.fps_label.pack(anchor=tk.W)
        
        self.face_label = ttk.Label(info_frame, text="Faces: 0")
        self.face_label.pack(anchor=tk.W)
        
        self.expr_label = ttk.Label(info_frame, text="Expression: --")
        self.expr_label.pack(anchor=tk.W)
        
        self.res_label = ttk.Label(info_frame, text="Resolution: --")
        self.res_label.pack(anchor=tk.W)
        
        # Settings
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="Flip Camera:").pack(anchor=tk.W)
        self.flip_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Mirror (Selfie)",
                       variable=self.flip_var).pack(anchor=tk.W)
        
        # Exit button
        ttk.Button(parent, text="❌ Exit",
                  command=self.on_exit).pack(fill=tk.X, padx=5, pady=10)
    
    def on_start_camera(self):
        """Start camera capture."""
        if self.app.start_camera():
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            # Update camera combo
            cameras = self.app.camera.get_available_cameras()
            self.camera_combo['values'] = [str(c) for c in cameras]
            if cameras:
                self.camera_combo.current(0)
            
            # Update mode combo
            modes = self.app.mode_manager.get_modes()
            self.mode_combo['values'] = modes
            if modes:
                self.app.mode_manager.set_mode(modes[0])
                self.mode_combo.current(0)
    
    def on_stop_camera(self):
        """Stop camera capture."""
        self.app.stop_camera()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def on_camera_changed(self, event):
        """Handle camera selection change."""
        camera_idx = int(self.camera_combo.get())
        self.app.camera.switch_camera(camera_idx)
    
    def on_mode_changed(self, event):
        """Handle meme mode change."""
        mode_name = self.mode_combo.get()
        self.app.mode_manager.set_mode(mode_name)
    
    def on_next_mode(self):
        """Switch to next meme mode."""
        mode_name = self.app.mode_manager.next_mode()
        mode_idx = self.mode_combo['values'].index(mode_name)
        self.mode_combo.current(mode_idx)
    
    def on_prev_mode(self):
        """Switch to previous meme mode."""
        mode_name = self.app.mode_manager.prev_mode()
        mode_idx = self.mode_combo['values'].index(mode_name)
        self.mode_combo.current(mode_idx)
    
    def on_landmarks_toggled(self):
        """Toggle landmarks display."""
        self.app.show_landmarks = self.landmarks_var.get()
    
    def on_expressions_toggled(self):
        """Toggle expressions display."""
        self.app.show_expressions = self.expression_var.get()
    
    def on_screenshot(self):
        """Take screenshot."""
        filename = self.app.take_screenshot()
        if filename:
            messagebox.showinfo("Screenshot Saved",
                              f"Screenshot saved to:\n{filename}")
    
    def on_exit(self):
        """Exit application."""
        self.running = False
        self.app.stop_camera()
        self.root.quit()
    
    def update_loop(self):
        """Update UI in real-time."""
        while self.running:
            if self.app.is_running:
                frame = self.app.get_processed_frame()
                if frame is not None:
                    self.display_frame(frame)
                    
                    # Update info labels
                    fps = self.app.camera.get_fps()
                    self.fps_label.config(text=f"FPS: {fps:.1f}")
                    
                    faces = self.app.current_faces
                    self.face_label.config(text=f"Faces: {len(faces)}")
                    
                    if self.app.current_expression:
                        expr = self.app.current_expression
                        self.expr_label.config(text=f"Expression: {expr}")
                    
                    res = self.app.camera.get_resolution()
                    if res:
                        self.res_label.config(text=f"Resolution: {res[0]}x{res[1]}")
            
            self.root.after(30)  # Update every 30ms
    
    def display_frame(self, frame):
        """Display frame in GUI."""
        # Flip if needed
        if self.flip_var.get():
            frame = cv2.flip(frame, 1)
        
        # Convert to RGB for PIL
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Scale to fit label
        label_width = self.video_label.winfo_width()
        label_height = self.video_label.winfo_height()
        
        if label_width > 1 and label_height > 1:
            rgb_frame = cv2.resize(rgb_frame, (label_width, label_height))
        
        # Convert to PIL Image
        image = Image.fromarray(rgb_frame)
        photo = ImageTk.PhotoImage(image)
        
        self.video_label.config(image=photo)
        self.video_label.image = photo
