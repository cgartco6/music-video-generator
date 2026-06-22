import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-2024')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # File paths
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    OUTPUT_FOLDER = os.path.join(os.getcwd(), 'outputs')
    MODEL_FOLDER = os.path.join(os.getcwd(), 'models')
    TEMP_FOLDER = os.path.join(os.getcwd(), 'temp')
    
    # Create folders if they don't exist
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, MODEL_FOLDER, TEMP_FOLDER]:
        os.makedirs(folder, exist_ok=True)
    
    # Audio settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 2048
    BEAT_THRESHOLD = 0.5
    MAX_AUDIO_DURATION = 600  # 10 minutes
    
    # Video settings
    FPS = 30
    RESOLUTION = (1920, 1080)
    BACKGROUND_COLOR = (0, 0, 0)
    VIDEO_CODEC = 'libx264'
    AUDIO_CODEC = 'aac'
    
    # ML models paths
    LIP_SYNC_MODEL = os.path.join(MODEL_FOLDER, 'lip_sync/wav2lip_model.pth')
    BEAT_MODEL = os.path.join(MODEL_FOLDER, 'beat_tracking/madmom_model.pkl')
    INSTRUMENT_MODEL = os.path.join(MODEL_FOLDER, 'instrument_recognition/instrument_classifier.pth')
    FACE_GENERATION_MODEL = os.path.join(MODEL_FOLDER, 'face_generation/stylegan2.pth')
    EMOTION_MODEL = os.path.join(MODEL_FOLDER, 'emotion_recognition/emotion_model.pth')
    STYLE_TRANSFER_MODEL = os.path.join(MODEL_FOLDER, 'style_transfer/pretrained.pth')
    
    # Character settings
    AVAILABLE_CHARACTERS = ['male_singer', 'female_singer', 'band_member', 'dancer']
    AVAILABLE_INSTRUMENTS = ['guitar', 'drums', 'keyboard', 'bass', 'violin', 'piano']
    AVAILABLE_HAIRSTYLES = ['long', 'short', 'curly', 'straight', 'ponytail', 'bun']
    AVAILABLE_OUTFITS = ['casual', 'formal', 'rock', 'pop', 'classic', 'modern']
    AVAILABLE_COLORS = ['#FF0000', '#00FF00', '#0000FF', '#FFD700', '#FF69B4', '#00CED1']
    
    # AI Enhancement settings
    ENABLE_SUPER_RESOLUTION = True
    ENABLE_COLOR_GRADING = True
    ENABLE_FACE_ENHANCEMENT = True
    ENABLE_REAL_TIME_PREVIEW = True
    ENABLE_EMOTION_DRIVEN = True
    ENABLE_STYLE_TRANSFER = True
    
    # Performance settings
    USE_GPU = os.getenv('USE_GPU', 'True') == 'True'
    BATCH_SIZE = 4
    MAX_WORKERS = 4
    
    # API settings
    API_RATE_LIMIT = 100  # requests per hour
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Redis settings (for production)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
