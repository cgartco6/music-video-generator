import pytest
import numpy as np
from app.models.video_renderer import VideoRenderer
import os
import tempfile

class TestVideoRenderer:
    @pytest.fixture
    def renderer(self):
        config = type('Config', (), {
            'FPS': 30,
            'RESOLUTION': (640, 480),
            'OUTPUT_FOLDER': tempfile.mkdtemp()
        })()
        return VideoRenderer(config)

    def test_render_video(self, renderer):
        # Create dummy scenes
        scenes = [
            {
                'duration': 1.0,
                'background': {'type': 'cityscape'},
                'lighting': {'dynamic': False, 'brightness': 0.5},
                'characters': []
            }
        ]
        # Create dummy audio file
        audio_path = tempfile.mktemp(suffix='.wav')
        import soundfile as sf
        sf.write(audio_path, np.random.randn(16000), 16000)
        
        output_path = tempfile.mktemp(suffix='.mp4')
        characters = []
        result = renderer.render_video(scenes, audio_path, characters, output_path)
        assert result is True
        assert os.path.exists(output_path)
        # Cleanup
        os.remove(audio_path)
        os.remove(output_path)
