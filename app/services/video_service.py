import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import ffmpeg
import os
import subprocess

class VideoService:
    def __init__(self, config):
        self.config = config
        self.fps = config.FPS
        self.resolution = config.RESOLUTION
        self.video_codec = config.VIDEO_CODEC
        self.audio_codec = config.AUDIO_CODEC
    
    def create_video_writer(self, output_path, fps=None, resolution=None):
        """Create video writer"""
        if fps is None:
            fps = self.fps
        if resolution is None:
            resolution = self.resolution
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            resolution
        )
        return writer
    
    def add_audio(self, video_path, audio_path, output_path):
        """Add audio to video using ffmpeg"""
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-strict', 'experimental',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                '-y',
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to add audio: {e.stderr.decode()}")
        except Exception as e:
            raise RuntimeError(f"Failed to add audio: {str(e)}")
    
    def extract_frames(self, video_path, max_frames=None):
        """Extract frames from video"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            frame_count += 1
            if max_frames and frame_count >= max_frames:
                break
        
        cap.release()
        return frames
    
    def create_video_from_frames(self, frames, output_path, audio_path=None, fps=None):
        """Create video from frames"""
        if fps is None:
            fps = self.fps
        
        temp_path = output_path + '.temp.mp4'
        writer = self.create_video_writer(temp_path, fps)
        
        for frame in frames:
            if isinstance(frame, Image.Image):
                frame = np.array(frame)
                if len(frame.shape) == 3 and frame.shape[2] == 4:
                    frame = frame[:, :, :3]
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            elif isinstance(frame, np.ndarray):
                if len(frame.shape) == 3 and frame.shape[2] == 4:
                    frame = frame[:, :, :3]
            
            writer.write(frame)
        
        writer.release()
        
        if audio_path and os.path.exists(audio_path):
            self.add_audio(temp_path, audio_path, output_path)
            os.remove(temp_path)
        else:
            os.rename(temp_path, output_path)
        
        return output_path
    
    def add_text_overlay(self, video_path, text_data, output_path):
        """Add text overlay to video"""
        try:
            cmd = ['ffmpeg', '-i', video_path]
            
            for text in text_data:
                font_file = text.get('font', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
                cmd.extend([
                    '-vf', f"drawtext=text='{text['content']}':x={text.get('x', 10)}:y={text.get('y', 10)}:fontsize={text.get('size', 24)}:fontcolor={text.get('color', 'white')}:fontfile={font_file}"
                ])
            
            cmd.extend(['-c:a', 'copy', '-y', output_path])
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to add text overlay: {str(e)}")
    
    def resize_video(self, input_path, output_path, resolution=None):
        """Resize video"""
        if resolution is None:
            resolution = self.resolution
        
        try:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vf', f'scale={resolution[0]}:{resolution[1]}',
                '-c:a', 'copy',
                '-y',
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to resize video: {str(e)}")
    
    def apply_transition(self, frame1, frame2, transition_type='fade', progress=0.5):
        """Apply transition between two frames"""
        if transition_type == 'fade':
            alpha = progress
            return cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)
        elif transition_type == 'wipe':
            h, w = frame1.shape[:2]
            cut_x = int(w * progress)
            result = frame2.copy()
            result[:, :cut_x] = frame1[:, :cut_x]
            return result
        elif transition_type == 'slide':
            h, w = frame1.shape[:2]
            shift = int(w * progress)
            result = np.zeros_like(frame1)
            result[:, :w-shift] = frame1[:, shift:]
            result[:, w-shift:] = frame2[:, :shift]
            return result
        else:
            return frame1
    
    def get_video_info(self, video_path):
        """Get video information"""
        cap = cv2.VideoCapture(video_path)
        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }
        cap.release()
        return info
