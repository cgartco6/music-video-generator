# create_vocoder.py
import torch
import torch.nn as nn

class Vocoder(nn.Module):
    def __init__(self):
        super().__init__()
        # Simple HiFi-GAN-like generator
        self.conv1 = nn.Conv1d(80, 512, 7, padding=3)
        self.conv2 = nn.Conv1d(512, 512, 7, padding=3)
        self.conv3 = nn.Conv1d(512, 1, 7, padding=3)
        self.lrelu = nn.LeakyReLU(0.2)

    def forward(self, x):
        x = self.lrelu(self.conv1(x))
        x = self.lrelu(self.conv2(x))
        return torch.tanh(self.conv3(x))

model = Vocoder()
torch.save(model.state_dict(), 'models/voice_cloning/vocode.pth')  # or vocoder.pth
