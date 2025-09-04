import json
from datetime import datetime, timedelta
from collections import Counter
import os

class SessionTracker:
    def __init__(self):
        self.session_start = datetime.now()
        self.mood_history = []
        self.log_file = "assets/neurobot_sessions.json"
        self.ensure_assets_directory()
    
    def ensure_assets_directory(self):
        if not os.path.exists("assets"):
            os.makedirs("assets")
    
    def log_mood_check(self, mood):
        self.mood_history.append({
            'mood': mood,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_session_stats(self):
        duration = datetime.now() - self.session_start
        moods = [entry['mood'] for entry in self.mood_history]
        
        return {
            'duration': str(duration).split('.')[0],  # Remove microseconds
            'moods': list(set(moods)),
            'most_common_mood': Counter(moods).most_common(1)[0][0] if moods else None
        }
    
    def save_session(self, conversation_history):
        session_data = {
            'session_id': self.session_start.isoformat(),
            'duration': (datetime.now() - self.session_start).total_seconds(),
            'conversation_length': len(conversation_history),
            'moods_detected': [entry['mood'] for entry in self.mood_history],
            'timestamp': datetime.now().isoformat()
        }
        
        # Load existing data
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        
        # Append new session
        data.append(session_data)
        
        # Save back to file
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)
