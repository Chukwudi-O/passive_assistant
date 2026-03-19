from google import genai
import io
import wave

import numpy as np
from typing import Union


class GenAI:
    def __init__(self, model_name: str, api_key: str, system_prompt: str = ""):
        self._model_name = model_name
        self._api_key = api_key
        self._system_prompt = system_prompt
        self._client = genai.Client(api_key=api_key)

    def _to_wav_bytes(self, audio: Union[bytes, np.ndarray], sample_rate: int = 16000) -> bytes:
        """Ensure the audio is encoded as WAV bytes.

        The Gemini API expects raw bytes (e.g., a WAV file) for audio inputs. We
        record audio as a NumPy float32 array, so we need to convert it to 16-bit
        PCM WAV bytes.
        """
        if isinstance(audio, (bytes, bytearray)):
            return bytes(audio)

        if not isinstance(audio, np.ndarray):
            raise TypeError(f"Unsupported audio type: {type(audio)}")

        # Force mono
        if audio.ndim > 1:
            audio = audio[:, 0]

        # Normalize/convert float data to int16 when needed
        if np.issubdtype(audio.dtype, np.floating):
            audio = np.clip(audio, -1.0, 1.0)
            audio = (audio * 32767).astype(np.int16)
        else:
            audio = audio.astype(np.int16)

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio.tobytes())

        return buf.getvalue()
    
    def generate_response(self, content:Union[bytes, np.ndarray]) -> str:
        audio_bytes = self._to_wav_bytes(content)

        response = self._client.models.generate_content(
            model=self._model_name,
            contents=[
                self._system_prompt,
                genai.types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type="audio/wav"
                )
            ]
        )
        return response.text