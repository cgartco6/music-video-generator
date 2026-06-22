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
        """Load any audio using pydub + ffmpeg, then convert to WAV."""
        try:
            audio = AudioSegment.from_file(file_path)
            audio = audio.set_channels(1).set_frame_rate(self.config.SAMPLE_RATE)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
            audio.export(tmp_path, format='wav')
            self.audio_data, self.sample_rate = sf.read(tmp_path)
            os.unlink(tmp_path)
            return True
        except Exception as e:
            raise ValueError(f"Failed to load audio: {str(e)}")

    def extract_features(self):
        if self.audio_data is None:
            raise ValueError("No audio loaded")
        features = {
            'tempo': self._get_tempo(),
            'beats': self._get_beats(),
            'energy': self._get_energy(),
            'chroma': self._get_chroma(),
            'mfcc': self._get_mfcc(),
            'harmonic': self._get_harmonic(),
            'percussive': self._get_percussive()
        }
        return features

    def _get_tempo(self):
        tempo, _ = librosa.beat.beat_track(y=self.audio_data, sr=self.sample_rate)
        return float(tempo)
    
    def _get_beats(self):
        _, beat_frames = librosa.beat.beat_track(y=self.audio_data, sr=self.sample_rate)
        return librosa.frames_to_time(beat_frames, sr=self.sample_rate).tolist()
    
    def _get_energy(self):
        return float(np.sum(self.audio_data**2) / len(self.audio_data))
    
    def _get_chroma(self):
        chroma = librosa.feature.chroma_stft(y=self.audio_data, sr=self.sample_rate)
        return chroma.mean(axis=1).tolist()
    
    def _get_mfcc(self):
        mfcc = librosa.feature.mfcc(y=self.audio_data, sr=self.sample_rate, n_mfcc=13)
        return mfcc.mean(axis=1).tolist()
    
    def _get_harmonic(self):
        harmonic, _ = librosa.effects.hpss(self.audio_data)
        return harmonic.tolist()
    
    def _get_percussive(self):
        _, percussive = librosa.effects.hpss(self.audio_data)
        return percussive.tolist()
