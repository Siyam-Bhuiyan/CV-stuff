"""
Meme modes with funny visual effects and overlays.
Implements: Gigachad, Troll, Sleep Detector, NPC, Big Mouth, Laser Eyes, etc.
"""

import cv2
import numpy as np
import random
from .utils import (
    Colors, draw_text, draw_circle, draw_line, draw_polygon,
    sharpen_region, add_glow, create_laser_effect, create_meme_text,
    blur_region, warp_face_region, screenshot_frame
)
from .face_detector import FaceLandmarkIndices


class MemeMode:
    """Base class for meme modes."""
    
    def __init__(self, name):
        """Initialize meme mode."""
        self.name = name
        self.active = False
    
    def apply(self, frame, faces, face_detector, expressions):
        """Apply meme effect to frame."""
        raise NotImplementedError


class GigachadMode(MemeMode):
    """Gigachad mode: Sharp jaw, intense contrast, glowing eyes."""
    
    def __init__(self):
        """Initialize Gigachad mode."""
        super().__init__("Gigachad")
        self.glow_intensity = 0
    
    def apply(self, frame, faces, face_detector, expressions):
        """Apply gigachad effect."""
        if not faces:
            return frame
        
        face = faces[0]
        landmarks = face['landmarks_normalized']
        
        # Get face region
        bbox = face_detector.get_face_bbox(landmarks, frame.shape)
        if not bbox:
            return frame
        
        x, y, w, h = bbox
        
        # Increase contrast
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        l_channel = cv2.convertScaleAbs(l_channel, alpha=1.3, beta=30)
        lab[:, :, 0] = cv2.clip(l_channel, 0, 255)
        frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Sharpen jawline
        jaw_points = face_detector.get_jawline(landmarks)
        if jaw_points:
            sharpen_region(frame, x, y, w, h)
        
        # Get eyes and add glow
        left_eye_points = face_detector.get_eye_region(landmarks, 'left')
        right_eye_points = face_detector.get_eye_region(landmarks, 'right')
        
        if left_eye_points:
            eye_x = int(left_eye_points[0][0])
            eye_y = int(left_eye_points[0][1])
            add_glow(frame, (eye_x, eye_y), 30, Colors.CYAN, intensity=0.5)
        
        if right_eye_points:
            eye_x = int(right_eye_points[0][0])
            eye_y = int(right_eye_points[0][1])
            add_glow(frame, (eye_x, eye_y), 30, Colors.CYAN, intensity=0.5)
        
        # Add dramatic text
        draw_text(frame, "GIGACHAD MODE", (20, 50), font_scale=1.5,
                 color=Colors.CYAN, bg_color=Colors.BLACK, thickness=3)
        
        return frame


