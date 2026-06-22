import librosa
import numpy as np
import soundfile as sf
from pydub import AudioSegment
import os
import tempfile

class AudioProcessor:
    def __init__(self, config):
        self.config = config
        self.audio_data = None
        self.sample_rate = None

    def load_audio(self, file_path):
        """Load any audio (MP3, WAV, etc.) using pydub + ffmpeg, then convert to WAV for librosa."""
        try:
            # Use pydub to load (handles MP3 via ffmpeg)
            audio = AudioSegment.from_file(file_path)
            # Convert to mono, set sample rate
            audio = audio.set_channels(1).set_frame_rate(self.config.SAMPLE_RATE)
            # Export to temporary WAV
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
            audio.export(tmp_path, format='wav')
            # Now load with soundfile (librosa will use soundfile backend)
            self.audio_data, self.sample_rate = sf.read(tmp_path)
            # Clean up temp file
            os.unlink(tmp_path)
            return True
        except Exception as e:
            raise ValueError(f"Failed to load audio: {str(e)}")

    def extract_features(self):
        """Extract comprehensive audio features"""
        if self.audio_data is None:
            raise ValueError("No audio loaded")
            
        features = {
            'tempo': self._get_tempo(),
            'beats': self._get_beats(),
            'energy': self._get_energy(),
            'chroma': self._get_chroma(),
            'mel_spectrogram': self._get_mel_spectrogram(),
            'mfcc': self._get_mfcc(),
            'harmonic': self._get_harmonic(),
            'percussive': self._get_percussive()
        }
        return features

    def _get_tempo(self):
        tempo, _ = librosa.beat.beat_track(
            y=self.audio_data, 
            sr=self.sample_rate
        )
        return float(tempo)
    
    def _get_beats(self):
        tempo, beat_frames = librosa.beat.beat_track(
            y=self.audio_data, 
            sr=self.sample_rate
        )
        beat_times = librosa.frames_to_time(beat_frames, sr=self.sample_rate)
        return beat_times.tolist()
    
    def _get_energy(self):
        energy = np.sum(self.audio_data**2) / len(self.audio_data)
        return float(energy)
    
    def _get_chroma(self):
        chroma = librosa.feature.chroma_stft(
            y=self.audio_data, 
            sr=self.sample_rate
        )
        return chroma.mean(axis=1).tolist()
    
    def _get_mel_spectrogram(self):
        mel = librosa.feature.melspectrogram(
            y=self.audio_data, 
            sr=self.sample_rate
        )
        return mel.tolist()
    
    def _get_mfcc(self):
        mfcc = librosa.feature.mfcc(
            y=self.audio_data, 
            sr=self.sample_rate, 
            n_mfcc=13
        )
        return mfcc.mean(axis=1).tolist()
    
    def _get_harmonic(self):
        harmonic, _ = librosa.effects.hpss(self.audio_data)
        return harmonic.tolist()
    
    def _get_percussive(self):
        _, percussive = librosa.effects.hpss(self.audio_data)
        return percussive.tolist()
