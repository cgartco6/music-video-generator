import numpy as np
import cv2
from scipy.spatial import Delaunay

class FaceMorphing:
    def __init__(self):
        self.landmark_indices = list(range(68))  # 68 facial landmarks
    
    def morph_faces(self, face1, face2, alpha=0.5, landmarks1=None, landmarks2=None):
        """Morph between two faces"""
        if landmarks1 is None or landmarks2 is None:
            # Detect landmarks
            from models.lip_sync.face_detection import FaceDetection
            detector = FaceDetection()
            landmarks1 = detector.get_face_landmarks(face1)
            landmarks2 = detector.get_face_landmarks(face2)
        
        # Convert to numpy arrays
        pts1 = np.array([(p.x, p.y) for p in landmarks1.parts()])
        pts2 = np.array([(p.x, p.y) for p in landmarks2.parts()])
        
        # Interpolate points
        pts = (1 - alpha) * pts1 + alpha * pts2
        
        # Warp images
        warped1 = self.warp_image(face1, pts1, pts)
        warped2 = self.warp_image(face2, pts2, pts)
        
        # Blend images
        morphed = (1 - alpha) * warped1 + alpha * warped2
        
        return morphed.astype(np.uint8)
    
    def warp_image(self, image, src_pts, dst_pts):
        """Warp image using Delaunay triangulation"""
        # Convert to numpy if PIL
        if hasattr(image, 'convert'):
            image = np.array(image.convert('RGB'))
        
        h, w = image.shape[:2]
        rect = (0, 0, w, h)
        
        # Delaunay triangulation
        tri = Delaunay(dst_pts)
        
        warped = np.zeros_like(image)
        
        for simplex in tri.simplices:
            # Get triangle vertices
            dst_tri = dst_pts[simplex]
            src_tri = src_pts[simplex]
            
            # Get bounding box
            xmin = int(min(dst_tri[:, 0]))
            xmax = int(max(dst_tri[:, 0]))
            ymin = int(min(dst_tri[:, 1]))
            ymax = int(max(dst_tri[:, 1]))
            
            # Apply affine transformation
            transform = cv2.getAffineTransform(
                src_tri.astype(np.float32),
                dst_tri.astype(np.float32)
            )
            
            # Warp triangle
            tri_img = cv2.warpAffine(
                image,
                transform,
                (w, h),
                borderMode=cv2.BORDER_REFLECT_101
            )
            
            # Mask for triangle
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.fillConvexPoly(mask, dst_tri.astype(np.int32), 255)
            
            # Apply mask
            warped[mask > 0] = tri_img[mask > 0]
        
        return warped