class TrollMode(MemeMode):
    """Troll mode: Face warping, trollface overlay, random captions."""
    
    def __init__(self):
        """Initialize Troll mode."""
        super().__init__("Troll")
        self.captions = [
            "U MAD BRO?",
            "PROBLEM?",
            "TROLLING 100",
            "EPIC TROLL",
            "PWNED",
            "JEBAIT"
        ]
        self.caption_timer = 0
        self.current_caption = ""
    
    def apply(self, frame, faces, face_detector, expressions):
        """Apply troll effect."""
        if not faces:
            return frame
        
        face = faces[0]
        landmarks = face['landmarks_normalized']
        
        # Get face region
        bbox = face_detector.get_face_bbox(landmarks, frame.shape)
        if not bbox:
            return frame
        
        x, y, w, h = bbox
        
        # Slight face warp
        left_eye = face_detector.get_eye_region(landmarks, 'left')
        right_eye = face_detector.get_eye_region(landmarks, 'right')
        
        if left_eye and right_eye:
            # Distort slightly
            cv2.GaussianBlur(frame, (5, 5), 0)
            
            # Make it pixelated for comic effect
            small = cv2.resize(frame[y:y+h, x:x+w], (w//3, h//3))
            frame[y:y+h, x:x+w] = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        
        # Update caption
        self.caption_timer += 1
        if self.caption_timer > 60:
            self.current_caption = random.choice(self.captions)
            self.caption_timer = 0
        
        if self.current_caption:
            caption_img = create_meme_text(self.current_caption, width=frame.shape[1])
            frame[0:caption_img.shape[0], 0:frame.shape[1]] = caption_img
        
        return frame


class SleepDetectorMode(MemeMode):
    """Sleep detector: Warning when eyes are closed, alarm sound."""
    
    def __init__(self):
        """Initialize Sleep Detector mode."""
        super().__init__("Sleep Detector")
        self.alert_triggered = False
        self.alert_frames = 0
    
    def apply(self, frame, faces, face_detector, expressions):
        """Apply sleep detector effect."""
        if not faces:
            return frame
        
        face = faces[0]
        landmarks = face['landmarks_normalized']
        
        # Get expression data
        expr = expressions.get('sleepy', {})
        is_sleepy = expr.get('is_sleepy', False)
        sleepy_level = expr.get('sleepy_level', 0)
        
        if is_sleepy:
            self.alert_frames += 1
            
            # Blink effect - darken frame
            darkness = int(255 * sleepy_level)
            overlay = np.zeros_like(frame)
            overlay[:, :] = (0, 0, darkness)
            cv2.addWeighted(frame, 0.7, overlay, 0.3, 0, frame)
            
            # Warning text
            draw_text(frame, "GO TO SLEEP BRO", (20, 50), font_scale=2.0,
                     color=Colors.RED, bg_color=Colors.BLACK, thickness=4)
            
            # Flashing border
            if self.alert_frames % 10 < 5:
                cv2.rectangle(frame, (0, 0), (frame.shape[1]-1, frame.shape[0]-1),
                             Colors.RED, 5)
        else:
            self.alert_frames = 0
        
        # Show sleepiness level
        bar_width = int(300 * sleepy_level)
        cv2.rectangle(frame, (20, frame.shape[0]-40), (20+bar_width, frame.shape[0]-10),
                     Colors.RED, -1)
        cv2.rectangle(frame, (20, frame.shape[0]-40), (320, frame.shape[0]-10),
                     Colors.WHITE, 2)
        draw_text(frame, "Sleepiness", (330, frame.shape[0]-15), font_scale=0.7,
                 color=Colors.WHITE)
        
        return frame


class NPCMode(MemeMode):
    """NPC mode: Display random NPC-style labels and dialogue."""
    
    def __init__(self):
        """Initialize NPC mode."""
        super().__init__("NPC")
        self.labels = [
            "[Side Quest Giver]",
            "[Low IQ Detected]",
            "[Main Character Energy: 2%]",
            "[NPC #47382]",
            "[Press F to pay respects]",
            "[Dialogue locked]",
            "[Cringe level: 99%]",
            "[Sigma male]",
            "[Simp detected]",
            "[No maidens?]",
            "[Touch grass]",
            "[Ratio'd]"
        ]
        self.dialogue = [
            "Huh?",
            "...",
            "k",
            "based",
            "ratio",
            "bet",
            "fr fr"
        ]
        self.label_timer = 0
        self.current_label = ""
        self.current_dialogue = ""
    
    def apply(self, frame, faces, face_detector, expressions):
        """Apply NPC effect."""
        if not faces:
            return frame
        
        face = faces[0]
        landmarks = face['landmarks_normalized']
        
        # Get face region
        bbox = face_detector.get_face_bbox(landmarks, frame.shape)
        if not bbox:
            return frame
        
        x, y, w, h = bbox
        
        # Update labels periodically
        self.label_timer += 1
        if self.label_timer > 120:
            self.current_label = random.choice(self.labels)
            self.current_dialogue = random.choice(self.dialogue)
            self.label_timer = 0
        
        # Draw NPC label above head
        if self.current_label:
            draw_text(frame, self.current_label, (x, y-30), font_scale=1.0,
                     color=Colors.YELLOW, bg_color=Colors.BLACK, thickness=2)
        
        # Draw dialogue bubble near mouth
        if self.current_dialogue:
            dialogue_img = create_meme_text(self.current_dialogue, width=200, font_size=50)
            frame[y+h//2:y+h//2+dialogue_img.shape[0],
                  x+w//2:x+w//2+dialogue_img.shape[1]] = dialogue_img
        
        # HP bar above head
        hp_width = 100
        cv2.rectangle(frame, (x, y-50), (x+hp_width, y-40), Colors.RED, -1)
        cv2.rectangle(frame, (x, y-50), (x+hp_width, y-40), Colors.WHITE, 2)
        draw_text(frame, "HP: 1/100", (x+hp_width+10, y-40), font_scale=0.7,
                 color=Colors.RED)
        
        return frame


class BigMouthMode(MemeMode):
    """Big Mouth mode: Exaggerate and enlarge mouth region."""
    
    def __init__(self):
        """Initialize Big Mouth mode."""
        super().__init__("Big Mouth")
    
    def apply(self, frame, faces, face_detector, expressions):
        """Apply big mouth effect."""
        if not faces:
            return frame
        
        face = faces[0]
        landmarks = face['landmarks_normalized']
        
        # Get mouth region
        mouth_outer, mouth_inner = face_detector.get_mouth_region(landmarks)
        
        if mouth_outer and len(mouth_outer) > 0:
            # Get bounding box of mouth
            mouth_points = mouth_outer
            mouth_x = [int(p[0]) for p in mouth_points]
            mouth_y = [int(p[1]) for p in mouth_points]
            
            mx_min, mx_max = min(mouth_x), max(mouth_x)
            my_min, my_max = min(mouth_y), max(mouth_y)
            
            mouth_w = mx_max - mx_min
            mouth_h = my_max - my_min
            
            # Expand mouth region
            expansion = 1.5
            new_x = int(mx_min - mouth_w * (expansion - 1) / 2)
            new_y = int(my_min - mouth_h * (expansion - 1) / 2)
            new_w = int(mouth_w * expansion)
            new_h = int(mouth_h * expansion)
            
            # Ensure within bounds
            new_x = max(0, new_x)
            new_y = max(0, new_y)
            new_w = min(frame.shape[1] - new_x, new_w)
            new_h = min(frame.shape[0] - new_y, new_h)
            
            # Extract and enlarge mouth
            if new_w > 0 and new_h > 0:
                mouth_region = frame[my_min:my_max, mx_min:mx_max].copy()
                enlarged = cv2.resize(mouth_region, (new_w, new_h))
                
                # Place enlarged mouth back
                frame[new_y:new_y+new_h, new_x:new_x+new_w] = enlarged
                
                # Draw border around mouth
                cv2.rectangle(frame, (mx_min, my_min), (mx_max, my_max),
                             Colors.RED, 3)
            
            draw_text(frame, "BIG MOUTH", (20, 50), font_scale=1.5,
                     color=Colors.RED, thickness=2)
        
        return frame


class LaserEyesMode(MemeMode):
    """Laser Eyes mode: Animated laser beams from eyes."""
    
    def __init__(self):
        """Initialize Laser Eyes mode."""
        super().__init__("Laser Eyes")
        self.animation_frame = 0
    
    def apply(self, frame, faces, face_detector, expressions):
        """Apply laser eyes effect."""
        if not faces:
            return frame
        
        face = faces[0]
        landmarks = face['landmarks_normalized']
        
        # Get eye positions
        left_eye = face_detector.get_eye_region(landmarks, 'left')
        right_eye = face_detector.get_eye_region(landmarks, 'right')
        
        self.animation_frame += 1
        
        if left_eye and len(left_eye) > 0:
            # Left eye center
            eye_x = int(left_eye[0][0])
            eye_y = int(left_eye[0][1])
            
            # Laser target direction (slightly downward and outward)
            target_x = int(eye_x - 300 - (self.animation_frame % 50) * 5)
            target_y = int(eye_y + 150)
            
            create_laser_effect(frame, (eye_x, eye_y), (target_x, target_y), length=400)
            
            # Eye glow
            cv2.circle(frame, (eye_x, eye_y), 15, Colors.CYAN, -1)
            cv2.circle(frame, (eye_x, eye_y), 20, Colors.YELLOW, 2)
        
        if right_eye and len(right_eye) > 0:
            # Right eye center
            eye_x = int(right_eye[0][0])
            eye_y = int(right_eye[0][1])
            
            # Laser target direction
            target_x = int(eye_x + 300 + (self.animation_frame % 50) * 5)
            target_y = int(eye_y + 150)
            
            create_laser_effect(frame, (eye_x, eye_y), (target_x, target_y), length=400)
            
            # Eye glow
            cv2.circle(frame, (eye_x, eye_y), 15, Colors.CYAN, -1)
            cv2.circle(frame, (eye_x, eye_y), 20, Colors.YELLOW, 2)
        
        draw_text(frame, "LASER EYES ACTIVATED", (20, 50), font_scale=1.5,
                 color=Colors.YELLOW, bg_color=Colors.BLACK, thickness=2)
        
        return frame


class MirrrorMode(MemeMode):
    """Mirror mode: Create symmetrical mirror effect."""
    
    def __init__(self):
        """Initialize Mirror mode."""
        super().__init__("Mirror")
    
    def apply(self, frame, faces, face_detector, expressions):
        """Apply mirror effect."""
        h, w = frame.shape[:2]
        
        # Get left half
        left_half = frame[:, :w//2].copy()
        
        # Mirror it to right
        right_half = cv2.flip(left_half, 1)
        frame[:, w//2:] = right_half
        
        draw_text(frame, "MIRROR EFFECT", (20, 50), font_scale=1.5,
                 color=Colors.MAGENTA, thickness=2)
        
        return frame


class VinylMode(MemeMode):
    """Vinyl/Retro mode: VHS effect with noise and scanlines."""
    
    def __init__(self):
        """Initialize Vinyl mode."""
        super().__init__("Vinyl")
        self.frame_counter = 0
    
    def apply(self, frame, faces, face_detector, expressions):
        """Apply VHS/retro effect."""
        # Add noise
        noise = np.random.randint(0, 50, frame.shape, dtype=np.uint8)
        frame = cv2.add(frame, noise)
        
        # Add scanlines
        for i in range(0, frame.shape[0], 4):
            frame[i:i+1, :] = cv2.addWeighted(frame[i:i+1, :], 0.5,
                                             np.zeros_like(frame[i:i+1, :]), 0.5, 0)
        
        # Add color shift
        self.frame_counter += 1
        if self.frame_counter % 2 == 0:
            frame[:, :, 2] = np.clip(frame[:, :, 2] + 20, 0, 255)  # More red
        
        # Add glitch
        if self.frame_counter % 30 == 0:
            glitch_h = np.random.randint(20, 100)
            glitch_y = np.random.randint(0, frame.shape[0] - glitch_h)
            frame[glitch_y:glitch_y+glitch_h, :] = cv2.flip(
                frame[glitch_y:glitch_y+glitch_h, :], 1)
        
        draw_text(frame, "REC", (20, 50), font_scale=1.5,
                 color=Colors.RED, bg_color=Colors.BLACK, thickness=2)
        
        return frame


class InvertMode(MemeMode):
    """Invert mode: Negative image effect."""
    
    def __init__(self):
        """Initialize Invert mode."""
        super().__init__("Invert")
    
    def apply(self, frame, faces, face_detector, expressions):
        """Apply inversion effect."""
        frame = cv2.bitwise_not(frame)
        
        draw_text(frame, "INVERTED", (20, 50), font_scale=1.5,
                 color=Colors.WHITE, bg_color=Colors.BLACK, thickness=2)
        
        return frame


class ModeManager:
    """Manages all available meme modes."""
    
    def __init__(self):
        """Initialize mode manager."""
        self.modes = {
            'gigachad': GigachadMode(),
            'troll': TrollMode(),
            'sleep': SleepDetectorMode(),
            'npc': NPCMode(),
            'bigmouth': BigMouthMode(),
            'laser': LaserEyesMode(),
            'mirror': MirrrorMode(),
            'vinyl': VinylMode(),
            'invert': InvertMode()
        }
        self.current_mode = None
        self.mode_names = list(self.modes.keys())
    
    def get_modes(self):
        """Get list of available modes."""
        return self.mode_names
    
    def set_mode(self, mode_name):
        """Set active mode."""
        if mode_name in self.modes:
            self.current_mode = self.modes[mode_name]
            return True
        return False
    
    def apply_mode(self, frame, faces, face_detector, expressions):
        """Apply current mode to frame."""
        if self.current_mode:
            return self.current_mode.apply(frame, faces, face_detector, expressions)
        return frame
    
    def next_mode(self):
        """Switch to next mode."""
        current_idx = self.mode_names.index(self.current_mode.name.lower()) if self.current_mode else -1
        next_idx = (current_idx + 1) % len(self.mode_names)
        mode_name = self.mode_names[next_idx]
        self.set_mode(mode_name)
        return mode_name
    
    def prev_mode(self):
        """Switch to previous mode."""
        current_idx = self.mode_names.index(self.current_mode.name.lower()) if self.current_mode else 0
        prev_idx = (current_idx - 1) % len(self.mode_names)
        mode_name = self.mode_names[prev_idx]
        self.set_mode(mode_name)
        return mode_name
