import numpy as np
from scipy.signal import butter, lfilter
import librosa

class BeatDetector:
    def __init__(self, config):
        self.config = config
        self.beat_times = []
        self.onset_frames = []
        self.tempo = 0
        
    def detect_beats(self, audio_data, sample_rate):
        """Detect beats with high accuracy"""
        try:
            # Compute onset strength
            onset_env = librosa.onset.onset_strength(
                y=audio_data, 
                sr=sample_rate,
                aggregate=np.median
            )
            
            # Detect tempo
            self.tempo, beat_frames = librosa.beat.beat_track(
                onset_envelope=onset_env,
                sr=sample_rate
            )
            
            # Convert to time
            self.beat_times = librosa.frames_to_time(
                beat_frames, 
                sr=sample_rate
            ).tolist()
            
            # Get onset frames for instrument detection
            self.onset_frames = librosa.onset.onset_detect(
                onset_envelope=onset_env,
                sr=sample_rate
            )
            
            return {
                'tempo': float(self.tempo),
                'beat_times': self.beat_times,
                'onset_times': librosa.frames_to_time(
                    self.onset_frames, 
                    sr=sample_rate
                ).tolist()
            }
        except Exception as e:
            raise RuntimeError(f"Beat detection failed: {str(e)}")
    
    def get_downbeats(self):
        """Detect downbeats (first beat of each measure)"""
        if not self.beat_times:
            return []
            
        # Assuming 4/4 time signature
        downbeats = []
        for i, beat in enumerate(self.beat_times):
            if i % 4 == 0:
                downbeats.append(beat)
        
        return downbeats
    
    def get_beat_intensity(self, audio_data, sample_rate):
        """Calculate beat intensity for dynamics"""
        onset_env = librosa.onset.onset_strength(
            y=audio_data, 
            sr=sample_rate
        )
        
        # Normalize intensity
        intensity = (onset_env - np.min(onset_env)) / \
                    (np.max(onset_env) - np.min(onset_env))
        
        return intensity.tolist()
