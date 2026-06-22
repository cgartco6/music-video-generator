class MIDIMapper:
    def __init__(self):
        # MIDI note numbers to instrument mapping
        self.instrument_to_midi = {
            'piano': 0,
            'guitar': 24,
            'bass': 32,
            'drums': 9,
            'keyboard': 4,
            'violin': 40,
            'flute': 73,
            'saxophone': 65,
            'trumpet': 56,
            'synth': 90
        }
        
        self.midi_to_instrument = {v: k for k, v in self.instrument_to_midi.items()}
    
    def get_midi_program(self, instrument):
        """Get MIDI program number for instrument"""
        return self.instrument_to_midi.get(instrument, 0)
    
    def get_instrument(self, midi_program):
        """Get instrument name from MIDI program number"""
        return self.midi_to_instrument.get(midi_program, 'piano')
    
    def generate_midi_notes(self, beat_times, instrument='piano', tempo=120):
        """Generate MIDI notes from beat times"""
        midi_notes = []
        program = self.get_midi_program(instrument)
        
        for i, beat in enumerate(beat_times):
            note = {
                'time': beat,
                'duration': 60 / tempo * 0.5,
                'pitch': 60 + (i % 12),  # Simple melody
                'velocity': 80 + (i % 40),
                'program': program
            }
            midi_notes.append(note)
        
        return midi_notes
