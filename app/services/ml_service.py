import torch
import torch.nn as nn
import numpy as np
from PIL import Image
import cv2
import os
import json
from collections import defaultdict

class MLService:
    def __init__(self, config):
        self.config = config
        self.device = torch.device('cuda' if config.USE_GPU and torch.cuda.is_available() else 'cpu')
        self.models = {}
        self.model_configs = {}
        self._load_model_configs()
    
    def _load_model_configs(self):
        """Load model configurations"""
        self.model_configs = {
            'wav2lip': {
                'path': os.path.join(self.config.MODEL_FOLDER, 'lip_sync/wav2lip_model.pth'),
                'input_size': (96, 96),
                'output_size': (96, 96)
            },
            'stylegan2': {
                'path': os.path.join(self.config.MODEL_FOLDER, 'face_generation/stylegan2.pth'),
                'input_size': (512, 512),
                'output_size': (512, 512)
            },
            'emotion': {
                'path': os.path.join(self.config.MODEL_FOLDER, 'emotion_recognition/emotion_model.pth'),
                'input_size': (224, 224),
                'num_classes': 8
            },
            'speaker_encoder': {
                'path': os.path.join(self.config.MODEL_FOLDER, 'voice_cloning/speaker_encoder.pth'),
                'embedding_dim': 256
            },
            'vocoder': {
                'path': os.path.join(self.config.MODEL_FOLDER, 'voice_cloning/vocoder.pth'),
                'upsample_rates': [8, 8, 4, 4]
            }
        }
    
    def load_model(self, model_name):
        """Load a PyTorch model"""
        if model_name in self.models:
            return self.models[model_name]
        
        config = self.model_configs.get(model_name)
        if not config:
            raise ValueError(f"Model {model_name} not configured")
        
        model_path = config.get('path')
        if not os.path.exists(model_path):
            print(f"Model {model_name} not found at {model_path}, using fallback")
            return None
        
        try:
            model = torch.load(model_path, map_location=self.device)
            model.eval()
            self.models[model_name] = model
            return model
        except Exception as e:
            print(f"Error loading model {model_name}: {str(e)}")
            return None
    
    def tensor_to_image(self, tensor):
        """Convert tensor to PIL Image"""
        if isinstance(tensor, torch.Tensor):
            tensor = tensor.cpu().detach()
            if tensor.dim() == 4:
                tensor = tensor[0]
            tensor = tensor * 0.5 + 0.5  # Denormalize
            tensor = tensor.clamp(0, 1)
            return Image.fromarray((tensor.numpy() * 255).astype(np.uint8).transpose(1, 2, 0))
        return tensor
    
    def image_to_tensor(self, image, normalize=True):
        """Convert PIL Image to tensor"""
        if isinstance(image, Image.Image):
            image = np.array(image) / 255.0
        elif isinstance(image, np.ndarray):
            image = image / 255.0
        
        tensor = torch.FloatTensor(image)
        if len(tensor.shape) == 3:
            tensor = tensor.permute(2, 0, 1)
        else:
            tensor = tensor.unsqueeze(0)
        
        if normalize:
            tensor = tensor * 2 - 1  # Normalize to [-1, 1]
        
        return tensor.unsqueeze(0).to(self.device)
    
    def process_batch(self, inputs, model_name, batch_size=4, preprocess=None, postprocess=None):
        """Process inputs in batches"""
        model = self.load_model(model_name)
        if model is None:
            return []
        
        outputs = []
        for i in range(0, len(inputs), batch_size):
            batch = inputs[i:i+batch_size]
            
            if preprocess:
                batch = [preprocess(x) for x in batch]
            
            # Convert to tensors
            if isinstance(batch[0], np.ndarray):
                batch = [self.image_to_tensor(x) for x in batch]
            
            batch_tensor = torch.cat(batch, dim=0)
            
            with torch.no_grad():
                batch_output = model(batch_tensor)
            
            if postprocess:
                batch_output = [postprocess(x) for x in batch_output]
            
            outputs.extend(batch_output)
        
        return outputs
    
    def extract_face_embedding(self, face_image):
        """Extract face embedding using model"""
        # Placeholder for face embedding extraction
        return np.random.randn(512)
    
    def extract_speaker_embedding(self, audio):
        """Extract speaker embedding"""
        model = self.load_model('speaker_encoder')
        if model is None:
            return np.random.randn(256)
        
        # Convert audio to tensor
        if isinstance(audio, np.ndarray):
            audio_tensor = torch.FloatTensor(audio).unsqueeze(0).to(self.device)
        else:
            audio_tensor = audio
        
        with torch.no_grad():
            embedding = model(audio_tensor)
        
        return embedding.cpu().numpy().flatten()
    
    def generate_face(self, embedding, resolution=512):
        """Generate face from embedding"""
        model = self.load_model('stylegan2')
        if model is None:
            # Fallback: generate random face
            return Image.new('RGB', (resolution, resolution), (200, 180, 160))
        
        # Generate face
        with torch.no_grad():
            if isinstance(embedding, np.ndarray):
                embedding = torch.FloatTensor(embedding).to(self.device)
            face_tensor = model(embedding)
        
        return self.tensor_to_image(face_tensor)
    
    def predict_emotion(self, audio_features):
        """Predict emotion from audio features"""
        model = self.load_model('emotion')
        if model is None:
            # Fallback: rule-based emotion detection
            return self._rule_based_emotion(audio_features)
        
        # Convert features to tensor
        features = torch.FloatTensor(audio_features).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = model(features)
            emotion_idx = torch.argmax(output, dim=1).item()
        
        return emotion_idx
    
    def _rule_based_emotion(self, features):
        """Rule-based emotion detection fallback"""
        tempo = features.get('tempo', 120)
        energy = features.get('energy', 0.5)
        
        if tempo > 140 and energy > 0.7:
            return 1  # Happy
        elif tempo < 80 and energy < 0.3:
            return 2  # Sad
        elif tempo > 130 and energy > 0.8:
            return 3  # Angry
        elif tempo > 110 and energy > 0.6:
            return 7  # Passionate
        else:
            return 0  # Neutral
    
    def lip_sync(self, face_frames, audio_features):
        """Generate lip sync frames"""
        model = self.load_model('wav2lip')
        if model is None:
            # Fallback: simple lip sync
            return self._simple_lip_sync(face_frames, audio_features)
        
        # Process with model
        synced_frames = []
        for frame in face_frames:
            frame_tensor = self.image_to_tensor(frame)
            audio_tensor = torch.FloatTensor(audio_features).to(self.device)
            
            with torch.no_grad():
                output = model(frame_tensor, audio_tensor)
            
            synced_frames.append(self.tensor_to_image(output))
        
        return synced_frames
    
    def _simple_lip_sync(self, frames, audio_features):
        """Simple fallback lip sync"""
        # Detect beats for mouth movement timing
        from scipy.signal import find_peaks
        amplitude = np.abs(audio_features)
        peaks, _ = find_peaks(amplitude, distance=100)
        
        synced_frames = []
        for i, frame in enumerate(frames):
            # Determine if mouth should be open
            is_open = i % 20 < 10  # Simple alternation
            
            # Modify mouth region
            frame_array = np.array(frame)
            h, w = frame_array.shape[:2]
            mouth_y = h // 2 + 30
            mouth_h = 20 if is_open else 10
            
            # Draw mouth
            cv2.ellipse(frame_array, (w//2, mouth_y), (20, mouth_h), 0, 0, 360, (50, 20, 20), -1)
            if is_open:
                cv2.ellipse(frame_array, (w//2, mouth_y + 5), (15, 10), 0, 0, 360, (30, 10, 10), -1)
            
            synced_frames.append(Image.fromarray(frame_array))
        
        return synced_frames
