import pytest
import numpy as np
from app.models.beat_detector import BeatDetector

class TestBeatDetector:
    @pytest.fixture
    def beat_detector(self):
        config = type('Config', (), {'SAMPLE_RATE': 22050})()
        return BeatDetector(config)

    def test_detect_beats_simple(self, beat_detector):
        # Generate a simple audio signal with beats
        sr = 22050
        duration = 5  # seconds
        t = np.linspace(0, duration, int(sr * duration))
        # Create a click track at 120 BPM (2 beats per second)
        beat_interval = 0.5  # seconds
        signal = np.zeros_like(t)
        for i in range(int(duration / beat_interval)):
            idx = int(i * beat_interval * sr)
            if idx < len(signal):
                signal[idx:idx+100] = 1.0
        # Add some noise
        signal += 0.1 * np.random.randn(len(signal))
        
        result = beat_detector.detect_beats(signal, sr)
        assert 'tempo' in result
        assert 'beat_times' in result
        assert len(result['beat_times']) > 0
        # Check that detected tempo is close to 120
        assert abs(result['tempo'] - 120) < 10

    def test_get_downbeats(self, beat_detector):
        sr = 22050
        duration = 4
        t = np.linspace(0, duration, int(sr * duration))
        signal = np.zeros_like(t)
        for i in range(8):  # 2 beats per second
            idx = int(i * 0.5 * sr)
            signal[idx:idx+100] = 1.0
        beat_detector.detect_beats(signal, sr)
        downbeats = beat_detector.get_downbeats()
        # In 4/4, downbeats at 0, 2, 4 seconds
        expected = [0.0, 2.0, 4.0]
        for d in downbeats:
            assert any(abs(d - e) < 0.05 for e in expected)

    def test_beat_intensity(self, beat_detector):
        sr = 22050
        duration = 2
        t = np.linspace(0, duration, int(sr * duration))
        # Varying intensity
        signal = np.sin(2 * np.pi * 440 * t) * (1 + 0.5 * np.sin(2 * np.pi * 2 * t))
        intensity = beat_detector.get_beat_intensity(signal, sr)
        assert len(intensity) > 0
        assert all(0 <= i <= 1 for i in intensity)
