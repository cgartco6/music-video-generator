import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import random
import math

class HumanMovementEngine:
    def __init__(self, config):
        self.config = config
        self.movement_patterns = {
            'singing': self._generate_singing_movement,
            'dancing': self._generate_dance_movement,
            'playing_instrument': self._generate_instrument_movement,
            'walking': self._generate_walking_movement,
            'expressive': self._generate_expressive_movement,
            'belting': self._generate_belting_movement
        }
        
        # Human body joint positions (simplified skeleton)
        self.joints = {
            'head': (0, -50),
            'neck': (0, -30),
            'shoulder_l': (-20, -25),
            'shoulder_r': (20, -25),
            'elbow_l': (-35, -10),
            'elbow_r': (35, -10),
            'wrist_l': (-45, 5),
            'wrist_r': (45, 5),
            'hip_l': (-15, 25),
            'hip_r': (15, 25),
            'knee_l': (-15, 45),
            'knee_r': (15, 45),
            'ankle_l': (-15, 65),
            'ankle_r': (15, 65)
        }
        
        # Movement constraints
        self.joint_limits = {
            'head': {'angle': (-30, 30), 'speed': 60},
            'shoulder_l': {'angle': (-45, 45), 'speed': 90},
            'shoulder_r': {'angle': (-45, 45), 'speed': 90},
            'elbow_l': {'angle': (-90, 20), 'speed': 120},
            'elbow_r': {'angle': (-20, 90), 'speed': 120},
            'wrist_l': {'angle': (-60, 60), 'speed': 150},
            'wrist_r': {'angle': (-60, 60), 'speed': 150},
            'hip_l': {'angle': (-30, 30), 'speed': 60},
            'hip_r': {'angle': (-30, 30), 'speed': 60},
            'knee_l': {'angle': (-10, 90), 'speed': 90},
            'knee_r': {'angle': (-10, 90), 'speed': 90}
        }
    
    def generate_movement_sequence(self, audio_features, beat_times, emotion_data, movement_type='singing'):
        """Generate realistic human movement sequence"""
        movement_func = self.movement_patterns.get(movement_type, self._generate_singing_movement)
        
        # Generate movement parameters
        movement_params = movement_func(audio_features, beat_times, emotion_data)
        
        # Smooth movements
        smoothed_movements = self._smooth_movements(movement_params)
        
        # Add natural variations
        natural_movements = self._add_natural_variations(smoothed_movements)
        
        return natural_movements
    
    def _generate_singing_movement(self, audio_features, beat_times, emotion_data):
        """Generate singing-specific movements"""
        movements = []
        tempo = audio_features.get('tempo', 120)
        energy = audio_features.get('energy', 0.5)
        emotion = emotion_data.get('primary_emotion', 'neutral')
        intensity = emotion_data.get('intensity', 0.5)
        
        for i, beat in enumerate(beat_times):
            # Body sway based on beat
            sway_amount = 5 + 10 * energy
            sway = sway_amount * np.sin(2 * np.pi * i / len(beat_times))
            
            # Head movement based on emotion
            head_tilt = self._get_head_movement(emotion, intensity)
            
            # Arm gestures based on intensity
            arm_gesture = self._get_arm_gesture(emotion, intensity)
            
            # Breathing motion
            breath = 3 * np.sin(2 * np.pi * i / (tempo / 60 * 2))
            
            movements.append({
                'time': beat,
                'body_sway': sway,
                'head_tilt': head_tilt,
                'arm_gesture': arm_gesture,
                'breath': breath,
                'intensity': intensity
            })
        
        return movements
    
    def _generate_belting_movement(self, audio_features, beat_times, emotion_data):
        """Generate belting (powerful singing) movements"""
        movements = []
        energy = audio_features.get('energy', 0.8)
        emotion = emotion_data.get('primary_emotion', 'passionate')
        
        for i, beat in enumerate(beat_times):
            # Powerful body movements
            body_lean = 15 * energy * np.sin(2 * np.pi * i / 8)
            
            # Arms wide
            arm_spread = 30 + 20 * energy
            
            # Head thrown back
            head_tilt = -20 * energy
            
            # Powerful gestures
            gesture_power = 1.5 * energy
            
            movements.append({
                'time': beat,
                'body_lean': body_lean,
                'arm_spread': arm_spread,
                'head_tilt': head_tilt,
                'gesture_power': gesture_power,
                'belting': True
            })
        
        return movements
    
    def _generate_dance_movement(self, audio_features, beat_times, emotion_data):
        """Generate dance movements"""
        movements = []
        tempo = audio_features.get('tempo', 120)
        energy = audio_features.get('energy', 0.6)
        
        for i, beat in enumerate(beat_times):
            # Dance steps
            step = self._get_dance_step(i, tempo)
            
            # Body movement
            body_move = 20 * energy * np.sin(2 * np.pi * i / (tempo / 60))
            
            # Arm choreography
            arm_sequence = self._get_arm_sequence(i, tempo)
            
            movements.append({
                'time': beat,
                'step': step,
                'body_move': body_move,
                'arm_sequence': arm_sequence,
                'energy': energy
            })
        
        return movements
    
    def _generate_instrument_movement(self, audio_features, beat_times, emotion_data):
        """Generate instrument playing movements"""
        movements = []
        instrument = audio_features.get('primary_instrument', 'guitar')
        
        for beat in beat_times:
            # Instrument-specific movements
            if instrument == 'guitar':
                movement = self._generate_guitar_movement(beat, audio_features)
            elif instrument == 'drums':
                movement = self._generate_drums_movement(beat, audio_features)
            elif instrument == 'keyboard':
                movement = self._generate_keyboard_movement(beat, audio_features)
            else:
                movement = self._generate_general_instrument_movement(beat)
            
            movements.append(movement)
        
        return movements
    
    def _generate_guitar_movement(self, beat, features):
        """Generate realistic guitar playing movements"""
        return {
            'time': beat,
            'strumming_hand': 'down' if beat % 2 == 0 else 'up',
            'fretting_hand': {
                'position': np.random.randint(1, 12),
                'pressure': 0.5 + 0.5 * features.get('energy', 0.5)
            },
            'body_sway': 3 * np.sin(beat * 0.5),
            'foot_tapping': beat % 2 == 0
        }
    
    def _generate_drums_movement(self, beat, features):
        """Generate realistic drum playing movements"""
        hits = []
        if beat % 2 == 0:
            hits.append('snare')
        if beat % 4 == 0:
            hits.append('bass')
        if beat % 8 == 0:
            hits.append('hihat')
        
        return {
            'time': beat,
            'hits': hits,
            'arm_raise': 10 + 20 * features.get('energy', 0.5),
            'head_bob': 5 * np.sin(beat * 2),
            'intensity': features.get('energy', 0.5)
        }
    
    def _generate_keyboard_movement(self, beat, features):
        """Generate realistic keyboard playing movements"""
        return {
            'time': beat,
            'hand_movement': 'left' if beat % 2 == 0 else 'right',
            'key_press': 0.3 + 0.7 * features.get('energy', 0.5),
            'body_lean': 5 * np.sin(beat * 0.3),
            'expression': 'passionate' if features.get('energy', 0.5) > 0.7 else 'focused'
        }
    
    def _get_head_movement(self, emotion, intensity):
        """Get head movement based on emotion"""
        movements = {
            'happy': {'tilt': (5, 15), 'nod': 0.3},
            'sad': {'tilt': (-5, -15), 'nod': 0.1},
            'angry': {'tilt': (0, 10), 'nod': 0.5},
            'passionate': {'tilt': (-10, 20), 'nod': 0.4},
            'romantic': {'tilt': (10, -5), 'nod': 0.2},
            'energetic': {'tilt': (-5, 25), 'nod': 0.6},
            'calm': {'tilt': (0, 5), 'nod': 0.1}
        }
        
        movement = movements.get(emotion, movements['neutral'])
        tilt = movement['tilt'][0] + (movement['tilt'][1] - movement['tilt'][0]) * intensity
        return tilt * random.uniform(0.8, 1.2)
    
    def _get_arm_gesture(self, emotion, intensity):
        """Get arm gesture based on emotion"""
        gestures = {
            'happy': {'open': 0.7, 'raise': 0.5, 'speed': 0.8},
            'sad': {'open': 0.2, 'raise': 0.1, 'speed': 0.3},
            'angry': {'open': 0.8, 'raise': 0.7, 'speed': 0.9},
            'passionate': {'open': 0.9, 'raise': 0.8, 'speed': 0.7},
            'romantic': {'open': 0.4, 'raise': 0.3, 'speed': 0.4},
            'energetic': {'open': 0.8, 'raise': 0.9, 'speed': 0.9},
            'calm': {'open': 0.3, 'raise': 0.2, 'speed': 0.2}
        }
        
        gesture = gestures.get(emotion, gestures['neutral'])
        return {
            'openness': gesture['open'] * intensity,
            'raise': gesture['raise'] * intensity,
            'speed': gesture['speed']
        }
    
    def _get_dance_step(self, i, tempo):
        """Get dance step pattern"""
        step_patterns = [
            ['left', 'right', 'left', 'right'],
            ['step', 'touch', 'step', 'touch'],
            ['forward', 'back', 'forward', 'back'],
            ['left', 'cross', 'right', 'cross']
        ]
        pattern = step_patterns[i % len(step_patterns)]
        return pattern[i % len(pattern)]
    
    def _get_arm_sequence(self, i, tempo):
        """Get arm sequence for dance"""
        sequences = [
            ['raise_l', 'raise_r', 'lower_l', 'lower_r'],
            ['pump_l', 'pump_r', 'pump_l', 'pump_r'],
            ['wave_l', 'wave_r', 'wave_both', 'wave_both'],
            ['cross', 'uncross', 'cross', 'uncross']
        ]
        seq = sequences[i % len(sequences)]
        return seq[i % len(seq)]
    
    def _smooth_movements(self, movements):
        """Apply smoothing to movements"""
        if len(movements) < 3:
            return movements
        
        smoothed = []
        window_size = 3
        
        for i in range(len(movements)):
            if i < window_size // 2 or i >= len(movements) - window_size // 2:
                smoothed.append(movements[i])
            else:
                # Average over window
                avg = {}
                for key in movements[i].keys():
                    if key != 'time' and isinstance(movements[i][key], (int, float)):
                        values = [m[key] for m in movements[i-window_size//2:i+window_size//2+1]]
                        avg[key] = np.mean(values)
                    else:
                        avg[key] = movements[i][key]
                smoothed.append(avg)
        
        return smoothed
    
    def _add_natural_variations(self, movements):
        """Add natural variations to prevent robotic movements"""
        varied = []
        
        for movement in movements:
            varied_movement = movement.copy()
            
            for key, value in movement.items():
                if key != 'time' and isinstance(value, (int, float)):
                    # Add small random variation
                    variation = value * random.uniform(-0.05, 0.05)
                    varied_movement[key] = value + variation
            
            varied.append(varied_movement)
        
        return varied
    
    def generate_body_animation(self, movement_sequence, character):
        """Generate body animation frames from movement sequence"""
        frames = []
        
        for movement in movement_sequence:
            # Calculate joint positions based on movement data
            joint_positions = self._calculate_joint_positions(movement, character)
            
            # Generate frame with character in these positions
            frame = self._render_character_frame(joint_positions, character)
            frames.append(frame)
        
        return frames
    
    def _calculate_joint_positions(self, movement, character):
        """Calculate joint positions from movement data"""
        positions = {}
        base_positions = character.get('joint_positions', self.joints)
        
        # Apply movement to joints
        for joint, base_pos in base_positions.items():
            x, y = base_pos
            
            # Apply body sway
            if 'body_sway' in movement:
                x += movement['body_sway'] * 0.5
            
            # Apply joint-specific movements
            if joint == 'head' and 'head_tilt' in movement:
                y += movement['head_tilt'] * 0.3
            
            if 'arm_gesture' in movement and joint in ['elbow_l', 'wrist_l', 'elbow_r', 'wrist_r']:
                arm = movement['arm_gesture']
                if 'l' in joint:
                    x -= arm['openness'] * 10
                    y -= arm['raise'] * 15
                else:
                    x += arm['openness'] * 10
                    y -= arm['raise'] * 15
            
            # Add breath movement
            if 'breath' in movement:
                y += movement['breath'] * 0.5
            
            positions[joint] = (x, y)
        
        return positions
    
    def _render_character_frame(self, joint_positions, character):
        """Render character in specific pose"""
        # This would create the visual representation
        # Placeholder for actual rendering
        return {
            'joints': joint_positions,
            'timestamp': time.time()
        }
