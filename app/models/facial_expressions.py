import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random
import math

class FacialExpressionEngine:
    def __init__(self, config):
        self.config = config
        
        # Facial Action Coding System (FACS) units
        self.facs_units = {
            'inner_brow_raise': (0.0, 1.0),
            'outer_brow_raise': (0.0, 1.0),
            'brow_lower': (0.0, 1.0),
            'upper_lid_raise': (0.0, 1.0),
            'cheek_raise': (0.0, 1.0),
            'lid_tighten': (0.0, 1.0),
            'nose_wrinkle': (0.0, 1.0),
            'upper_lip_raise': (0.0, 1.0),
            'lip_corner_pull': (0.0, 1.0),
            'lip_stretch': (0.0, 1.0),
            'lip_corner_depress': (0.0, 1.0),
            'chin_raise': (0.0, 1.0),
            'mouth_open': (0.0, 1.0),
            'jaw_drop': (0.0, 1.0),
            'lip_pucker': (0.0, 1.0),
            'eye_blink': (0.0, 1.0)
        }
        
        # Emotion to FACS mapping
        self.emotion_facs = {
            'neutral': {
                'inner_brow_raise': 0.0, 'outer_brow_raise': 0.0, 'brow_lower': 0.0,
                'upper_lid_raise': 0.0, 'cheek_raise': 0.0, 'lid_tighten': 0.0,
                'lip_corner_pull': 0.0, 'mouth_open': 0.0, 'jaw_drop': 0.0
            },
            'happy': {
                'cheek_raise': 0.7, 'lip_corner_pull': 0.8, 'upper_lid_raise': 0.3,
                'inner_brow_raise': 0.2, 'mouth_open': 0.3
            },
            'sad': {
                'inner_brow_raise': 0.6, 'brow_lower': 0.3, 'lip_corner_depress': 0.7,
                'upper_lid_raise': 0.1, 'lip_stretch': 0.2
            },
            'angry': {
                'brow_lower': 0.8, 'lid_tighten': 0.7, 'lip_corner_depress': 0.6,
                'upper_lid_raise': 0.2, 'jaw_drop': 0.1
            },
            'surprised': {
                'inner_brow_raise': 0.9, 'outer_brow_raise': 0.9, 'upper_lid_raise': 0.9,
                'jaw_drop': 0.8, 'mouth_open': 0.9, 'lip_stretch': 0.3
            },
            'fear': {
                'inner_brow_raise': 0.7, 'outer_brow_raise': 0.6, 'brow_lower': 0.4,
                'upper_lid_raise': 0.8, 'lid_tighten': 0.5, 'jaw_drop': 0.3
            },
            'disgust': {
                'brow_lower': 0.5, 'nose_wrinkle': 0.8, 'upper_lip_raise': 0.7,
                'lip_corner_depress': 0.3, 'mouth_open': 0.2
            },
            'passionate': {
                'inner_brow_raise': 0.3, 'cheek_raise': 0.4, 'lip_corner_pull': 0.6,
                'upper_lid_raise': 0.4, 'mouth_open': 0.5, 'jaw_drop': 0.3
            },
            'singing': {
                'mouth_open': 0.8, 'jaw_drop': 0.7, 'lip_stretch': 0.5,
                'cheek_raise': 0.3, 'upper_lid_raise': 0.4
            },
            'belting': {
                'mouth_open': 0.9, 'jaw_drop': 0.9, 'lip_stretch': 0.7,
                'cheek_raise': 0.6, 'upper_lid_raise': 0.6, 'inner_brow_raise': 0.4
            },
            'emotional': {
                'inner_brow_raise': 0.7, 'brow_lower': 0.3, 'lip_corner_pull': 0.4,
                'lip_corner_depress': 0.3, 'cheek_raise': 0.3, 'mouth_open': 0.4
            }
        }
    
    def generate_expression_sequence(self, emotion_data, lip_sync_data, duration):
        """Generate facial expression sequence over time"""
        expression_sequence = []
        fps = self.config.FPS
        num_frames = int(duration * fps)
        
        # Get emotion progression
        emotion_progression = emotion_data.get('progression', [])
        
        for frame_idx in range(num_frames):
            time = frame_idx / fps
            
            # Find current emotion
            current_emotion = self._get_emotion_at_time(emotion_progression, time)
            emotion_intensity = self._get_intensity_at_time(emotion_progression, time)
            
            # Get FACS values for emotion
            facs_values = self._get_facs_for_emotion(current_emotion, emotion_intensity)
            
            # Add lip sync influence
            if lip_sync_data and frame_idx < len(lip_sync_data):
                lip_sync_values = lip_sync_data[frame_idx]
                facs_values = self._blend_lip_sync(facs_values, lip_sync_values)
            
            # Add eye blinking
            facs_values = self._add_blinking(facs_values, frame_idx, num_frames)
            
            # Add subtle micro-expressions for realism
            facs_values = self._add_micro_expressions(facs_values)
            
            expression_sequence.append({
                'frame': frame_idx,
                'time': time,
                'emotion': current_emotion,
                'intensity': emotion_intensity,
                'facs': facs_values
            })
        
        return expression_sequence
    
    def _get_emotion_at_time(self, progression, time):
        """Get emotion at specific time"""
        if not progression:
            return 'neutral'
        
        # Find closest time point
        closest = min(progression, key=lambda x: abs(x['time'] - time))
        return closest.get('emotion', 'neutral')
    
    def _get_intensity_at_time(self, progression, time):
        """Get emotion intensity at specific time"""
        if not progression:
            return 0.5
        
        closest = min(progression, key=lambda x: abs(x['time'] - time))
        return closest.get('intensity', 0.5)
    
    def _get_facs_for_emotion(self, emotion, intensity):
        """Get FACS values for an emotion with intensity scaling"""
        base_facs = self.emotion_facs.get(emotion, self.emotion_facs['neutral'])
        
        facs_values = {}
        for unit, value in base_facs.items():
            # Scale by intensity
            scaled_value = value * intensity
            
            # Add random natural variation
            variation = random.uniform(-0.03, 0.03)
            facs_values[unit] = max(0, min(1, scaled_value + variation))
        
        return facs_values
    
    def _blend_lip_sync(self, facs_values, lip_sync_values):
        """Blend emotion with lip sync"""
        # Lip sync affects mouth-related FACS units
        mouth_units = ['mouth_open', 'jaw_drop', 'lip_stretch', 'lip_corner_pull', 'lip_pucker']
        
        blended = facs_values.copy()
        for unit in mouth_units:
            if unit in lip_sync_values and unit in blended:
                # Blend with weight 0.7 for lip sync, 0.3 for emotion
                blended[unit] = lip_sync_values[unit] * 0.7 + facs_values[unit] * 0.3
        
        return blended
    
    def _add_blinking(self, facs_values, frame_idx, total_frames):
        """Add realistic eye blinking"""
        # Blink every 3-5 seconds (90-150 frames at 30fps)
        blink_interval = random.randint(90, 150)
        blink_duration = 3  # frames
        
        if frame_idx % blink_interval < blink_duration:
            # Blink
            blink_progress = (frame_idx % blink_interval) / blink_duration
            if blink_progress < 0.5:
                facs_values['eye_blink'] = blink_progress * 2
            else:
                facs_values['eye_blink'] = 2 - blink_progress * 2
        else:
            facs_values['eye_blink'] = 0
        
        return facs_values
    
    def _add_micro_expressions(self, facs_values):
        """Add subtle micro-expressions for realism"""
        # Random micro-expressions
        if random.random() < 0.1:  # 10% chance per frame
            micro_unit = random.choice(list(facs_values.keys()))
            micro_intensity = random.uniform(0.05, 0.15)
            facs_values[micro_unit] = min(1, facs_values[micro_unit] + micro_intensity)
        
        return facs_values
    
    def render_facial_expression(self, face_image, expression_data):
        """Render facial expression on face image"""
        # Create a copy of the face
        img = face_image.copy()
        draw = ImageDraw.Draw(img)
        
        # Get FACS values
        facs = expression_data['facs']
        
        # Apply facial deformations based on FACS units
        img = self._apply_facs_deformations(img, draw, facs)
        
        # Add emotion-specific effects
        emotion = expression_data['emotion']
        img = self._add_emotion_effects(img, emotion, expression_data['intensity'])
        
        return img
    
    def _apply_facs_deformations(self, img, draw, facs):
        """Apply FACS-based deformations to face"""
        width, height = img.size
        center_x, center_y = width // 2, height // 2
        
        # Mouth changes
        mouth_open = facs.get('mouth_open', 0)
        if mouth_open > 0.1:
            # Open mouth
            mouth_height = 10 + 30 * mouth_open
            draw.ellipse([center_x - 25, center_y + 35, center_x + 25, center_y + 35 + mouth_height],
                        fill=(50, 20, 20))
        
        # Jaw drop
        jaw_drop = facs.get('jaw_drop', 0)
        if jaw_drop > 0.1:
            # Lower jaw
            jaw_amount = 10 * jaw_drop
            draw.ellipse([center_x - 30, center_y + 50 + jaw_amount,
                         center_x + 30, center_y + 80 + jaw_amount],
                        fill=(200, 180, 160))
        
        # Cheek raise (smile)
        cheek_raise = facs.get('cheek_raise', 0)
        if cheek_raise > 0.1:
            # Raise cheeks
            raise_amount = 10 * cheek_raise
            draw.ellipse([center_x - 50, center_y - 10 - raise_amount,
                         center_x - 20, center_y + 20 - raise_amount],
                        fill=(230, 200, 180, 50))
            draw.ellipse([center_x + 20, center_y - 10 - raise_amount,
                         center_x + 50, center_y + 20 - raise_amount],
                        fill=(230, 200, 180, 50))
        
        # Eyebrow movements
        brow_raise = facs.get('inner_brow_raise', 0)
        brow_lower = facs.get('brow_lower', 0)
        
        if brow_raise > 0.1:
            # Raise inner eyebrows
            raise_amount = 15 * brow_raise
            draw.arc([center_x - 40, center_y - 60 - raise_amount,
                     center_x + 40, center_y - 30 - raise_amount],
                    0, 180, fill=(40, 30, 20), width=4)
        
        if brow_lower > 0.1:
            # Lower eyebrows
            lower_amount = 10 * brow_lower
            draw.arc([center_x - 40, center_y - 40 - lower_amount,
                     center_x + 40, center_y - 10 - lower_amount],
                    180, 360, fill=(40, 30, 20), width=4)
        
        return img
    
    def _add_emotion_effects(self, img, emotion, intensity):
        """Add emotion-specific visual effects"""
        if emotion == 'happy':
            # Add sparkle to eyes
            draw = ImageDraw.Draw(img)
            draw.ellipse([center_x - 35, center_y - 20, center_x - 25, center_y - 10],
                        fill=(255, 255, 255, 100))
            draw.ellipse([center_x + 25, center_y - 20, center_x + 35, center_y - 10],
                        fill=(255, 255, 255, 100))
        
        elif emotion == 'sad':
            # Add tear effect
            draw = ImageDraw.Draw(img)
            draw.ellipse([center_x - 30, center_y + 10, center_x - 20, center_y + 25],
                        fill=(200, 220, 255, 80))
        
        elif emotion == 'angry':
            # Add vein effect
            draw = ImageDraw.Draw(img)
            draw.line([center_x - 20, center_y - 50, center_x - 15, center_y - 30],
                     fill=(200, 50, 50, 50), width=2)
        
        return img
    
    def get_mouth_shape_for_phoneme(self, phoneme):
        """Get mouth shape for specific phoneme"""
        mouth_shapes = {
            'AA': {'mouth_open': 0.8, 'jaw_drop': 0.7, 'lip_stretch': 0.3},
            'AE': {'mouth_open': 0.7, 'jaw_drop': 0.6, 'lip_stretch': 0.5},
            'AH': {'mouth_open': 0.6, 'jaw_drop': 0.5, 'lip_stretch': 0.4},
            'AO': {'mouth_open': 0.5, 'jaw_drop': 0.4, 'lip_pucker': 0.6},
            'AW': {'mouth_open': 0.7, 'jaw_drop': 0.6, 'lip_pucker': 0.4},
            'AY': {'mouth_open': 0.6, 'jaw_drop': 0.5, 'lip_stretch': 0.6},
            'B': {'mouth_open': 0.1, 'jaw_drop': 0.1, 'lip_pucker': 0.8},
            'CH': {'mouth_open': 0.3, 'jaw_drop': 0.2, 'lip_pucker': 0.7},
            'D': {'mouth_open': 0.2, 'jaw_drop': 0.2, 'lip_pucker': 0.6},
            'EH': {'mouth_open': 0.6, 'jaw_drop': 0.5, 'lip_stretch': 0.4},
            'ER': {'mouth_open': 0.4, 'jaw_drop': 0.3, 'lip_pucker': 0.6},
            'EY': {'mouth_open': 0.5, 'jaw_drop': 0.4, 'lip_stretch': 0.7},
            'F': {'mouth_open': 0.2, 'jaw_drop': 0.2, 'lip_pucker': 0.1},
            'G': {'mouth_open': 0.2, 'jaw_drop': 0.2, 'lip_pucker': 0.5},
            'HH': {'mouth_open': 0.5, 'jaw_drop': 0.4, 'lip_stretch': 0.3},
            'IH': {'mouth_open': 0.5, 'jaw_drop': 0.4, 'lip_stretch': 0.3},
            'IY': {'mouth_open': 0.4, 'jaw_drop': 0.3, 'lip_stretch': 0.5},
            'JH': {'mouth_open': 0.3, 'jaw_drop': 0.2, 'lip_pucker': 0.6},
            'K': {'mouth_open': 0.1, 'jaw_drop': 0.1, 'lip_pucker': 0.4},
            'L': {'mouth_open': 0.3, 'jaw_drop': 0.2, 'lip_stretch': 0.5},
            'M': {'mouth_open': 0.1, 'jaw_drop': 0.1, 'lip_pucker': 0.8},
            'N': {'mouth_open': 0.1, 'jaw_drop': 0.1, 'lip_pucker': 0.7},
            'NG': {'mouth_open': 0.2, 'jaw_drop': 0.2, 'lip_stretch': 0.4},
            'OW': {'mouth_open': 0.6, 'jaw_drop': 0.5, 'lip_pucker': 0.5},
            'OY': {'mouth_open': 0.5, 'jaw_drop': 0.4, 'lip_pucker': 0.7},
            'P': {'mouth_open': 0.1, 'jaw_drop': 0.1, 'lip_pucker': 0.8},
            'R': {'mouth_open': 0.3, 'jaw_drop': 0.2, 'lip_pucker': 0.6},
            'S': {'mouth_open': 0.2, 'jaw_drop': 0.1, 'lip_stretch': 0.4},
            'SH': {'mouth_open': 0.3, 'jaw_drop': 0.2, 'lip_pucker': 0.5},
            'T': {'mouth_open': 0.1, 'jaw_drop': 0.1, 'lip_pucker': 0.6},
            'TH': {'mouth_open': 0.2, 'jaw_drop': 0.1, 'lip_stretch': 0.3},
            'UH': {'mouth_open': 0.4, 'jaw_drop': 0.3, 'lip_pucker': 0.6},
            'UW': {'mouth_open': 0.3, 'jaw_drop': 0.2, 'lip_pucker': 0.8},
            'V': {'mouth_open': 0.2, 'jaw_drop': 0.2, 'lip_pucker': 0.2},
            'W': {'mouth_open': 0.3, 'jaw_drop': 0.2, 'lip_pucker': 0.7},
            'Y': {'mouth_open': 0.3, 'jaw_drop': 0.2, 'lip_stretch': 0.5},
            'Z': {'mouth_open': 0.2, 'jaw_drop': 0.1, 'lip_stretch': 0.4},
            'ZH': {'mouth_open': 0.3, 'jaw_drop': 0.2, 'lip_pucker': 0.4},
            'sil': {'mouth_open': 0.0, 'jaw_drop': 0.0, 'lip_pucker': 0.0}
        }
        
        return mouth_shapes.get(phoneme, mouth_shapes['sil'])
