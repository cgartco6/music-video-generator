import numpy as np
import random

class SceneComposer:
    def __init__(self, config):
        self.config = config
        self.scene_types = ['closeup', 'medium', 'wide', 'performance']
        
    def compose_scenes(self, audio_features, characters, beat_times):
        """Compose video scenes based on audio features"""
        scenes = []
        
        # Analyze audio structure
        sections = self._analyze_audio_structure(audio_features)
        
        # Create scenes for each section
        for section in sections:
            scene = self._create_scene(section, characters)
            scenes.append(scene)
        
        # Add transitions between scenes
        self._add_transitions(scenes)
        
        # Assign timing based on beats
        self._assign_timing(scenes, beat_times)
        
        return scenes
    
    def _analyze_audio_structure(self, audio_features):
        """Analyze audio to determine sections"""
        sections = []
        
        # Detect intensity changes
        energy = audio_features.get('energy', 0)
        
        if energy > 0.7:
            section_type = 'chorus'
            intensity = 'high'
        elif energy > 0.3:
            section_type = 'verse'
            intensity = 'medium'
        else:
            section_type = 'intro'
            intensity = 'low'
        
        # Create multiple sections
        for i in range(4):
            sections.append({
                'type': section_type,
                'intensity': intensity,
                'duration': 8 + i * 2  # seconds
            })
        
        return sections
    
    def _create_scene(self, section, characters):
        """Create a scene based on section properties"""
        scene = {
            'type': random.choice(self.scene_types),
            'characters': self._select_characters(characters, section),
            'camera_angle': self._get_camera_angle(section),
            'lighting': self._get_lighting(section),
            'background': self._get_background(section),
            'intensity': section['intensity'],
            'duration': section['duration']
        }
        
        return scene
    
    def _select_characters(self, characters, section):
        """Select characters for scene"""
        selected = []
        if characters:
            # Select main characters based on section intensity
            if section['intensity'] == 'high':
                selected = characters[:2]  # More characters in high intensity
            else:
                selected = [characters[0]]  # Fewer in low intensity
        return selected
    
    def _get_camera_angle(self, section):
        """Get camera angle based on section"""
        angles = ['front', 'side', 'slight_left', 'slight_right']
        return random.choice(angles)
    
    def _get_lighting(self, section):
        """Get lighting setup based on section"""
        if section['intensity'] == 'high':
            return {'brightness': 0.8, 'color': 'warm', 'dynamic': True}
        elif section['intensity'] == 'medium':
            return {'brightness': 0.5, 'color': 'neutral', 'dynamic': False}
        else:
            return {'brightness': 0.3, 'color': 'cool', 'dynamic': False}
    
    def _get_background(self, section):
        """Get background scene based on section"""
        backgrounds = [
            {'type': 'cityscape', 'elements': ['lights', 'buildings']},
            {'type': 'studio', 'elements': ['lights', 'speakers']},
            {'type': 'natural', 'elements': ['trees', 'water']}
        ]
        return random.choice(backgrounds)
    
    def _add_transitions(self, scenes):
        """Add transitions between scenes"""
        for i in range(len(scenes) - 1):
            scenes[i]['transition'] = {
                'type': random.choice(['fade', 'wipe', 'crossfade']),
                'duration': 0.5
            }
    
    def _assign_timing(self, scenes, beat_times):
        """Assign timing to scenes based on beats"""
        if not beat_times:
            return
        
        total_beats = len(beat_times)
        beats_per_scene = total_beats // len(scenes)
        
        for i, scene in enumerate(scenes):
            start_idx = i * beats_per_scene
            end_idx = start_idx + beats_per_scene
            if end_idx < len(beat_times):
                scene['start_beat'] = beat_times[start_idx]
                scene['end_beat'] = beat_times[end_idx - 1]
