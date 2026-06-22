import cv2
import numpy as np
from PIL import Image
import ffmpeg

class VideoRenderer:
    def __init__(self, config):
        self.config = config
        self.fps = config.FPS
        self.resolution = config.RESOLUTION
        
    def render_video(self, scenes, audio_path, characters, output_path):
        """Render complete video with all elements"""
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(
            output_path + '.temp.mp4',
            fourcc,
            self.fps,
            self.resolution
        )
        
        # Render each scene
        for scene in scenes:
            frames = self._render_scene(scene, characters)
            for frame in frames:
                video_writer.write(frame)
        
        video_writer.release()
        
        # Add audio
        self._add_audio(output_path + '.temp.mp4', audio_path, output_path)
        
        return True
    
    def _render_scene(self, scene, characters):
        """Render a single scene"""
        frames = []
        duration = scene['duration']
        total_frames = int(duration * self.fps)
        
        for i in range(total_frames):
            # Create frame
            frame = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
            
            # Add background
            frame = self._add_background(frame, scene['background'])
            
            # Add characters
            for character in characters:
                frame = self._add_character(frame, character, i, total_frames)
            
            # Add lighting
            frame = self._add_lighting(frame, scene['lighting'])
            
            frames.append(frame)
        
        return frames
    
    def _add_background(self, frame, background):
        """Add background to frame"""
        # Simple gradient background based on background type
        h, w = frame.shape[:2]
        
        if background['type'] == 'cityscape':
            # Create dark background with light dots
            frame = np.full((h, w, 3), [20, 20, 30], dtype=np.uint8)
            # Add random lights
            for _ in range(50):
                x = np.random.randint(0, w)
                y = np.random.randint(0, h)
                cv2.circle(frame, (x, y), 3, (200, 200, 100), -1)
        else:
            # Simple gradient
            for i in range(h):
                gradient_value = int((i / h) * 100) + 30
                frame[i, :] = [gradient_value, gradient_value, gradient_value]
        
        return frame
    
    def _add_character(self, frame, character, frame_idx, total_frames):
        """Add character to frame with animation"""
        h, w = frame.shape[:2]
        char_image = character.get('visual')
        
        if char_image:
            # Resize character
            char_image = char_image.resize((200, 400))
            char_array = np.array(char_image)
            
            # Calculate position with animation
            progress = frame_idx / total_frames
            x = int(w // 2 + np.sin(progress * 2 * np.pi) * 50 - 100)
            y = int(h - 450 - np.sin(progress * 2 * np.pi * 0.5) * 20)
            
            # Ensure character stays in frame
            x = max(0, min(x, w - 200))
            y = max(0, min(y, h - 400))
            
            # Add character to frame
            try:
                if char_array.shape[-1] == 4:  # RGBA
                    alpha = char_array[:, :, 3] / 255.0
                    for c in range(3):
                        frame[y:y+400, x:x+200, c] = (
                            frame[y:y+400, x:x+200, c] * (1 - alpha) +
                            char_array[:, :, c] * alpha
                        )
                else:
                    frame[y:y+400, x:x+200] = char_array[:, :, :3]
            except ValueError:
                pass
        
        return frame
    
    def _add_lighting(self, frame, lighting):
        """Add lighting effects to frame"""
        h, w = frame.shape[:2]
        
        if lighting['dynamic']:
            # Add dynamic lighting effect
            for i in range(h):
                for j in range(w):
                    distance = np.sqrt((j - w/2)**2 + (i - h/2)**2)
                    intensity = lighting['brightness'] * np.exp(-distance / 500)
                    frame[i, j] = frame[i, j] * (1 + intensity * 0.5)
        
        return frame
    
    def _add_audio(self, video_path, audio_path, output_path):
        """Add audio to video using ffmpeg"""
        try:
            (
                ffmpeg
                .input(video_path)
                .input(audio_path)
                .output(output_path, vcodec='libx264', acodec='aac', strict='experimental')
                .run(overwrite_output=True)
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to add audio: {str(e)}")
