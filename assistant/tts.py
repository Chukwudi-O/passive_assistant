"""
Text-to-speech via pyttsx3.

pyttsx3 is MIT-licensed, fully offline, and uses the OS's built-in TTS engine
(Windows: SAPI5 / Microsoft voices — free, no account needed).

We run the TTS engine in its own thread because pyttsx3's runAndWait() blocks.
"""

import threading
import pyttsx3


class TTSEngine:
    def __init__(self, state):
        self.state   = state
        self._lock   = threading.Lock()
        self._engine = None
        self._init()

    def _init(self):
        try:
            self._engine = pyttsx3.init()
            self._apply_settings()
            print("[TTS] pyttsx3 initialised (Windows SAPI5)")
        except Exception as e:
            print(f"[TTS] Init error: {e}")

    def _apply_settings(self):
        if not self._engine:
            return
        try:
            rate   = self.state.get("tts_rate",   175)
            volume = self.state.get("tts_volume",  1.0)
            vi     = self.state.get("tts_voice_index", 0)

            self._engine.setProperty("rate",   rate)
            self._engine.setProperty("volume", volume)

            voices = self._engine.getProperty("voices")
            if voices and 0 <= vi < len(voices):
                self._engine.setProperty("voice", voices[vi].id)
        except Exception as e:
            print(f"[TTS] Settings error: {e}")

    def speak(self, text: str, on_done: callable = None):
        """
        Speak text in a background thread so the caller isn't blocked.
        on_done() is called after speech finishes (or on error).
        """
        def _run():
            with self._lock:
                try:
                    if not self._engine:
                        self._init()
                    self._apply_settings()
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception as e:
                    print(f"[TTS] Speak error: {e}")
                finally:
                    if on_done:
                        on_done()

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def get_voices(self) -> list[dict]:
        """Return list of available voices as {index, name, id}."""
        if not self._engine:
            return []
        try:
            voices = self._engine.getProperty("voices") or []
            return [{"index": i, "name": v.name, "id": v.id}
                    for i, v in enumerate(voices)]
        except Exception:
            return []
