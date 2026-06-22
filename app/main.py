from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import uuid
import threading
import time
from werkzeug.utils import secure_filename
from app.config import Config
from app.models import *

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize all models
audio_processor = AudioProcessor(app.config)
beat_detector = BeatDetector(app.config)
character_generator = CharacterGenerator(app.config)
lip_sync_engine = LipSyncEngine(app.config)
instrument_simulator = InstrumentSimulator(app.config)
scene_composer = SceneComposer(app.config)
video_renderer = VideoRenderer(app.config)
face_generator = FaceGenerator(app.config)
emotion_analyzer = EmotionAnalyzer(app.config)
style_transfer = StyleTransfer(app.config)
video_enhancer = VideoEnhancer(app.config)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

# Store active jobs
active_jobs = {}

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_audio():
    """Upload audio file for processing"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file size
    if len(file.read()) > app.config['MAX_FILE_SIZE']:
        return jsonify({'error': 'File size exceeds maximum limit (50MB)'}), 400
    file.seek(0)
    
    # Save file
    filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
    file.save(file_path)
    
    # Process audio
    try:
        audio_processor.load_audio(file_path)
        features = audio_processor.extract_features()
        
        # Analyze emotion
        emotion_data = emotion_analyzer.analyze_audio_emotion(
            audio_processor.audio_data,
            audio_processor.sample_rate
        )
        
        return jsonify({
            'file_id': file_id,
            'filename': filename,
            'features': features,
            'emotion': emotion_data['primary_emotion'],
            'emotion_intensity': emotion_data['intensity'],
            'emotion_progression': emotion_data['progression']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_audio():
    """Process audio and generate video with all enhancements"""
    data = request.json
    file_id = data.get('file_id')
    character_settings = data.get('characters', {})
    enhancement_settings = data.get('enhancements', {})
    
    if not file_id:
        return jsonify({'error': 'No file ID provided'}), 400
    
    # Find uploaded file
    upload_dir = app.config['UPLOAD_FOLDER']
    files = os.listdir(upload_dir)
    audio_file = None
    for f in files:
        if f.startswith(file_id):
            audio_file = os.path.join(upload_dir, f)
            break
    
    if not audio_file:
        return jsonify({'error': 'Audio file not found'}), 404
    
    # Start processing in background
    job_id = str(uuid.uuid4())
    active_jobs[job_id] = {
        'status': 'processing',
        'progress': 0,
        'file_id': file_id
    }
    
    def process_video():
        try:
            # Update progress
            def update_progress(progress, message=''):
                active_jobs[job_id]['progress'] = progress
                socketio.emit('progress_update', {
                    'job_id': job_id,
                    'progress': progress,
                    'message': message
                })
            
            update_progress(10, 'Loading audio...')
            
            # Process audio
            audio_processor.load_audio(audio_file)
            audio_features = audio_processor.extract_features()
            
            update_progress(20, 'Detecting beats...')
            
            # Detect beats
            beat_data = beat_detector.detect_beats(
                audio_processor.audio_data,
                audio_processor.sample_rate
            )
            
            update_progress(30, 'Analyzing emotions...')
            
            # Analyze emotion
            emotion_data = emotion_analyzer.analyze_audio_emotion(
                audio_processor.audio_data,
                audio_processor.sample_rate
            )
            
            update_progress(40, 'Detecting instruments...')
            
            # Detect instruments
            instrument_data = instrument_simulator.detect_instruments(
                audio_processor.audio_data,
                audio_processor.sample_rate
            )
            
            update_progress(50, 'Generating characters...')
            
            # Generate characters with faces
            characters = []
            for char_type in character_settings.get('types', ['male_singer']):
                # Generate base character
                char = character_generator.generate_character(
                    char_type,
                    instrument_data['instruments'][0] if instrument_data['instruments'] else None
                )
                
                # Generate realistic face
                gender = 'male' if 'male' in char_type else 'female'
                face = face_generator.generate_face(
                    gender=gender,
                    age=30,
                    expression='neutral',
                    hairstyle=character_settings.get('hairstyle', 'medium'),
                    ethnicity=character_settings.get('ethnicity', 'caucasian')
                )
                char['face'] = face
                char['visual'] = character_generator.create_character_visual(char)
                characters.append(char)
            
            update_progress(60, 'Generating lip sync...')
            
            # Generate lip sync
            lip_sync_data = lip_sync_engine.process_audio_for_lip_sync(
                audio_processor.audio_data,
                audio_processor.sample_rate
            )
            
            update_progress(70, 'Composing scenes...')
            
            # Compose scenes with emotion awareness
            scenes = scene_composer.compose_scenes(
                audio_features,
                characters,
                beat_data['beat_times'],
                emotion_data
            )
            
            update_progress(80, 'Rendering video...')
            
            # Render video
            output_filename = f"{file_id}_output.mp4"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            video_renderer.render_video(
                scenes,
                audio_file,
                characters,
                output_path,
                progress_callback=lambda p: update_progress(80 + p * 0.15, f'Rendering... {p:.1f}%')
            )
            
            update_progress(95, 'Enhancing video...')
            
            # Apply enhancements if enabled
            if enhancement_settings.get('style_transfer', True):
                # Read rendered video frames and apply style
                genre = enhancement_settings.get('genre', 'pop')
                # Note: Full implementation would process frames here
                # This is a placeholder for the enhancement step
            
            if enhancement_settings.get('color_grading', True):
                # Apply color grading
                style = enhancement_settings.get('color_style', 'cinematic')
                # Note: Full implementation would process frames here
            
            update_progress(100, 'Video generation complete!')
            
            active_jobs[job_id]['status'] = 'complete'
            active_jobs[job_id]['output_file'] = output_filename
            
            socketio.emit('job_complete', {
                'job_id': job_id,
                'video_url': f"/api/download/{output_filename}"
            })
            
        except Exception as e:
            active_jobs[job_id]['status'] = 'error'
            active_jobs[job_id]['error'] = str(e)
            socketio.emit('job_error', {
                'job_id': job_id,
                'error': str(e)
            })
    
    # Start background thread
    thread = threading.Thread(target=process_video)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'status': 'processing'
    }), 202

@app.route('/api/status/<job_id>')
def get_status(job_id):
    """Get job status"""
    job = active_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job), 200

@app.route('/api/download/<filename>')
def download_video(filename):
    """Download generated video"""
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'Video not found'}), 404
    
    return send_file(file_path, as_attachment=True)

@app.route('/api/preview/<job_id>')
def preview_video(job_id):
    """Stream preview of video during generation"""
    # Placeholder - full implementation would stream frames
    return jsonify({'status': 'preview not available'}), 501

@app.route('/api/characters', methods=['GET'])
def get_characters():
    """Get available characters and customization options"""
    return jsonify({
        'types': app.config['AVAILABLE_CHARACTERS'],
        'instruments': app.config['AVAILABLE_INSTRUMENTS'],
        'hairstyles': app.config['AVAILABLE_HAIRSTYLES'],
        'outfits': app.config['AVAILABLE_OUTFITS'],
        'colors': app.config['AVAILABLE_COLORS']
    })

@app.route('/api/emotions', methods=['GET'])
def get_emotions():
    """Get available emotions"""
    return jsonify({
        'emotions': list(emotion_analyzer.emotion_mapping.keys()),
        'intensity_range': [0.0, 1.0]
    })

@app.route('/api/genres', methods=['GET'])
def get_genres():
    """Get available music genres for style transfer"""
    return jsonify({
        'genres': list(style_transfer.genre_styles.keys()),
        'styles': list(style_transfer.genre_styles.values())
    })

@app.route('/api/enhancement_presets', methods=['GET'])
def get_enhancement_presets():
    """Get available enhancement presets"""
    return jsonify({
        'presets': list(video_enhancer.enhancement_presets.keys())
    })

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
