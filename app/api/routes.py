from flask import request, jsonify, send_file, current_app
from app.api import api_bp
from app.models import *
import os
import uuid
import threading
import time
from werkzeug.utils import secure_filename

# Initialize models
audio_processor = None
beat_detector = None
character_generator = None
lip_sync_engine = None
instrument_simulator = None
scene_composer = None
video_renderer = None
face_generator = None
emotion_analyzer = None
style_transfer = None
video_enhancer = None
human_movement = None
facial_expressions = None
voice_cloner = None
music_style_replicator = None

active_jobs = {}

def init_models(app):
    """Initialize all models with app config"""
    global audio_processor, beat_detector, character_generator
    global lip_sync_engine, instrument_simulator, scene_composer
    global video_renderer, face_generator, emotion_analyzer
    global style_transfer, video_enhancer, human_movement
    global facial_expressions, voice_cloner, music_style_replicator
    
    config = app.config
    
    audio_processor = AudioProcessor(config)
    beat_detector = BeatDetector(config)
    character_generator = CharacterGenerator(config)
    lip_sync_engine = LipSyncEngine(config)
    instrument_simulator = InstrumentSimulator(config)
    scene_composer = SceneComposer(config)
    video_renderer = VideoRenderer(config)
    face_generator = FaceGenerator(config)
    emotion_analyzer = EmotionAnalyzer(config)
    style_transfer = StyleTransfer(config)
    video_enhancer = VideoEnhancer(config)
    human_movement = HumanMovementEngine(config)
    facial_expressions = FacialExpressionEngine(config)
    voice_cloner = VoiceCloner(config)
    music_style_replicator = MusicStyleReplicator(config)

