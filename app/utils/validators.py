import re
import os
from datetime import datetime

class Validator:
    @staticmethod
    def validate_audio_file(filename):
        """Validate audio file extension"""
        allowed = {'mp3', 'wav', 'flac', 'm4a', 'aac', 'ogg', 'wma', 'mp4'}
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in allowed
    
    @staticmethod
    def validate_voice_name(name):
        """Validate voice name"""
        if not name or len(name) < 2 or len(name) > 50:
            return False
        return re.match(r'^[a-zA-Z0-9_\s-]+$', name) is not None
    
    @staticmethod
    def validate_style_name(name):
        """Validate style name"""
        if not name or len(name) < 2 or len(name) > 50:
            return False
        return re.match(r'^[a-zA-Z0-9_\s-]+$', name) is not None
    
    @staticmethod
    def validate_job_id(job_id):
        """Validate job ID format"""
        return re.match(r'^[a-f0-9-]{36}$', job_id) is not None
    
    @staticmethod
    def validate_email(email):
        """Validate email address"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_url(url):
        """Validate URL"""
        pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def validate_audio_features(features):
        """Validate audio features dictionary"""
        required_keys = ['tempo', 'energy', 'mfcc']
        for key in required_keys:
            if key not in features:
                return False
        return True
    
    @staticmethod
    def validate_character_data(data):
        """Validate character data"""
        required_keys = ['type', 'name']
        for key in required_keys:
            if key not in data:
                return False
        
        valid_types = ['male_singer', 'female_singer', 'band_member', 'dancer']
        if data['type'] not in valid_types:
            return False
        
        return True
    
    @staticmethod
    def validate_scene_data(data):
        """Validate scene data"""
        required_keys = ['duration', 'characters', 'background']
        for key in required_keys:
            if key not in data:
                return False
        
        if not isinstance(data['duration'], (int, float)) or data['duration'] <= 0:
            return False
        
        if not isinstance(data['characters'], list) or len(data['characters']) == 0:
            return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename"""
        # Remove any path components
        filename = os.path.basename(filename)
        # Remove any non-alphanumeric characters except dots, dashes, underscores
        return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    
    @staticmethod
    def validate_resolution(width, height):
        """Validate video resolution"""
        valid_resolutions = [
            (1920, 1080), (1280, 720), (854, 480), (640, 360),
            (3840, 2160), (2560, 1440)
        ]
        return (width, height) in valid_resolutions
    
    @staticmethod
    def validate_fps(fps):
        """Validate FPS"""
        valid_fps = [23.976, 24, 25, 29.97, 30, 50, 60, 120]
        return fps in valid_fps or 1 <= fps <= 120
    
    @staticmethod
    def validate_audio_sample_rate(sr):
        """Validate audio sample rate"""
        valid_sr = [8000, 11025, 16000, 22050, 24000, 32000, 44100, 48000]
        return sr in valid_sr
    
    @staticmethod
    def validate_emotion(emotion):
        """Validate emotion"""
        valid_emotions = [
            'neutral', 'happy', 'sad', 'angry', 'surprised',
            'fear', 'disgust', 'passionate', 'romantic',
            'energetic', 'calm', 'melancholic', 'triumphant'
        ]
        return emotion in valid_emotions
    
    @staticmethod
    def validate_instrument(instrument):
        """Validate instrument"""
        valid_instruments = [
            'guitar', 'drums', 'keyboard', 'bass', 'violin',
            'piano', 'saxophone', 'trumpet', 'flute', 'synth'
        ]
        return instrument in valid_instruments
    
    @staticmethod
    def validate_duration(duration_seconds):
        """Validate duration in seconds"""
        return isinstance(duration_seconds, (int, float)) and 0 < duration_seconds <= 600

**models/lip_sync/face_detection.py**
```python
import cv2
import numpy as np
import dlib
from PIL import Image

class FaceDetection:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
        
    def detect_faces(self, image):
        """Detect faces in image"""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        faces = self.detector(gray, 1)
        return faces
    
    def get_face_landmarks(self, image, face):
        """Get facial landmarks"""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        landmarks = self.predictor(gray, face)
        return landmarks
    
    def get_landmark_points(self, landmarks):
        """Get landmark points as numpy array"""
        points = []
        for i in range(68):
            x = landmarks.part(i).x
            y = landmarks.part(i).y
            points.append((x, y))
        return np.array(points)
    
    def crop_face(self, image, face, padding=20):
        """Crop face from image"""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        x = max(0, face.left() - padding)
        y = max(0, face.top() - padding)
        w = min(image.shape[1] - x, face.width() + padding * 2)
        h = min(image.shape[0] - y, face.height() + padding * 2)
        
        return image[y:y+h, x:x+w]
    
    def get_face_region(self, image, face):
        """Get face region coordinates"""
        return {
            'x': face.left(),
            'y': face.top(),
            'width': face.width(),
            'height': face.height()
        }
    
    def draw_landmarks(self, image, landmarks):
        """Draw landmarks on image"""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        for i in range(68):
            x = landmarks.part(i).x
            y = landmarks.part(i).y
            cv2.circle(image, (x, y), 2, (0, 255,
