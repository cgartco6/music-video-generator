# This file is already included in the app/models/emotion_recognition/emotion_mapper.py
# I'll just give the code again.
class EmotionMapper:
    def __init__(self):
        self.emotion_map = {
            0: 'neutral',
            1: 'happy',
            2: 'sad',
            3: 'angry',
            4: 'surprised',
            5: 'fear',
            6: 'disgust',
            7: 'passionate'
        }
        
        self.audio_emotion_map = {
            'happy': {'tempo': (120, 160), 'energy': (0.7, 1.0), 'valence': (0.6, 1.0)},
            'sad': {'tempo': (60, 90), 'energy': (0.0, 0.4), 'valence': (0.0, 0.3)},
            'angry': {'tempo': (130, 170), 'energy': (0.7, 1.0), 'valence': (0.0, 0.2)},
            'surprised': {'tempo': (100, 140), 'energy': (0.6, 0.9), 'valence': (0.4, 0.7)},
            'fear': {'tempo': (80, 120), 'energy': (0.3, 0.6), 'valence': (0.1, 0.3)},
            'disgust': {'tempo': (70, 110), 'energy': (0.2, 0.5), 'valence': (0.0, 0.2)},
            'passionate': {'tempo': (100, 140), 'energy': (0.8, 1.0), 'valence': (0.5, 0.8)},
            'neutral': {'tempo': (90, 120), 'energy': (0.3, 0.6), 'valence': (0.3, 0.6)}
        }
    
    def map_emotion(self, emotion_id):
        """Map emotion ID to name"""
        return self.emotion_map.get(emotion_id, 'neutral')
    
    def get_audio_parameters(self, emotion):
        """Get audio parameters for emotion"""
        return self.audio_emotion_map.get(emotion, self.audio_emotion_map['neutral'])
    
    def detect_emotion_from_features(self, features):
        """Detect emotion from audio features"""
        best_emotion = 'neutral'
        best_score = 0
        
        for emotion, params in self.audio_emotion_map.items():
            score = 0
            
            tempo = features.get('tempo', 120)
            if params['tempo'][0] <= tempo <= params['tempo'][1]:
                score += 0.3
            
            energy = features.get('energy', 0.5)
            if params['energy'][0] <= energy <= params['energy'][1]:
                score += 0.3
            
            valence = self.estimate_valence(features)
            if params['valence'][0] <= valence <= params['valence'][1]:
                score += 0.4
            
            if score > best_score:
                best_score = score
                best_emotion = emotion
        
        return best_emotion, best_score
    
    def estimate_valence(self, features):
        """Estimate valence from features"""
        energy = features.get('energy', 0.5)
        spectral_centroid = features.get('spectral_centroid', 2000)
        
        energy_norm = min(1.0, energy * 2)
        spectral_norm = min(1.0, spectral_centroid / 5000)
        
        return energy_norm * 0.5 + spectral_norm * 0.5

