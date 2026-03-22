"""
Audio recording with silence detection.
Records from the default microphone and stops when the user falls silent.

Dependencies: sounddevice, numpy
"""

import time

import sounddevice as sd
import numpy as np
from openwakeword.model import Model

SAMPLE_RATE     = 16000
CHANNELS        = 1
CHUNK_DURATION  = 0.5  # how long each audio chunk is when checking for silence


class AudioRecorder:
    def __init__(self,chunk_duration=CHUNK_DURATION,state=None):
        self._silence_threshold = state.get("silence_threshold", 0.7)
        self._silence_duration  = state.get("silence_duration", 4.0)
        self._chunk_duration    = chunk_duration
        self._model             = Model(wakeword_models=[state.get("wake_phrase", "hey jarvis")])
        self._state             = state
        sd.default.channels     = CHANNELS
        sd.default.samplerate   = SAMPLE_RATE

    def get_audio_chunk(self)-> np.ndarray:
        """Record a short chunk of audio and return it as a numpy array."""
        chunk = sd.rec(int(self._chunk_duration * SAMPLE_RATE))
        sd.wait()
        return chunk

    # def process_audio_chunk(self,chunk):
    #     # Convert to correct format
    #     audio = chunk[:, 0]  # mono
    #     audio = (audio * 32767).astype(np.int16)

    #     prediction = self._model.predict(audio)

    #     # prediction is a dict: {'wake_word_name': score}
    #     for key, score in prediction.items():
    #         if score > self._silence_threshold:
    #             return True
    #     return False
    
    def listen_for_wake(self,hit_count):
        detected = False

        def callback(indata, frames, time_info, status):
            nonlocal detected, hit_count

            if detected:
                return

            # Convert audio to int16 mono
            audio = (indata[:, 0] * 32767).astype(np.int16)

            predictions = self._model.predict(audio)

            for score in predictions.values():
                if score > self._silence_threshold:
                    hit_count += 1

            if hit_count >= 20:
                detected = True

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype='float32',
            callback=callback
        ):
            while not detected:
                time.sleep(0.04)  # prevents CPU overuse

        print("Wake word detected!")
        return True

    def record_until_silence(self):
        """Record until silence is detected for the full silence_duration."""
        recorded_audio = []
        silence_chunks = int(self._silence_duration / self._chunk_duration)
        min_chunks = 2.5  # minimum 2.5 seconds before we start checking for silence
        silent_count = 0

        while True:
            chunk = self.get_audio_chunk()
            recorded_audio.append(chunk)

            # Calculate volume using RMS (root mean square) for more accurate audio level
            rms = np.sqrt(np.mean(chunk**2))

            # Only start checking for silence after minimum recording time
            if len(recorded_audio) >= min_chunks:
                if rms < self._silence_threshold:
                    silent_count += 1
                else:
                    silent_count = 0

                # Stop when we've detected silence for the full duration
                if silent_count >= silence_chunks:
                    print("Silence detected. Stopping...")
                    break

        # Concatenate all chunks and return
        audio = np.concatenate(recorded_audio)
        return audio