# This file is already included in the app/models/emotion_recognition/emotion_mapper.py
# I'll just give the code again.
class EmotionMapper:
    def __init__(self):
        self.emotion_map = {
            0: 'neutral', 1: 'happy', 2: 'sad', 3: 'angry',
            4: 'surprised', 5: 'fear', 6: 'disgust', 7: 'passionate'
        }
        self.reverse_map = {v: k for k, v in self.emotion_map.items()}
        self.audio_features = {
            'happy': {'tempo': (120, 160), 'energy': (0.7, 1.0), 'valence': (0.6, 1.0)},
            'sad': {'tempo': (60, 90), 'energy': (0.0, 0.4), 'valence': (0.0, 0.3)},
            # ... etc (include all emotions)
        }
    def map_emotion(self, emotion_id):
        return self.emotion_map.get(emotion_id, 'neutral')
    def get_audio_parameters(self, emotion):
        return self.audio_features.get(emotion, self.audio_features['happy'])
    # Other methods...
