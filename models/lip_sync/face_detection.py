import cv2
import numpy as np
import dlib

class FaceDetection:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
    
    def detect_faces(self, image):
        """Detect faces in image"""
        if isinstance(image, np.ndarray):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = np.array(image.convert('L'))
        
        faces = self.detector(gray)
        return faces
    
    def get_face_landmarks(self, image, face):
        """Get facial landmarks"""
        if isinstance(image, np.ndarray):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = np.array(image.convert('L'))
        
        landmarks = self.predictor(gray, face)
        return landmarks
    
    def crop_face(self, image, face, padding=20):
        """Crop face from image"""
        x = face.left() - padding
        y = face.top() - padding
        w = face.width() + padding * 2
        h = face.height() + padding * 2
        
        if isinstance(image, np.ndarray):
            return image[y:y+h, x:x+w]
        else:
            return image.crop((x, y, x+w, y+h))
