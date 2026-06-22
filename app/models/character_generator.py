import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random

class CharacterGenerator:
    def __init__(self, config):
        self.config = config
        self.character_types = config.AVAILABLE_CHARACTERS
        self.instruments = config.AVAILABLE_INSTRUMENTS
        
    def generate_character(self, character_type, instrument=None):
        """Generate character based on type and instrument"""
        if character_type not in self.character_types:
            raise ValueError(f"Invalid character type: {character_type}")
            
        character = {
            'type': character_type,
            'instrument': instrument,
            'pose': self._generate_pose(character_type, instrument),
            'facial_features': self._generate_facial_features(character_type),
            'body_proportions': self._generate_body_proportions(character_type),
            'animation_style': self._get_animation_style(character_type)
        }
        
        return character
    
    def _generate_pose(self, character_type, instrument):
        """Generate realistic pose based on role"""
        poses = {
            'male_singer': [
                {'standing': True, 'arms': 'raised', 'legs': 'slightly_apart'},
                {'standing': True, 'arms': 'crossed', 'legs': 'shoulder_width'},
                {'standing': True, 'arms': 'one_raised', 'legs': 'hip_width'}
            ],
            'female_singer': [
                {'standing': True, 'arms': 'elegant', 'legs': 'turned'},
                {'standing': True, 'arms': 'gesturing', 'legs': 'crossed'},
                {'standing': True, 'arms': 'one_hip', 'legs': 'slightly_bent'}
            ],
            'band_member': [
                {'sitting': True, 'arms': 'playing_instrument', 'legs': 'positioned'}
            ]
        }
        
        if character_type in poses:
            return random.choice(poses[character_type])
        
        return {'standing': True, 'arms': 'neutral', 'legs': 'straight'}
    
    def _generate_facial_features(self, character_type):
        """Generate facial features for lip sync"""
        features = {
            'mouth_shape': 'neutral',
            'eye_expression': 'neutral',
            'head_position': 'center'
        }
        
        if 'singer' in character_type:
            features['mouth_shape'] = 'open_singing'
            features['eye_expression'] = 'expressive'
        
        return features
    
    def _generate_body_proportions(self, character_type):
        """Generate realistic body proportions"""
        proportions = {
            'male_singer': {'height': 1.8, 'shoulder_width': 0.45, 'hip_width': 0.35},
            'female_singer': {'height': 1.7, 'shoulder_width': 0.38, 'hip_width': 0.40},
            'band_member': {'height': 1.75, 'shoulder_width': 0.42, 'hip_width': 0.38}
        }
        
        return proportions.get(character_type, {'height': 1.7, 'shoulder_width': 0.4, 'hip_width': 0.38})
    
    def _get_animation_style(self, character_type):
        """Get animation style based on character type"""
        styles = {
            'male_singer': 'energetic',
            'female_singer': 'graceful',
            'band_member': 'rhythmic',
            'dancer': 'dynamic'
        }
        
        return styles.get(character_type, 'neutral')
    
    def create_character_visual(self, character):
        """Create visual representation of character"""
        size = (512, 512)
        image = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw body based on proportions
        width, height = size
        center_x = width // 2
        center_y = height // 2
        
        # Draw head
        head_radius = 30
        draw.ellipse(
            [center_x - head_radius, center_y - 100 - head_radius,
             center_x + head_radius, center_y - 100 + head_radius],
            fill=(255, 200, 150)
        )
        
        # Draw body
        body_props = character['body_proportions']
        body_width = int(body_props['shoulder_width'] * 100)
        body_height = int(body_props['height'] * 100)
        
        draw.rectangle(
            [center_x - body_width//2, center_y - 70,
             center_x + body_width//2, center_y + body_height//2],
            fill=(200, 180, 160)
        )
        
        # Draw arms based on pose
        pose = character['pose']
        if 'arms' in pose:
            if pose['arms'] == 'raised':
                draw.line(
                    [(center_x - 50, center_y - 50), 
                     (center_x - 80, center_y - 100)],
                    fill=(200, 180, 160), width=10
                )
                draw.line(
                    [(center_x + 50, center_y - 50), 
                     (center_x + 80, center_y - 100)],
                    fill=(200, 180, 160), width=10
                )
        
        # Add instrument if applicable
        if character['instrument']:
            self._draw_instrument(draw, center_x, center_y, character['instrument'])
        
        # Apply filters for realism
        image = image.filter(ImageFilter.SMOOTH_MORE)
        
        return image
    
    def _draw_instrument(self, draw, x, y, instrument_type):
        """Draw instrument based on type"""
        instruments = {
            'guitar': lambda: draw.rectangle(
                [x - 30, y - 20, x + 30, y + 40], 
                fill=(160, 100, 50)
            ),
            'drums': lambda: draw.ellipse(
                [x - 40, y - 40, x + 40, y + 40],
                fill=(200, 200, 200)
            ),
            'keyboard': lambda: draw.rectangle(
                [x - 60, y - 20, x + 60, y + 20],
                fill=(50, 50, 50)
            )
        }
        
        if instrument_type in instruments:
            instruments[instrument_type]()
