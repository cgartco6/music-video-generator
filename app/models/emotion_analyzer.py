import torch
import torch.nn as nn
import numpy as np
import librosa
from collections import deque

class EmotionAnalyzer:
    def __init__(self, config):
        self.config = config
        self.device = torch.device('cuda' if config.USE_GPU and torch.cuda.is_available() else 'cpu')
        self.model = None
        self._load_model()
        
        # Emotion mapping for audio features
        self.emotion_mapping = {
            'happy': {'tempo': (120, 160), 'energy': (0.7, 1.0), 'valence': (0.6, 1.0)},
            'sad': {'tempo': (60, 90), 'energy': (0.0, 0.4), 'valence': (0.0, 0.3)},
            'energetic': {'tempo': (140, 180), 'energy': (0.8, 1.0), 'valence': (0.5, 0.8)},
            'calm': {'tempo': (60, 100), 'energy': (0.0, 0.3), 'valence': (0.3, 0.6)},
            'angry': {'tempo': (130, 170), 'energy': (0.7, 1.0), 'valence': (0.0, 0.2)},
            'romantic': {'tempo': (70, 110), 'energy': (0.3, 0.6), 'valence': (0.5, 0.8)},
            'melancholic': {'tempo': (60, 90), 'energy': (0.1, 0.4), 'valence': (0.1, 0.3)},
            'triumphant': {'tempo': (120, 150), 'energy': (0.8, 1.0), 'valence': (0.7, 1.0)}
        }
    
    def _load_model(self):
        """Load emotion recognition model"""
        try:
            model_path = self.config.EMOTION_MODEL
            if os.path.exists(model_path):
                self.model = torch.load(model_path, map_location=self.device)
            else:
                print(f"Warning: Emotion model not found at {model_path}")
                print("Using rule-based emotion detection")
        except Exception as e:
            print(f"Error loading emotion model: {str(e)}")
            self.model = None
    
    def analyze_audio_emotion(self, audio_data, sample_rate):
        """Analyze emotion from audio features"""
        # Extract features
        features = self._extract_features(audio_data, sample_rate)
        
        # Detect emotion using rule-based system (or ML model if available)
        if self.model is not None:
            emotion = self._predict_with_model(features)
        else:
            emotion = self._predict_with_rules(features)
        
        # Get emotional intensity and confidence
        intensity = self._calculate_intensity(features, emotion)
        confidence = self._calculate_confidence(features, emotion)
        
        # Get emotional progression over time
        progression = self._get_emotion_progression(audio_data, sample_rate)
        
        return {
            'primary_emotion': emotion,
            'intensity': intensity,
            'confidence': confidence,
            'progression': progression,
            'features': features
        }
    
    def _extract_features(self, audio_data, sample_rate):
        """Extract relevant audio features for emotion detection"""
        features = {}
        
        # Tempo
        tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
        features['tempo'] = float(tempo)
        
        # Energy
        features['energy'] = float(np.mean(np.abs(audio_data)))
        
        # Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
        features['spectral_centroid'] = float(np.mean(spectral_centroid))
        
        # Root Mean Square (RMS)
        rms = librosa.feature.rms(y=audio_data)
        features['rms'] = float(np.mean(rms))
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y=audio_data)
        features['zcr'] = float(np.mean(zcr))
        
        # Mel-frequency cepstral coefficients (MFCC)
        mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        features['mfcc'] = np.mean(mfcc, axis=1).tolist()
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
        features['chroma'] = np.mean(chroma, axis=1).tolist()
        
        # Harmonic and percussive components
        harmonic, percussive = librosa.effects.hpss(audio_data)
        features['harmonic_ratio'] = float(np.sum(harmonic**2) / (np.sum(percussive**2) + 1e-6))
        
        # Onset strength
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sample_rate)
        features['onset_strength'] = float(np.mean(onset_env))
        
        # Spectral contrast
        contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
        features['spectral_contrast'] = np.mean(contrast, axis=1).tolist()
        
        return features
    
    def _predict_with_rules(self, features):
        """Predict emotion using rule-based system"""
        scores = {}
        
        for emotion, params in self.emotion_mapping.items():
            score = 0
            
            # Check tempo
            tempo = features['tempo']
            if params['tempo'][0] <= tempo <= params['tempo'][1]:
                score += 0.3
            
            # Check energy
            energy = features['energy']
            if params['energy'][0] <= energy <= params['energy'][1]:
                score += 0.3
            
            # Check valence (approximated from spectral features)
            valence = self._estimate_valence(features)
            if params['valence'][0] <= valence <= params['valence'][1]:
                score += 0.4
            
            scores[emotion] = score
        
        # Return emotion with highest score
        return max(scores, key=scores.get)
    
    def _estimate_valence(self, features):
        """Estimate valence (positivity) from audio features"""
        # Higher energy, higher spectral centroid = more positive
        energy_norm = min(1.0, features['energy'] * 2)
        spectral_norm = min(1.0, features['spectral_centroid'] / 5000)
        valence = (energy_norm * 0.5 + spectral_norm * 0.5)
        return valence
    
    def _predict_with_model(self, features):
        """Predict emotion using ML model"""
        # Prepare features for model
        input_features = np.array([
            features['tempo'],
            features['energy'],
            features['spectral_centroid'],
            features['rms'],
            features['zcr'],
            features['harmonic_ratio'],
            features['onset_strength']
        ]).reshape(1, -1)
        
        # Convert to tensor
        input_tensor = torch.FloatTensor(input_features).to(self.device)
        
        # Get prediction
        with torch.no_grad():
            output = self.model(input_tensor)
            emotion_idx = torch.argmax(output, dim=1).item()
        
        # Map index to emotion
        emotion_list = list(self.emotion_mapping.keys())
        return emotion_list[min(emotion_idx, len(emotion_list) - 1)]
    
    def _calculate_intensity(self, features, emotion):
        """Calculate emotional intensity"""
        # Intensity based on energy and tempo
        intensity = features['energy'] * 0.5 + (features['tempo'] / 200) * 0.5
        return min(1.0, intensity)
    
    def _calculate_confidence(self, features, emotion):
        """Calculate confidence in emotion detection"""
        # Based on how well features match the emotion parameters
        params = self.emotion_mapping.get(emotion, {})
        if not params:
            return 0.5
        
        confidence = 0.0
        if 'tempo' in params:
            tempo = features['tempo']
            if params['tempo'][0] <= tempo <= params['tempo'][1]:
                confidence += 0.33
        
        if 'energy' in params:
            energy = features['energy']
            if params['energy'][0] <= energy <= params['energy'][1]:
                confidence += 0.33
        
        if 'valence' in params:
            valence = self._estimate_valence(features)
            if params['valence'][0] <= valence <= params['valence'][1]:
                confidence += 0.34
        
        return confidence
    
    def _get_emotion_progression(self, audio_data, sample_rate):
        """Get emotion progression over time"""
        # Split audio into segments
        segment_duration = 2.0  # seconds
        segment_samples = int(segment_duration * sample_rate)
        num_segments = len(audio_data) // segment_samples
        
        progression = []
        
        for i in range(num_segments):
            start = i * segment_samples
            end = start + segment_samples
            segment = audio_data[start:end]
            
            if len(segment) > 100:
                features = self._extract_features(segment, sample_rate)
                emotion = self._predict_with_rules(features)
                intensity = self._calculate_intensity(features, emotion)
                
                progression.append({
                    'time': i * segment_duration,
                    'emotion': emotion,
                    'intensity': intensity
                })
        
        return progression
    
    def get_emotion_for_scene(self, progression, scene_time):
        """Get emotion for a specific scene time"""
        if not progression:
            return 'neutral', 0.5
        
        # Find the closest time point
        closest = min(progression, key=lambda x: abs(x['time'] - scene_time))
        return closest['emotion'], closest['intensity']