@api_bp.route('/upload', methods=['POST'])
def upload_audio():
    """Upload audio file for processing"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > current_app.config['MAX_FILE_SIZE']:
        return jsonify({'error': 'File size exceeds maximum limit (50MB)'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, f"{file_id}_{filename}")
    file.save(file_path)
    
    try:
        # Process audio
        audio_processor.load_audio(file_path)
        features = audio_processor.extract_features()
        
        # Analyze emotion
        emotion_data = emotion_analyzer.analyze_audio_emotion(
            audio_processor.audio_data,
            audio_processor.sample_rate
        )
        
        # Detect beats
        beat_data = beat_detector.detect_beats(
            audio_processor.audio_data,
            audio_processor.sample_rate
        )
        
        return jsonify({
            'file_id': file_id,
            'filename': filename,
            'features': features,
            'emotion': emotion_data['primary_emotion'],
            'emotion_intensity': emotion_data['intensity'],
            'tempo': beat_data['tempo'],
            'beat_count': len(beat_data['beat_times'])
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/process', methods=['POST'])
def process_audio():
    """Process audio and generate video with all enhancements"""
    data = request.json
    file_id = data.get('file_id')
    character_settings = data.get('characters', {})
    enhancement_settings = data.get('enhancements', {})
    voice_settings = data.get('voice', {})
    style_settings = data.get('style', {})
    
    if not file_id:
        return jsonify({'error': 'No file ID provided'}), 400
    
    # Find uploaded file
    upload_dir = current_app.config['UPLOAD_FOLDER']
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
        'file_id': file_id,
        'start_time': time.time()
    }
    
    def process_video():
        try:
            from app.api.websocket import emit_progress, emit_complete, emit_error
            
            def update_progress(progress, message=''):
                active_jobs[job_id]['progress'] = progress
                emit_progress(job_id, progress, message)
            
            update_progress(5, 'Loading audio...')
            
            # Process audio
            audio_processor.load_audio(audio_file)
            audio_features = audio_processor.extract_features()
            
            update_progress(10, 'Detecting beats...')
            
            # Detect beats
            beat_data = beat_detector.detect_beats(
                audio_processor.audio_data,
                audio_processor.sample_rate
            )
            
            update_progress(15, 'Analyzing emotions...')
            
            # Analyze emotion
            emotion_data = emotion_analyzer.analyze_audio_emotion(
                audio_processor.audio_data,
                audio_processor.sample_rate
            )
            
            update_progress(20, 'Detecting instruments...')
            
            # Detect instruments
            instrument_data = instrument_simulator.detect_instruments(
                audio_processor.audio_data,
                audio_processor.sample_rate
            )
            
            update_progress(25, 'Processing voice...')
            
            # Apply voice cloning if enabled
            voice_audio = audio_processor.audio_data
            if voice_settings.get('enabled', False):
                voice_name = voice_settings.get('voice_name', 'male_singer')
                try:
                    voice_audio = voice_cloner.clone_voice(
                        audio_processor.audio_data,
                        voice_name,
                        voice_settings.get('pitch_shift', 0),
                        voice_settings.get('formant_shift', 0)
                    )
                except Exception as e:
                    print(f"Voice cloning failed: {str(e)}")
            
            update_progress(30, 'Generating characters...')
            
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
            
            update_progress(40, 'Generating lip sync...')
            
            # Generate lip sync
            lip_sync_data = lip_sync_engine.process_audio_for_lip_sync(
                audio_processor.audio_data,
                audio_processor.sample_rate
            )
            
            update_progress(50, 'Generating human movements...')
            
            # Generate human movements
            movement_type = character_settings.get('movement_type', 'singing')
            movement_sequence = human_movement.generate_movement_sequence(
                audio_features,
                beat_data['beat_times'],
                emotion_data,
                movement_type
            )
            
            # Generate facial expressions
            expression_sequence = facial_expressions.generate_expression_sequence(
                emotion_data,
                lip_sync_data,
                len(audio_processor.audio_data) / audio_processor.sample_rate
            )
            
            update_progress(60, 'Applying music style...')
            
            # Apply music style replication if enabled
            style_audio = audio_processor.audio_data
            if style_settings.get('enabled', False):
                style_name = style_settings.get('style', 'pop')
                try:
                    style_audio = music_style_replicator.replicate_style(
                        audio_processor.audio_data,
                        style_name,
                        style_settings.get('intensity', 0.7)
                    )
                except Exception as e:
                    print(f"Style replication failed: {str(e)}")
            
            update_progress(70, 'Composing scenes...')
            
            # Compose scenes with emotion awareness and movement
            scenes = scene_composer.compose_scenes(
                audio_features,
                characters,
                beat_data['beat_times'],
                emotion_data,
                movement_sequence
            )
            
            update_progress(80, 'Rendering video...')
            
            # Render video
            output_filename = f"{file_id}_output.mp4"
            output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], output_filename)
            
            video_renderer.render_video(
                scenes,
                audio_file,
                characters,
                output_path,
                movement_sequence,
                expression_sequence,
                progress_callback=lambda p: update_progress(80 + p * 0.15, f'Rendering... {p:.1f}%')
            )
            
            update_progress(95, 'Enhancing video...')
            
            # Apply enhancements if enabled
            if enhancement_settings.get('style_transfer', True):
                genre = enhancement_settings.get('genre', 'pop')
                # Apply style transfer to video frames
                
            if enhancement_settings.get('color_grading', True):
                style = enhancement_settings.get('color_style', 'cinematic')
                # Apply color grading
            
            if enhancement_settings.get('face_enhancement', True):
                # Apply face enhancement
                pass
            
            update_progress(100, 'Video generation complete!')
            
            active_jobs[job_id]['status'] = 'complete'
            active_jobs[job_id]['output_file'] = output_filename
            active_jobs[job_id]['completed_time'] = time.time()
            
            emit_complete(job_id, f"/api/download/{output_filename}")
            
        except Exception as e:
            active_jobs[job_id]['status'] = 'error'
            active_jobs[job_id]['error'] = str(e)
            emit_error(job_id, str(e))
    
    # Start background thread
    thread = threading.Thread(target=process_video)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'status': 'processing'
    }), 202

@api_bp.route('/status/<job_id>')
def get_status(job_id):
    """Get job status"""
    job = active_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job), 200

@api_bp.route('/download/<filename>')
def download_video(filename):
    """Download generated video"""
    file_path = os.path.join(current_app.config['OUTPUT_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'Video not found'}), 404
    
    return send_file(file_path, as_attachment=True)

@api_bp.route('/preview/<job_id>')
def preview_video(job_id):
    """Stream preview of video during generation"""
    job = active_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Return preview data
    return jsonify({
        'status': job['status'],
        'progress': job['progress'],
        'preview_available': job['progress'] > 50
    })

@api_bp.route('/characters', methods=['GET'])
def get_characters():
    """Get available characters and customization options"""
    return jsonify({
        'types': current_app.config['AVAILABLE_CHARACTERS'],
        'instruments': current_app.config['AVAILABLE_INSTRUMENTS'],
        'hairstyles': current_app.config['AVAILABLE_HAIRSTYLES'],
        'outfits': current_app.config['AVAILABLE_OUTFITS'],
        'colors': current_app.config['AVAILABLE_COLORS'],
        'movement_types': ['singing', 'dancing', 'playing_instrument', 'walking', 'expressive', 'belting']
    })

@api_bp.route('/emotions', methods=['GET'])
def get_emotions():
    """Get available emotions"""
    return jsonify({
        'emotions': list(emotion_analyzer.emotion_mapping.keys()),
        'intensity_range': [0.0, 1.0]
    })

@api_bp.route('/genres', methods=['GET'])
def get_genres():
    """Get available music genres for style transfer"""
    return jsonify({
        'genres': list(music_style_replicator.style_characteristics.keys()),
        'styles': list(music_style_replicator.style_characteristics.keys())
    })

@api_bp.route('/enhancement_presets', methods=['GET'])
def get_enhancement_presets():
    """Get available enhancement presets"""
    return jsonify({
        'presets': list(video_enhancer.enhancement_presets.keys())
    })

@api_bp.route('/voices', methods=['GET'])
def get_voices():
    """Get available voices"""
    voices = voice_cloner.get_available_voices()
    return jsonify({
        'voices': voices,
        'defaults': ['male_singer', 'female_singer', 'tenor', 'soprano', 'bass']
    })

@api_bp.route('/train_voice', methods=['POST'])
def train_voice():
    """Train a new voice model"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    voice_name = request.form.get('voice_name', 'custom_voice')
    
    # Save audio
    filename = secure_filename(file.filename)
    temp_path = os.path.join(current_app.config['TEMP_FOLDER'], filename)
    file.save(temp_path)
    
    try:
        # Train voice
        voice_profile = voice_cloner.train_voice_from_audio(
            temp_path,
            voice_name,
            request.form.get('speaker_id')
        )
        
        return jsonify({
            'voice_name': voice_name,
            'profile': voice_profile,
            'message': 'Voice trained successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

@api_bp.route('/replicate_style', methods=['POST'])
def replicate_style():
    """Replicate music style"""
    data = request.json
    audio_file = data.get('audio_file')
    target_style = data.get('target_style', 'pop')
    
    if not audio_file:
        return jsonify({'error': 'No audio file provided'}), 400
    
    try:
        # Apply style replication
        style_audio = music_style_replicator.perfect_style_reproduction(
            audio_file,
            target_style,
            data.get('preserve_features', True)
        )
        
        # Save result
        output_filename = f"styled_{uuid.uuid4()}.wav"
        output_path = os.path.join(current_app.config['TEMP_FOLDER'], output_filename)
        
        import soundfile as sf
        sf.write(output_path, style_audio, 22050)
        
        return jsonify({
            'styled_audio': f"/api/download_temp/{output_filename}",
            'style': target_style
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'active_jobs': len(active_jobs)
    }), 200
