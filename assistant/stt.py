import io
import json
import os
import wave
from os import PathLike

import numpy as np


MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
SMALL_MODEL_NAME = "vosk-model-small-en-us-0.15"
LARGE_MODEL_NAME = "vosk-model-en-us-0.22"


def _find_model(prefer_large: bool = True) -> str | None:
    candidates = (
        [LARGE_MODEL_NAME, SMALL_MODEL_NAME]
        if prefer_large
        else [SMALL_MODEL_NAME, LARGE_MODEL_NAME]
    )
    for name in candidates:
        path = os.path.join(MODELS_DIR, name)
        if os.path.isdir(path):
            return path
    return None


def _audio_to_wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:
    if audio.ndim > 1:
        audio = audio[:, 0]

    if np.issubdtype(audio.dtype, np.floating):
        audio = np.clip(audio, -1.0, 1.0)
        audio = (audio * 32767).astype(np.int16)
    else:
        audio = audio.astype(np.int16)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())
    return buffer.getvalue()


def transcribe_wav(
    audio_source: str | PathLike[str] | bytes | bytearray | np.ndarray,
    sample_rate: int = 16000,
) -> str | None:
    try:
        import vosk
    except ImportError:
        print("[STT] vosk not installed. Run: pip install vosk")
        return None

    model_path = _find_model(prefer_large=True)
    if not model_path:
        print(f"[STT] No Vosk model found in {MODELS_DIR}")
        return None

    try:
        model = vosk.Model(model_path)

        if isinstance(audio_source, np.ndarray):
            wav_bytes = _audio_to_wav_bytes(audio_source, sample_rate)
            wave_source = io.BytesIO(wav_bytes)
        elif isinstance(audio_source, (bytes, bytearray)):
            wave_source = io.BytesIO(bytes(audio_source))
        else:
            wave_source = os.fspath(audio_source)

        with wave.open(wave_source, "rb") as wav_file:
            if wav_file.getnchannels() != 1 or wav_file.getsampwidth() != 2:
                print("[STT] Audio must be mono 16-bit PCM WAV.")
                return None

            recognizer = vosk.KaldiRecognizer(model, wav_file.getframerate())
            recognizer.SetWords(True)

            parts = []
            while True:
                data = wav_file.readframes(4000)
                if not data:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    parts.append(result.get("text", ""))

            final = json.loads(recognizer.FinalResult())
            parts.append(final.get("text", ""))

        text = " ".join(part for part in parts if part).strip()
        return text or None
    except Exception as exc:
        print(f"[STT] Transcription error: {exc}")
        return None
