"""
WakeWordListener
================
Background thread that:
  1. Streams microphone audio through Vosk to detect the wake phrase.
  2. On detection → records the user's command with silence detection.
  3. Transcribes the recording with Vosk.
  4. Sends transcript to GPT.
  5. Speaks the reply via pyttsx3.
  6. Updates the overlay indicator throughout.

All heavy work happens in threads so the main thread (system tray) is never
blocked.
"""

import threading
import time
import sounddevice as sd

from assistant.stt import SpeechToTextEngine
from .audio   import AudioRecorder
from .tts     import TTSEngine
from .genai   import GenAI

COOLDOWN_SECONDS = 1.0   # pause after TTS before listening again


class WakeWordListener:
    def __init__(self, state, overlay):
        self._running       = True
        self.state          = state
        self.overlay        = overlay
        self._tts           = TTSEngine(state)
        self._stt           = SpeechToTextEngine(state)
        self._genai         = GenAI(
            model_name      = state.get("gemini_model", "gemini-2.0-flash"),
            api_key         = state.get("gemini_api_key", ""),
            system_prompt   = state.get("system_prompt", "")
        )
        self._audio         = AudioRecorder(
            chunk_duration      = 0.5,
            state               = state
        )

    # ── public API ─────────────────────────────────────────────────────────────

    def stop(self):
        self._running = False

    # ── main loop (runs in daemon thread) ──────────────────────────────────────

    def run(self):
        print("[Listener] Starting wake-word loop …")
        hit_count = 0
        while self._running and self.state.running:
            try:
                    # If paused from tray or currently speaking, skip listening
                    if not self.state.is_listening() or self.state.is_processing():
                        continue

                    # Otherwise, listen for the wake word
                    print("[Listener] Listening for wake word …")
                    detected = self._audio.listen_for_wake(hit_count=hit_count)
                    if detected:
                        hit_count = 0
                        print("[Listener] Wake word detected!")
                        time.sleep(1)  # brief pause to avoid immediate retrigger
                        self._handle_command()
            except Exception as e:
                print(f"[Listener] Error in main loop: {e}")
                self.state.set_processing(False)
                self.overlay.hide()


        print("[Listener] Stopped.")

    # ── pipeline ───────────────────────────────────────────────────────────────

    def _handle_command(self):
        """Record → transcribe → GenAI → TTS (blocking within this call)."""
        self.state.set_processing(True)
        self.overlay.show_listening()

        # 1. Record the command
        print("[Listener] Recording command …")
        audio = self._audio.record_until_silence()

        #2. Transcribe the command
        print("[Listener] Transcribing audio …")
        transcript = self._stt.transcribe(audio)
        print(f"[Listener] Transcript: {transcript}")

        # 3. GenAI
        self.overlay.show_thinking()
        print("[Listener] Querying Gemini …")
        reply = "Testing Text to Speech"#self._genai.generate_response(transcript)

        print(f"[Listener] Reply: {reply}")

        if not reply:
            self.overlay.hide()
            self.state.set_processing(False)
            print("[Listener] Couldn't get a reply from Gemini.")
            return

        # 4. TTS
        self.overlay.show_speaking()

        done_event = threading.Event()

        def on_done():
            done_event.set()

        self._tts.speak(reply, on_done=on_done)
        done_event.wait()   # block until speech finishes

        self.overlay.hide()
        time.sleep(COOLDOWN_SECONDS)
        self.state.set_processing(False)