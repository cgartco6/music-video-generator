import pytest
import numpy as np
from PIL import Image
from app.models.lip_sync_engine import LipSyncEngine

class TestLipSyncEngine:
    @pytest.fixture
    def engine(self):
        config = type('Config', (), {'SAMPLE_RATE': 16000})()
        return LipSyncEngine(config)

    def test_process_audio_for_lip_sync(self, engine):
        # Create a simple audio with silence and some speech-like noise
        sr = 16000
        duration = 1
        audio = np.random.randn(int(sr * duration)) * 0.1
        # Add some voiced segments
        audio[1000:2000] = 0.5
        audio[5000:6000] = 0.3
        result = engine.process_audio_for_lip_sync(audio, sr)
        assert 'viseme_sequence' in result
        assert 'times' in result
        assert 'mouth_shapes' in result
        assert len(result['viseme_sequence']) > 0

    def test_render_lip_sync(self, engine):
        # Create dummy face image
        face = Image.new('RGB', (100, 100), color='white')
        mouth_shapes = [[0.5, 0.3, 0.2, 0.1, 0.0], [0.0, 0.5, 0.3, 0.2, 0.1]]
        times = [0.0, 0.5]
        frames = engine.render_lip_sync(face, mouth_shapes, times)
        assert len(frames) > 0
        assert isinstance(frames[0], Image.Image)
