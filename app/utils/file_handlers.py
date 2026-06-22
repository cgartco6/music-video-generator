import os
import uuid
import shutil
import hashlib
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

class FileHandler:
    def __init__(self, config):
        self.config = config
        self.allowed_extensions = {'mp3', 'wav', 'flac', 'm4a', 'mp4', 'aac', 'ogg', 'wma'}
        self.max_file_size = config.MAX_FILE_SIZE
    
    def validate_extension(self, filename):
        """Validate file extension"""
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in self.allowed_extensions
    
    def validate_file_size(self, file):
        """Validate file size"""
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        return size <= self.max_file_size
    
    def save_file(self, file, upload_folder, subfolder=None):
        """Save uploaded file"""
        if not self.validate_extension(file.filename):
            raise ValueError(f"Invalid file type. Allowed: {', '.join(self.allowed_extensions)}")
        
        if not self.validate_file_size(file):
            raise ValueError(f"File size exceeds {self.max_file_size / (1024*1024):.0f}MB limit")
        
        # Create upload folder if it doesn't exist
        if subfolder:
            upload_folder = os.path.join(upload_folder, subfolder)
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        unique_filename = f"{file_id}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Save file
        file.save(file_path)
        
        return {
            'file_id': file_id,
            'filename': filename,
            'unique_filename': unique_filename,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'extension': filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        }
    
    def delete_file(self, file_path):
        """Delete file"""
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    def get_file_info(self, file_path):
        """Get file information"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': os.path.splitext(file_path)[1][1:].lower()
        }
    
    def get_file_hash(self, file_path, algorithm='md5'):
        """Get file hash"""
        hash_func = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    def copy_file(self, source_path, dest_path):
        """Copy file"""
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(source_path, dest_path)
        return dest_path
    
    def move_file(self, source_path, dest_path):
        """Move file"""
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.move(source_path, dest_path)
        return dest_path
    
    def cleanup_old_files(self, folder, max_age_hours=24):
        """Clean up old files in folder"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        deleted_count = 0
        
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mtime < cutoff_time:
                    os.remove(file_path)
                    deleted_count += 1
        
        return deleted_count
    
    def get_audio_duration(self, file_path):
        """Get audio duration using librosa"""
        import librosa
        try:
            duration = librosa.get_duration(filename=file_path)
            return duration
        except:
            return 0
    
    def normalize_filename(self, filename):
        """Normalize filename"""
        # Remove any path components
        filename = os.path.basename(filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Remove any non-alphanumeric characters
        import re
        return re.sub(r'[^a-zA-Z0-9_.-]', '', filename)
