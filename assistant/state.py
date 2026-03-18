"""
Shared application state — thread-safe flags and config used across all modules.
"""

import threading
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')

DEFAULT_CONFIG = {
    "wake_phrase": "Yo chat",
    "gemini_api_key": "",
    "gemini_model": "gemini-2.0-flash",
    "tts_rate": 175,
    "tts_volume": 1.0,
    "tts_voice_index": 0,
    "system_prompt": (
        "You are a member of a twitch that that will help the streamer with various tasks. "
        "You are helpful, creative, clever, and very friendly. You will answer questions and provide information to the best of your ability. "
        "Keep responses concise and conversational — ideally under 5 sentences unless more detail is clearly needed. "
        "Do not use markdown, bullet points, or special formatting; speak in plain natural language."
    ),
    "silence_threshold": 700,
    "silence_duration": 2.0,
    "max_record_seconds": 15
}


class AppState:
    def __init__(self):
        self._lock = threading.Lock()
        self.running = True
        self.listening = True
        self.processing = False
        self.config = self._load_config()

    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    saved = json.load(f)
                cfg = DEFAULT_CONFIG.copy()
                cfg.update(saved)
                print(f"[State] Config loaded from {CONFIG_PATH}")
                return cfg
            except Exception:
                print(f"[State] Failed to load config, using defaults.")
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"[State] Config saved to {CONFIG_PATH}")
        except Exception as e:
            print(f"[State] Failed to save: {e}")

    def get(self, key, default=None):
        with self._lock:
            return self.config.get(key, default)

    def set(self, key, value):
        with self._lock:
            self.config[key] = value
        self.save_config()

    def set_processing(self, val: bool):
        with self._lock:
            self.processing = val

    def is_processing(self):
        with self._lock:
            return self.processing

    def set_listening(self, val: bool):
        with self._lock:
            self.listening = val

    def is_listening(self):
        with self._lock:
            return self.listening
