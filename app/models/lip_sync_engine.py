import numpy as np
import cv2
from collections import deque

class LipSyncEngine:
    def __init__(self, config):
        self.config = config
        self.visemes = {
            'sil': [0.0, 0.0, 0.0, 0.0, 0.0],
            'AA': [1.0, 0.0, 0.0, 0.0, 0.0],
            'AE': [1.0, 0.0, 0.0, 0.0, 0.0],
            'AH': [1.0, 0.0, 0.0, 0.0, 0.0],
            'AO': [0.0, 0.8, 0.0, 0.0, 0.0],
            'AW': [0.0, 0.0, 0.5, 0.0, 0.0],
            'AY': [0.0, 0.0, 0.0, 0.5, 0.0],
            'B': [0.0, 0.0, 0.0, 0.0, 1.0],
            'CH': [0.0, 0.0, 0.0, 0.0, 1.0],
            'D': [0.0, 0.0, 0.0, 0.0, 1.0],
            'DH': [0.0, 0.0, 0.0, 0.0, 1.0],
            'EH': [1.0, 0.0, 0.0, 0.0, 0.0],
            'ER': [0.0, 0.8, 0.0, 0.0, 0.0],
            'EY': [0.0, 0.0, 0.5, 0.0, 0.0],
            'F': [0.0, 0.0, 0.0, 0.0, 1.0],
            'G': [0.0, 0.0, 0.0, 0.0, 1.0],
            'HH': [0.0, 0.0, 0.0, 0.0, 0.0],
            'IH': [1.0, 0.0, 0.0, 0.0, 0.0],
            'IY': [0.0, 0.0, 0.5, 0.0, 0.0],
            'JH': [0.0, 0.0, 0.0, 0.0, 1.0],
            'K': [0.0, 0.0, 0.0, 0.0, 1.0],
            'L': [0.0, 0.0, 0.0, 0.5, 0.0],
            'M': [0.0, 0.0, 0.0, 0.0, 1.0],
            'N': [0.0, 0.0, 0.0, 0.0, 1.0],
            'NG': [0.0, 0.0, 0.0, 0.0, 1.0],
            'OW': [0.0, 0.8, 0.0, 0.0, 0.0],
            'OY': [0.0, 0.0, 0.5, 0.0, 0.0],
            'P': [0.0, 0.0, 0.0, 0.0, 1.0],
            'R': [0.0, 0.0, 0.0, 0.5, 0.0],
            'S': [0.0, 0.0, 0.0, 0.0, 1.0],
            'SH': [0.0, 0.0, 0.0, 0.0, 1.0],
            'T': [0.0, 0.0, 0.0, 0.0, 1.0],
            'TH': [0.0, 0.0, 0.0, 0.0, 1.0],
            'UH': [0.0, 0.8, 0.0, 0.0, 0.0],
            'UW': [0.0, 0.8, 0.0, 0.0, 0.0],
            'V': [0.0, 0.0, 0.0, 0.0, 1.0],
            'W': [0.0, 0.0, 0.5, 0.0, 0.0],
            'Y': [0.0, 0.0, 0.5, 0.0, 0.0],
            'Z': [0.0, 0.0, 0.0, 0.0, 1.0],
            'ZH': [0.0, 0.0, 0.0, 0.0, 1.0]
        }
        
    def process_audio_for_lip_sync(self, audio_data, sample_rate):
        """Process audio to extract lip sync data"""
        # Extract phonemes and timestamps
        phonemes, times = self._extract_phonemes(audio_data, sample_rate)
        
        # Map phonemes to visemes
        viseme_sequence = self._map_to_visemes(phonemes)
        
        # Create mouth shape sequence
        mouth_shapes = self._generate_mouth_shapes(viseme_sequence, times)
        
        return {
            'viseme_sequence': viseme_sequence,
            'times': times,
            'mouth_shapes': mouth_shapes,
            'phonemes': phonemes
        }
    
    def _extract_phonemes(self, audio_data, sample_rate):
        """Extract phonemes from audio (simplified for demo)"""
        # In production, use a proper phoneme extraction model
        import librosa
        
        # Detect voiced segments
        voiced_frames = librosa.feature.rms(y=audio_data)[0] > 0.1
        times = librosa.times_like(voiced_frames, sr=sample_rate)
        
        # Simulate phoneme sequence
        phonemes = []
        for i, voiced in enumerate(voiced_frames):
            if voiced:
                phoneme = list(self.visemes.keys())[np.random.randint(0, len(self.visemes))]
                phonemes.append(phoneme)
            else:
                phonemes.append('sil')
        
        return phonemes, times
    
    def _map_to_visemes(self, phonemes):
        """Map phonemes to visemes"""
        visemes = []
        for phoneme in phonemes:
            viseme = self.visemes.get(phoneme, self.visemes['sil'])
            visemes.append(viseme)
        return visemes
    
    def _generate_mouth_shapes(self, visemes, times):
        """Generate smooth mouth shape animation"""
        shape_sequence = []
        
        for i, viseme in enumerate(visemes):
            # Smooth transitions between visemes
            if i > 0:
                prev_viseme = visemes[i-1]
                # Interpolate between previous and current viseme
                for t in np.linspace(0, 1, 5):
                    interpolated = self._interpolate_viseme(prev_viseme, viseme, t)
                    shape_sequence.append(interpolated)
            else:
                shape_sequence.append(viseme)
        
        return shape_sequence
    
    def _interpolate_viseme(self, viseme1, viseme2, t):
        """Interpolate between two visemes"""
        return [v1 + (v2 - v1) * t for v1, v2 in zip(viseme1, viseme2)]
    
    def render_lip_sync(self, character_image, mouth_shapes, times):
        """Render lip sync animation on character"""
        # Create frames for each mouth shape
        frames = []
        for i, shape in enumerate(mouth_shapes):
            frame = character_image.copy()
            # Apply mouth shape to character
            # In production, this would use a full face morphing system
            frames.append(frame)
        
        return frames
