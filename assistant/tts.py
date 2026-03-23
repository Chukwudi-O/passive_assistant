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
        self.state = state
        self._lock = threading.Lock()

    def speak(self, text: str, on_done: callable = None):
        """
        Speak text in a background thread so the caller isn't blocked.
        on_done() is called after speech finishes (or on error).
        """
        def _run():
            with self._lock:
                engine = None
                try:
                    engine = pyttsx3.init()
                    rate   = self.state.get("tts_rate",   175)
                    volume = self.state.get("tts_volume",  1.0)
                    vi     = self.state.get("tts_voice_index", 0)

                    engine.setProperty("rate",   rate)
                    engine.setProperty("volume", volume)

                    voices = engine.getProperty("voices")
                    if voices and 0 <= vi < len(voices):
                        engine.setProperty("voice", voices[vi].id)

                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    print(f"[TTS] Speak error: {e}")
                finally:
                    # Don't stop the engine
                    if on_done:
                        on_done()

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def get_voices(self) -> list[dict]:
        """Return list of available voices as {index, name, id}."""
        engine = None
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices") or []
            return [{"index": i, "name": v.name, "id": v.id}
                    for i, v in enumerate(voices)]
        except Exception:
            return []
        finally:
            if engine:
                try:
                    engine.stop()
                except Exception:
                    pass
