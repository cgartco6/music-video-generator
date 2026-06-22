import numpy as np
import librosa
import soundfile as sf
from scipy.signal import hilbert, butter, lfilter
import os
import json

class MusicStyleReplicator:
    def __init__(self, config):
        self.config = config
        self.style_models = {}
        self.style_profiles = {}
        self.style_profiles_path = os.path.join(config.MODEL_FOLDER, 'style_profiles.json')
        self._load_style_profiles()
        
        # Music style characteristics
        self.style_characteristics = {
            'pop': {
                'tempo_range': (100, 130),
                'energy': 0.7,
                'instrumentation': ['drums', 'bass', 'keys', 'guitar'],
                'rhythm_complexity': 0.6,
                'harmonic_complexity': 0.5,
                'melodic_range': (3, 5)
            },
            'rock': {
                'tempo_range': (120, 160),
                'energy': 0.9,
                'instrumentation': ['drums', 'bass', 'electric_guitar', 'vocals'],
                'rhythm_complexity': 0.7,
                'harmonic_complexity': 0.6,
                'melodic_range': (4, 6)
            },
            'jazz': {
                'tempo_range': (80, 140),
                'energy': 0.5,
                'instrumentation': ['drums', 'bass', 'piano', 'saxophone', 'trumpet'],
                'rhythm_complexity': 0.8,
                'harmonic_complexity': 0.9,
                'melodic_range': (5, 7)
            },
            'classical': {
                'tempo_range': (60, 120),
                'energy': 0.4,
                'instrumentation': ['strings', 'piano', 'woodwinds', 'brass'],
                'rhythm_complexity': 0.3,
                'harmonic_complexity': 0.8,
                'melodic_range': (6, 8)
            },
            'electronic': {
                'tempo_range': (120, 160),
                'energy': 0.8,
                'instrumentation': ['synths', 'drums', 'bass'],
                'rhythm_complexity': 0.7,
                'harmonic_complexity': 0.4,
                'melodic_range': (3, 4)
            },
            'hiphop': {
                'tempo_range': (70, 100),
                'energy': 0.6,
                'instrumentation': ['drums', 'bass', 'synths', 'vocals'],
                'rhythm_complexity': 0.9,
                'harmonic_complexity': 0.3,
                'melodic_range': (2, 3)
            },
            'country': {
                'tempo_range': (80, 120),
                'energy': 0.5,
                'instrumentation': ['acoustic_guitar', 'bass', 'drums', 'fiddle'],
                'rhythm_complexity': 0.4,
                'harmonic_complexity': 0.5,
                'melodic_range': (3, 4)
            },
            'r&b': {
                'tempo_range': (60, 90),
                'energy': 0.5,
                'instrumentation': ['drums', 'bass', 'keys', 'guitar', 'vocals'],
                'rhythm_complexity': 0.7,
                'harmonic_complexity': 0.6,
                'melodic_range': (4, 5)
            }
        }
    
    def _load_style_profiles(self):
        """Load saved style profiles"""
        if os.path.exists(self.style_profiles_path):
            try:
                with open(self.style_profiles_path, 'r') as f:
                    self.style_profiles = json.load(f)
            except:
                self.style_profiles = {}
    
    def save_style_profile(self, profile_name, style_data):
        """Save a custom style profile"""
        self.style_profiles[profile_name] = style_data
        with open(self.style_profiles_path, 'w') as f:
            json.dump(self.style_profiles, f)
        return True
    
    def analyze_music_style(self, audio_path):
        """Analyze music style from audio"""
        try:
            audio, sr = librosa.load(audio_path, sr=22050)
            
            # Extract style features
            style_features = {
                'tempo': self._extract_tempo(audio, sr),
                'energy': self._extract_energy(audio),
                'rhythm_complexity': self._extract_rhythm_complexity(audio, sr),
                'harmonic_complexity': self._extract_harmonic_complexity(audio, sr),
                'instrumentation': self._detect_instruments(audio, sr),
                'spectral_features': self._extract_spectral_features(audio, sr),
                'genre': self._predict_genre(audio, sr)
            }
            
            return style_features
            
        except Exception as e:
            raise RuntimeError(f"Failed to analyze music style: {str(e)}")
    
    def _extract_tempo(self, audio, sr):
        """Extract tempo from audio"""
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
        return float(tempo)
    
    def _extract_energy(self, audio):
        """Extract energy from audio"""
        return float(np.mean(np.abs(audio)))
    
    def _extract_rhythm_complexity(self, audio, sr):
        """Extract rhythm complexity"""
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)
        complexity = np.std(tempogram) / (np.mean(tempogram) + 1e-6)
        return float(min(1, complexity))
    
    def _extract_harmonic_complexity(self, audio, sr):
        """Extract harmonic complexity"""
        chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
        harmonic_complexity = np.std(chroma) / (np.mean(chroma) + 1e-6)
        return float(min(1, harmonic_complexity))
    
    def _detect_instruments(self, audio, sr):
        """Detect instruments in audio"""
        instruments = []
        
        # Extract spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
        
        # Simple instrument detection based on spectral features
        if np.mean(spectral_centroid) > 3000:
            instruments.append('high_freq')
        if np.mean(spectral_centroid) < 1000:
            instruments.append('low_freq')
        if np.mean(spectral_rolloff) > 5000:
            instruments.append('bright')
        
        # Detect drums (percussive)
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        if np.max(onset_env) > 0.5:
            instruments.append('drums')
        
        # Detect bass (low frequencies with stable amplitude)
        if np.mean(spectral_centroid) < 500:
            instruments.append('bass')
        
        return list(set(instruments))
    
    def _extract_spectral_features(self, audio, sr):
        """Extract spectral features"""
        stft = librosa.stft(audio)
        spectral_centroid = librosa.feature.spectral_centroid(S=np.abs(stft))
        spectral_bandwidth = librosa.feature.spectral_bandwidth(S=np.abs(stft))
        spectral_contrast = librosa.feature.spectral_contrast(S=np.abs(stft))
        
        return {
            'centroid_mean': float(np.mean(spectral_centroid)),
            'bandwidth_mean': float(np.mean(spectral_bandwidth)),
            'contrast_mean': float(np.mean(spectral_contrast))
        }
    
    def _predict_genre(self, audio, sr):
        """Predict genre from audio features"""
        # Simplified genre prediction
        tempo = self._extract_tempo(audio, sr)
        energy = self._extract_energy(audio)
        rhythm_complexity = self._extract_rhythm_complexity(audio, sr)
        
        # Rule-based genre prediction
        if tempo > 140 and energy > 0.7:
            return 'electronic'
        elif tempo > 120 and energy > 0.8:
            return 'rock'
        elif 80 <= tempo <= 120 and energy < 0.6:
            return 'pop'
        elif 70 <= tempo <= 100 and rhythm_complexity > 0.7:
            return 'hiphop'
        elif 80 <= tempo <= 140 and rhythm_complexity > 0.6:
            return 'jazz'
        elif tempo < 120 and energy < 0.5:
            return 'classical'
        else:
            return 'pop'
    
    def replicate_style(self, original_audio, target_style, intensity=0.7):
        """Replicate music style in audio"""
        # Get style characteristics
        style_char = self.style_characteristics.get(target_style)
        if style_char is None:
            # Try custom style profile
            if target_style in self.style_profiles:
                style_char = self.style_profiles[target_style]
            else:
                style_char = self.style_characteristics['pop']
        
        # Apply style transformation
        transformed_audio = self._apply_style_transformation(
            original_audio,
            style_char,
            intensity
        )
        
        return transformed_audio
    
    def _apply_style_transformation(self, audio, style_char, intensity):
        """Apply style transformation to audio"""
        sr = 22050
        
        # Adjust tempo
        current_tempo = self._extract_tempo(audio, sr)
        target_tempo = np.mean(style_char['tempo_range'])
        tempo_ratio = target_tempo / (current_tempo + 1e-6)
        
        if abs(tempo_ratio - 1) > 0.05:
            audio = librosa.effects.time_stretch(audio, rate=tempo_ratio)
        
        # Adjust energy
        current_energy = self._extract_energy(audio)
        target_energy = style_char['energy']
        energy_ratio = target_energy / (current_energy + 1e-6)
        audio = audio * (1 + (energy_ratio - 1) * intensity)
        
        # Apply EQ based on style
        audio = self._apply_style_eq(audio, sr, style_char, intensity)
        
        # Add style-specific effects
        audio = self._apply_style_effects(audio, sr, style_char, intensity)
        
        # Normalize
        audio = audio / np.max(np.abs(audio))
        
        return audio
    
    def _apply_style_eq(self, audio, sr, style_char, intensity):
        """Apply style-specific EQ"""
        # Different EQ profiles for different styles
        if style_char['energy'] > 0.7:
            # Boost highs and lows for energetic styles
            b, a = butter(2, [100/(sr/2), 8000/(sr/2)], btype='band')
            audio = lfilter(b, a, audio)
        elif style_char['energy'] < 0.4:
            # Cut highs for mellow styles
            b, a = butter(2, 500/(sr/2), btype='low')
            audio = lfilter(b, a, audio)
        else:
            # Neutral EQ
            pass
        
        return audio
    
    def _apply_style_effects(self, audio, sr, style_char, intensity):
        """Apply style-specific effects"""
        if style_char['genre'] in ['rock', 'electronic']:
            # Add slight distortion for rock/electronic
            audio = self._add_soft_distortion(audio, intensity * 0.3)
        
        if style_char['genre'] == 'jazz':
            # Add warmth for jazz
            audio = self._add_warmth(audio, sr, intensity * 0.4)
        
        if style_char['genre'] == 'classical':
            # Add reverb for classical
            audio = self._add_reverb(audio, sr, intensity * 0.3)
        
        if style_char['genre'] == 'hiphop':
            # Add compression for hiphop
            audio = self._add_compression(audio, intensity * 0.5)
        
        return audio
    
    def _add_soft_distortion(self, audio, amount):
        """Add soft distortion"""
        return np.tanh(audio * (1 + amount))
    
    def _add_warmth(self, audio, sr, amount):
        """Add warmth (boost low mids)"""
        b, a = butter(2, [200/(sr/2), 500/(sr/2)], btype='band')
        warm = lfilter(b, a, audio)
        return audio + warm * amount
    
    def _add_reverb(self, audio, sr, amount):
        """Add simple reverb effect"""
        delay_samples = int(0.1 * sr)
        reverb = np.zeros(len(audio) + delay_samples)
        reverb[:len(audio)] = audio
        reverb[delay_samples:] += audio * 0.3 * amount
        return reverb[:len(audio)]
    
    def _add_compression(self, audio, amount):
        """Add compression"""
        threshold = 0.5 * amount
        ratio = 3 * amount
        audio_compressed = audio.copy()
        
        for i, sample in enumerate(audio):
            if abs(sample) > threshold:
                audio_compressed[i] = np.sign(sample) * (threshold + (abs(sample) - threshold) / ratio)
        
        return audio_compressed
    
    def perfect_style_reproduction(self, audio_path, target_style, preserve_features=True):
        """Reproduce music style with perfection"""
        # Analyze original
        original_style = self.analyze_music_style(audio_path)
        
        # Get target style characteristics
        target_char = self.style_characteristics.get(target_style)
        if target_char is None and target_style in self.style_profiles:
            target_char = self.style_profiles[target_style]
        else:
            target_char = self.style_characteristics['pop']
        
        # Load audio
        audio, sr = librosa.load(audio_path, sr=22050)
        
        # Perfect reproduction process
        audio = self._perfect_tempo_matching(audio, sr, target_char['tempo_range'])
        audio = self._perfect_harmonic_matching(audio, sr, target_char['harmonic_complexity'])
        audio = self._perfect_instrumentation(audio, target_char['instrumentation'])
        audio = self._perfect_rhythm(audio, sr, target_char['rhythm_complexity'])
        
        if preserve_features:
            audio = self._preserve_original_features(audio, original_style)
        
        return audio
    
    def _perfect_tempo_matching(self, audio, sr, tempo_range):
        """Perfect tempo matching"""
        current_tempo = self._extract_tempo(audio, sr)
        target_tempo = np.mean(tempo_range)
        ratio = target_tempo / (current_tempo + 1e-6)
        return librosa.effects.time_stretch(audio, rate=ratio)
    
    def _perfect_harmonic_matching(self, audio, sr, harmonic_complexity):
        """Perfect harmonic matching"""
        # Extract harmonic components
        harmonic, percussive = librosa.effects.hpss(audio)
        
        # Adjust harmonic complexity
        if harmonic_complexity > 0.6:
            # Enhance harmonics
            harmonic = harmonic * 1.3
        else:
            # Reduce harmonics
            harmonic = harmonic * 0.7
        
        return harmonic + percussive
    
    def _perfect_instrumentation(self, audio, instruments):
        """Perfect instrumentation matching"""
        # In production, use instrument-specific processing
        # This is a simplified version
        if 'drums' in instruments:
            # Enhance percussive elements
            _, percussive = librosa.effects.hpss(audio)
            audio = audio + percussive * 0.3
        
        if 'bass' in instruments:
            # Enhance low frequencies
            b, a = butter(2, 200/(22050/2), btype='low')
            bass = lfilter(b, a, audio)
            audio = audio + bass * 0.2
        
        return audio
    
    def _perfect_rhythm(self, audio, sr, rhythm_complexity):
        """Perfect rhythm matching"""
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        
        if rhythm_complexity > 0.7:
            # Add rhythmic variation
            audio = audio * (1 + 0.1 * np.sin(2 * np.pi * 4 * np.linspace(0, 1, len(audio))))
        
        return audio
    
    def _preserve_original_features(self, audio, original_style):
        """Preserve original features while applying style"""
        # Extract original characteristics
        original_energy = original_style['energy']
        
        # Maintain original energy level
        current_energy = self._extract_energy(audio)
        energy_ratio = original_energy / (current_energy + 1e-6)
        audio = audio * np.sqrt(energy_ratio)
        
        return audio
    
    def get_available_styles(self):
        """Get list of available styles"""
        styles = list(self.style_characteristics.keys())
        styles.extend(self.style_profiles.keys())
        return list(set(styles))
