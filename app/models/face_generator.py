import torch
import torch.nn as nn
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import cv2
import random
import os

class FaceGenerator:
    def __init__(self, config):
        self.config = config
        self.device = torch.device('cuda' if config.USE_GPU and torch.cuda.is_available() else 'cpu')
        self.model = None
        self._load_model()
        
        # Face features database
        self.face_features = {
            'male': {
                'jawline': ['square', 'round', 'oval', 'heart'],
                'nose': ['straight', 'aquiline', 'snub', 'roman'],
                'eyes': ['deep_set', 'hooded', 'almond', 'round'],
                'eyebrows': ['bushy', 'arched', 'straight', 'thin'],
                'lips': ['full', 'thin', 'medium', 'wide'],
                'cheekbones': ['high', 'low', 'prominent', 'flat']
            },
            'female': {
                'jawline': ['oval', 'heart', 'round', 'square'],
                'nose': ['straight', 'turned_up', 'snub', 'aquiline'],
                'eyes': ['almond', 'round', 'hooded', 'deep_set'],
                'eyebrows': ['arched', 'thin', 'straight', 'bushy'],
                'lips': ['full', 'medium', 'thin', 'wide'],
                'cheekbones': ['high', 'prominent', 'low', 'flat']
            }
        }
        
        # Facial expression mapping
        self.expressions = {
            'neutral': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'happy': [0.8, 0.0, 0.0, 0.5, 0.0, 0.0],
            'sad': [-0.3, 0.0, 0.5, 0.0, 0.0, 0.0],
            'angry': [-0.5, 0.5, 0.0, 0.0, 0.0, 0.0],
            'surprised': [0.0, 0.8, 0.0, 0.0, 0.0, 0.0],
            'singing': [0.5, 0.3, 0.0, 0.7, 0.0, 0.0],
            'passionate': [0.7, 0.0, 0.0, 0.8, 0.0, 0.0],
            'emotional': [0.6, 0.2, 0.3, 0.5, 0.0, 0.0]
        }
    
    def _load_model(self):
        """Load StyleGAN2 model for face generation"""
        try:
            # In production, load actual StyleGAN2 weights
            model_path = self.config.FACE_GENERATION_MODEL
            if os.path.exists(model_path):
                self.model = torch.load(model_path, map_location=self.device)
            else:
                print(f"Warning: Face generation model not found at {model_path}")
                print("Using fallback face generation")
        except Exception as e:
            print(f"Error loading face generation model: {str(e)}")
            self.model = None
    
    def generate_face(self, gender='male', age=30, expression='neutral', 
                     hairstyle='medium', ethnicity='caucasian'):
        """Generate a realistic face with specified features"""
        # Generate face based on parameters
        face = self._generate_base_face(gender, age, ethnicity)
        
        # Add features
        face = self._add_facial_features(face, gender)
        
        # Apply expression
        face = self._apply_expression(face, expression)
        
        # Add hair
        face = self._add_hair(face, hairstyle, gender)
        
        # Add skin texture
        face = self._add_skin_texture(face)
        
        # Apply enhancements
        face = self._enhance_face(face)
        
        return face
    
    def _generate_base_face(self, gender, age, ethnicity):
        """Generate base face shape"""
        size = (512, 512)
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Face proportions based on gender
        if gender == 'male':
            face_width = 180
            face_height = 220
            jaw_width = 150
        else:
            face_width = 160
            face_height = 200
            jaw_width = 130
        
        # Center position
        cx, cy = size[0] // 2, size[1] // 2
        
        # Draw face shape (oval with variations)
        points = []
        for angle in range(0, 360, 5):
            rad = np.radians(angle)
            if angle < 60 or angle > 300:  # Jaw area
                radius = face_width // 2
            elif 60 <= angle <= 120:  # Top of head
                radius = face_width // 2 * 0.8
            elif 240 <= angle <= 300:  # Chin
                radius = jaw_width // 2 * 0.7
            else:  # Cheeks
                radius = face_width // 2 * 1.1
            
            x = cx + int(radius * np.cos(rad))
            y = cy + int(face_height // 2 * np.sin(rad))
            points.append((x, y))
        
        # Draw face
        draw.polygon(points, fill=self._get_skin_color(ethnicity))
        
        return img
    
    def _get_skin_color(self, ethnicity):
        """Get skin color based on ethnicity"""
        colors = {
            'caucasian': (255, 220, 190),
            'african': (180, 130, 90),
            'asian': (240, 210, 170),
            'hispanic': (220, 170, 130),
            'middle_eastern': (230, 190, 150)
        }
        return colors.get(ethnicity, (255, 220, 190))
    
    def _add_facial_features(self, face, gender):
        """Add detailed facial features"""
        img = face.copy()
        draw = ImageDraw.Draw(img)
        size = img.size
        cx, cy = size[0] // 2, size[1] // 2
        
        # Select features based on gender
        features = self.face_features.get(gender, self.face_features['male'])
        
        # Eyes
        eye_y = cy - 30
        eye_spacing = 50
        for x_offset in [-eye_spacing, eye_spacing]:
            self._draw_eye(draw, cx + x_offset, eye_y, features['eyes'][0])
        
        # Eyebrows
        brow_y = cy - 45
        for x_offset in [-eye_spacing - 5, eye_spacing + 5]:
            self._draw_eyebrow(draw, cx + x_offset, brow_y, features['eyebrows'][0])
        
        # Nose
        nose_y = cy + 10
        self._draw_nose(draw, cx, nose_y, features['nose'][0])
        
        # Mouth
        mouth_y = cy + 40
        self._draw_mouth(draw, cx, mouth_y, features['lips'][0])
        
        # Cheekbones
        cheek_y = cy + 15
        self._draw_cheekbones(draw, cx, cheek_y, features['cheekbones'][0])
        
        # Jawline
        self._draw_jawline(draw, cx, cy, features['jawline'][0])
        
        return img
    
    def _draw_eye(self, draw, x, y, eye_type):
        """Draw realistic eye"""
        # Eye shape based on type
        if eye_type == 'almond':
            points = [
                (x - 20, y - 5),
                (x - 15, y - 10),
                (x, y - 12),
                (x + 15, y - 10),
                (x + 20, y - 5),
                (x + 15, y),
                (x, y + 2),
                (x - 15, y)
            ]
            draw.polygon(points, fill=(255, 255, 255))
            # Iris
            draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(60, 80, 120))
            # Pupil
            draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(0, 0, 0))
            # Highlight
            draw.ellipse([x - 2, y - 4, x + 4, y + 2], fill=(255, 255, 255, 128))
        
        elif eye_type == 'round':
            draw.ellipse([x - 18, y - 12, x + 18, y + 8], fill=(255, 255, 255))
            draw.ellipse([x - 9, y - 6, x + 9, y + 6], fill=(60, 80, 120))
            draw.ellipse([x - 4, y - 3, x + 4, y + 3], fill=(0, 0, 0))
        
        elif eye_type == 'hooded':
            draw.ellipse([x - 18, y - 8, x + 18, y + 8], fill=(255, 255, 255))
            # Hooded eyelid
            draw.arc([x - 22, y - 14, x + 22, y + 6], 0, 180, fill=(200, 180, 160), width=3)
            draw.ellipse([x - 7, y - 5, x + 7, y + 5], fill=(60, 80, 120))
            draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(0, 0, 0))
        
        else:  # deep_set
            draw.ellipse([x - 18, y - 8, x + 18, y + 8], fill=(200, 180, 160))
            draw.ellipse([x - 15, y - 6, x + 15, y + 6], fill=(255, 255, 255))
            draw.ellipse([x - 6, y - 5, x + 6, y + 5], fill=(60, 80, 120))
            draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(0, 0, 0))
    
    def _draw_eyebrow(self, draw, x, y, brow_type):
        """Draw realistic eyebrow"""
        if brow_type == 'bushy':
            draw.arc([x - 25, y - 10, x + 25, y + 10], 0, 180, fill=(40, 30, 20), width=6)
        elif brow_type == 'arched':
            draw.arc([x - 20, y - 15, x + 20, y + 5], 10, 170, fill=(40, 30, 20), width=4)
        elif brow_type == 'straight':
            draw.line([x - 22, y - 2, x + 22, y - 2], fill=(40, 30, 20), width=4)
        else:  # thin
            draw.arc([x - 25, y - 5, x + 25, y + 5], 5, 175, fill=(40, 30, 20), width=2)
    
    def _draw_nose(self, draw, x, y, nose_type):
        """Draw realistic nose"""
        if nose_type == 'straight':
            draw.line([x, y - 15, x, y + 25], fill=(200, 170, 150), width=3)
            draw.ellipse([x - 8, y + 20, x + 8, y + 30], fill=(200, 170, 150))
        elif nose_type == 'aquiline':
            draw.line([x - 2, y - 15, x + 3, y + 10], fill=(200, 170, 150), width=3)
            draw.line([x + 3, y + 10, x - 2, y + 25], fill=(200, 170, 150), width=3)
            draw.ellipse([x - 8, y + 20, x + 8, y + 30], fill=(200, 170, 150))
        elif nose_type == 'snub':
            draw.line([x, y - 15, x, y + 15], fill=(200, 170, 150), width=3)
            draw.ellipse([x - 10, y + 12, x + 10, y + 25], fill=(200, 170, 150))
        else:  # roman
            draw.line([x - 3, y - 15, x, y + 10], fill=(200, 170, 150), width=3)
            draw.line([x, y + 10, x + 3, y + 25], fill=(200, 170, 150), width=3)
            draw.ellipse([x - 8, y + 20, x + 8, y + 30], fill=(200, 170, 150))
    
    def _draw_mouth(self, draw, x, y, lip_type):
        """Draw realistic mouth"""
        if lip_type == 'full':
            draw.ellipse([x - 25, y - 8, x + 25, y + 8], fill=(200, 100, 100))
            draw.ellipse([x - 20, y - 3, x + 20, y + 3], fill=(180, 80, 80))
        elif lip_type == 'thin':
            draw.ellipse([x - 22, y - 4, x + 22, y + 4], fill=(200, 100, 100))
            draw.line([x - 18, y, x + 18, y], fill=(180, 80, 80), width=1)
        elif lip_type == 'medium':
            draw.ellipse([x - 24, y - 6, x + 24, y + 6], fill=(200, 100, 100))
            draw.ellipse([x - 18, y - 2, x + 18, y + 2], fill=(180, 80, 80))
        else:  # wide
            draw.ellipse([x - 30, y - 6, x + 30, y + 6], fill=(200, 100, 100))
            draw.ellipse([x - 22, y - 2, x + 22, y + 2], fill=(180, 80, 80))
    
    def _draw_cheekbones(self, draw, x, y, cheek_type):
        """Add cheekbone definition"""
        if cheek_type == 'high':
            draw.ellipse([x - 50, y - 10, x - 20, y + 20], fill=(200, 180, 170, 50))
            draw.ellipse([x + 20, y - 10, x + 50, y + 20], fill=(200, 180, 170, 50))
        elif cheek_type == 'prominent':
            draw.ellipse([x - 55, y - 5, x - 15, y + 25], fill=(190, 170, 160, 70))
            draw.ellipse([x + 15, y - 5, x + 55, y + 25], fill=(190, 170, 160, 70))
    
    def _draw_jawline(self, draw, x, y, jaw_type):
        """Define jawline shape"""
        if jaw_type == 'square':
            draw.line([x - 80, y + 60, x - 60, y + 90, x + 60, y + 90, x + 80, y + 60],
                     fill=(200, 180, 170), width=2)
        elif jaw_type == 'round':
            draw.arc([x - 80, y + 40, x + 80, y + 100], 0, 180, fill=(200, 180, 170), width=2)
        elif jaw_type == 'oval':
            draw.arc([x - 70, y + 30, x + 70, y + 90], 10, 170, fill=(200, 180, 170), width=2)
        else:  # heart
            draw.line([x - 70, y + 50, x - 50, y + 85, x, y + 95, x + 50, y + 85, x + 70, y + 50],
                     fill=(200, 180, 170), width=2)
    
    def _apply_expression(self, face, expression):
        """Apply facial expression"""
        if expression not in self.expressions:
            return face
        
        expr_values = self.expressions[expression]
        img = face.copy()
        
        # Apply expression deformations
        # This is a simplified version - in production use face mesh deformation
        if expr_values[0] > 0:  # Happy - raise cheeks
            img = self._apply_happy_expression(img, expr_values[0])
        elif expr_values[0] < 0:  # Sad - lower corners
            img = self._apply_sad_expression(img, abs(expr_values[0]))
        
        if expr_values[1] > 0:  # Surprise - raise eyebrows
            img = self._apply_surprise_expression(img, expr_values[1])
        
        if expr_values[3] > 0:  # Singing - open mouth
            img = self._apply_singing_expression(img, expr_values[3])
        
        return img
    
    def _apply_happy_expression(self, img, intensity):
        """Apply happy expression"""
        draw = ImageDraw.Draw(img)
        size = img.size
        cx, cy = size[0] // 2, size[1] // 2
        
        # Raise corners of mouth
        for x_offset in [-30, 30]:
            y_offset = int(10 * intensity)
            draw.arc([cx + x_offset - 15, cy + 50 - y_offset, 
                     cx + x_offset + 15, cy + 70 - y_offset],
                    0, 180, fill=(200, 100, 100), width=2)
        
        return img
    
    def _apply_sad_expression(self, img, intensity):
        """Apply sad expression"""
        draw = ImageDraw.Draw(img)
        size = img.size
        cx, cy = size[0] // 2, size[1] // 2
        
        # Lower corners of mouth
        for x_offset in [-30, 30]:
            y_offset = int(10 * intensity)
            draw.arc([cx + x_offset - 15, cy + 50 + y_offset,
                     cx + x_offset + 15, cy + 70 + y_offset],
                    180, 360, fill=(200, 100, 100), width=2)
        
        return img
    
    def _apply_surprise_expression(self, img, intensity):
        """Apply surprise expression"""
        draw = ImageDraw.Draw(img)
        size = img.size
        cx, cy = size[0] // 2, size[1] // 2
        
        # Raise eyebrows
        for x_offset in [-35, 35]:
            y_offset = int(15 * intensity)
            draw.arc([cx + x_offset - 20, cy - 60 - y_offset,
                     cx + x_offset + 20, cy - 40 - y_offset],
                    0, 180, fill=(40, 30, 20), width=3)
        
        # Open eyes wider
        for x_offset in [-35, 35]:
            draw.ellipse([cx + x_offset - 18, cy - 20 - y_offset//2,
                         cx + x_offset + 18, cy + 10 - y_offset//2],
                        fill=(255, 255, 255))
            draw.ellipse([cx + x_offset - 8, cy - 10 - y_offset//2,
                         cx + x_offset + 8, cy + 5 - y_offset//2],
                        fill=(60, 80, 120))
        
        return img
    
    def _apply_singing_expression(self, img, intensity):
        """Apply singing expression (open mouth)"""
        draw = ImageDraw.Draw(img)
        size = img.size
        cx, cy = size[0] // 2, size[1] // 2
        
        # Open mouth
        mouth_height = int(20 * intensity)
        draw.ellipse([cx - 25, cy + 35, cx + 25, cy + 45 + mouth_height],
                    fill=(50, 20, 20))
        draw.ellipse([cx - 22, cy + 37, cx + 22, cy + 43 + mouth_height],
                    fill=(30, 10, 10))
        
        return img
    
    def _add_hair(self, face, hairstyle, gender):
        """Add hair to face"""
        img = face.copy()
        draw = ImageDraw.Draw(img)
        size = img.size
        cx, cy = size[0] // 2, size[1] // 2
        
        hair_color = self._get_hair_color(gender)
        
        if hairstyle == 'long':
            # Long flowing hair
            for i in range(5):
                y_offset = i * 10
                draw.arc([cx - 90, cy - 80 + y_offset, cx + 90, cy + 20 + y_offset],
                        0, 180, fill=hair_color, width=15 - i)
        
        elif hairstyle == 'short':
            # Short hair
            draw.arc([cx - 85, cy - 90, cx + 85, cy - 30], 0, 180, fill=hair_color, width=20)
        
        elif hairstyle == 'curly':
            # Curly hair
            for i in range(3):
                for j in range(6):
                    x_offset = -70 + j * 28
                    y_offset = -70 + i * 15
                    draw.ellipse([cx + x_offset - 15, cy + y_offset - 10,
                                 cx + x_offset + 15, cy + y_offset + 10],
                                fill=hair_color)
        
        elif hairstyle == 'straight':
            # Straight hair
            for i in range(3):
                draw.line([cx - 80 + i * 30, cy - 90, cx - 80 + i * 30, cy + 20],
                         fill=hair_color, width=12)
        
        elif hairstyle == 'ponytail':
            # Ponytail
            draw.arc([cx - 80, cy - 90, cx + 80, cy - 30], 0, 180, fill=hair_color, width=20)
            # Ponytail
            for i in range(10):
                y_offset = i * 8
                draw.ellipse([cx + 30 - 10, cy - 20 + y_offset,
                             cx + 50 + 10, cy + 20 + y_offset],
                            fill=hair_color)
        
        elif hairstyle == 'bun':
            # Bun
            draw.arc([cx - 80, cy - 90, cx + 80, cy - 30], 0, 180, fill=hair_color, width=20)
            draw.ellipse([cx - 25, cy - 75, cx + 25, cy - 35], fill=hair_color)
        
        return img
    
    def _get_hair_color(self, gender):
        """Get hair color based on gender"""
        colors = {
            'male': [(40, 30, 20), (30, 25, 20), (50, 40, 30)],
            'female': [(60, 40, 30), (50, 35, 25), (70, 50, 40)]
        }
        return random.choice(colors.get(gender, colors['male']))
    
    def _add_skin_texture(self, face):
        """Add realistic skin texture"""
        img = face.copy()
        
        # Add subtle noise for texture
        np_img = np.array(img)
        noise = np.random.normal(0, 3, np_img.shape[:2])
        noise = np.stack([noise] * 4, axis=2)
        np_img = np_img + noise
        np_img = np.clip(np_img, 0, 255).astype(np.uint8)
        
        img = Image.fromarray(np_img)
        
        # Apply slight blur for realism
        img = img.filter(ImageFilter.SMOOTH)
        
        return img
    
    def _enhance_face(self, face):
        """Apply final enhancements to face"""
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(face)
        face = enhancer.enhance(1.1)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(face)
        face = enhancer.enhance(1.2)
        
        return face
    
    def morph_faces(self, face1, face2, alpha=0.5):
        """Morph between two faces"""
        # In production, use actual face morphing
        # This is a simplified version using Image.blend
        img1 = face1.convert('RGBA')
        img2 = face2.convert('RGBA')
        return Image.blend(img1, img2, alpha)
