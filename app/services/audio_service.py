import librosa
import numpy as np
import soundfile as sf
import os
from scipy.signal import resample

class AudioService:
    def __init__(self, config):
        self.config = config
        self.sample_rate = config.SAMPLE_RATE
        self.chunk_size = config.CHUNK_SIZE
    
    def load_audio(self, file_path):
        """Load and process audio file"""
        try:
            audio, sr = librosa.load(file_path, sr=self.sample_rate)
            return audio
        except Exception as e:
            raise RuntimeError(f"Failed to load audio: {str(e)}")
    
    def save_audio(self, audio, file_path, sample_rate=None):
        """Save audio to file"""
        if sample_rate is None:
            sample_rate = self.sample_rate
        sf.write(file_path, audio, sample_rate)
    
    def get_audio_duration(self, audio):
        """Get audio duration in seconds"""
        return len(audio) / self.sample_rate
    
    def normalize_audio(self, audio):
        """Normalize audio to [-1, 1] range"""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val
        return audio
    
    def extract_voice_features(self, audio, sr):
        """Extract voice features for cloning"""
        # Pitch extraction
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
        pitch_values = pitches[magnitudes > np.median(magnitudes)]
        
        if len(pitch_values) > 0:
            pitch_mean = np.mean(pitch_values)
            pitch_std = np.std(pitch_values)
        else:
            pitch_mean = 0
            pitch_std = 0
        
        # MFCCs
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        
        # Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y=audio)
        
        # RMS energy
        rms = librosa.feature.rms(y=audio)
        
        return {
            'pitch_mean': float(pitch_mean),
            'pitch_std': float(pitch_std),
            'mfcc_mean': mfcc_mean.tolist(),
            'spectral_centroid': float(np.mean(spectral_centroid)),
            'spectral_rolloff': float(np.mean(spectral_rolloff)),
            'spectral_bandwidth': float(np.mean(spectral_bandwidth)),
            'zcr': float(np.mean(zcr)),
            'rms': float(np.mean(rms))
        }
    
    def pitch_shift_audio(self, audio, semitones):
        """Pitch shift audio by semitones"""
        return librosa.effects.pitch_shift(audio, sr=self.sample_rate, n_steps=semitones)
    
    def time_stretch_audio(self, audio, rate):
        """Time stretch audio by rate"""
        return librosa.effects.time_stretch(audio, rate=rate)
    
    def extract_mel_spectrogram(self, audio):
        """Extract mel spectrogram"""
        return librosa.feature.melspectrogram(y=audio, sr=self.sample_rate)
    
    def extract_mfcc(self, audio, n_mfcc=13):
        """Extract MFCC features"""
        return librosa.feature.mfcc(y=audio, sr=self.sample_rate, n_mfcc=n_mfcc)
    
    def extract_chroma(self, audio):
        """Extract chroma features"""
        return librosa.feature.chroma_stft(y=audio, sr=self.sample_rate)
    
    def separate_harmonic_percussive(self, audio):
        """Separate harmonic and percussive components"""
        return librosa.effects.hpss(audio)
    
    def get_onsets(self, audio):
        """Get onset times"""
        onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
        return librosa.onset.onset_detect(onset_envelope=onset_env, sr=self.sample_rate)
