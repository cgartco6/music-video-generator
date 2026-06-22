# generate_models.py
import torch
import torch.nn as nn
import os

# Define minimal model architectures for each component
def create_dummy_model(path, model_class):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    model = model_class()
    torch.save(model.state_dict(), path)

# ============= LIP SYNC =============
class Wav2LipDummy(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 16, 3, padding=1)
    def forward(self, x, audio): return x
create_dummy_model('models/lip_sync/wav2lip_model.pth', Wav2LipDummy)

# ============= BEAT TRACKING =============
# Madmom uses built-in models, just create empty .pkl placeholder
with open('models/beat_tracking/madmom_model.pkl', 'w') as f:
    f.write('madmom placeholder – use built-in models')
# And the tempo estimator is already a Python file, so we just ensure folder exists

# ============= INSTRUMENT RECOGNITION =============
class InstDummy(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(128, 10)
    def forward(self, x): return self.fc(x)
create_dummy_model('models/instrument_recognition/instrument_classifier.pth', InstDummy)

# ============= FACE GENERATION =============
class StyleGAN2Dummy(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(512, 512*4*4)
    def forward(self, z): return z
create_dummy_model('models/face_generation/stylegan2.pth', StyleGAN2Dummy)

# ============= EMOTION =============
class EmotionDummy(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(512, 8)
    def forward(self, x): return self.fc(x)
create_dummy_model('models/emotion_recognition/emotion_model.pth', EmotionDummy)

# ============= VOICE CLONING =============
class SVCDummy(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv1d(80, 80, 1)
    def forward(self, x): return x
create_dummy_model('models/voice_cloning/svc_model.pth', SVCDummy)

class SpeakerEncoderDummy(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(40*128, 256)
    def forward(self, x): return self.fc(x.view(x.size(0), -1))
create_dummy_model('models/voice_cloning/speaker_encoder.pth', SpeakerEncoderDummy)

class VocoderDummy(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv1d(80, 1, 1)
    def forward(self, x): return self.conv(x)
create_dummy_model('models/voice_cloning/vocode.pth', VocoderDummy)

# ============= MUSIC STYLE =============
class StyleModelDummy(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(512, 10)
    def forward(self, x): return self.fc(x)
create_dummy_model('models/music_style/style_model.pth', StyleModelDummy)

class GenreClassifierDummy(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(1, 10, 1)
    def forward(self, x): return self.conv(x)
create_dummy_model('models/music_style/genre_classifier.pt', GenreClassifierDummy)

print("✅ All dummy .pth / .pkl files created.")
