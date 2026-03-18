"""
download_model.py
=================
Downloads and extracts the Vosk English models into ./models/

Run once before launching the assistant:
    python download_model.py

Models
------
  small  ~40 MB   fast, lower accuracy, good for wake-word detection
  large ~1.8 GB   slower to load, higher accuracy for transcription

Both are Apache 2.0 licensed from https://alphacephei.com/vosk/models
"""

import os
import sys
import urllib.request
import zipfile

import openwakeword
from openwakeword.model import Model

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

MODELS = {
    "small": {
        "name": "vosk-model-small-en-us-0.15",
        "url":  "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "size": "~40 MB",
    },
    "large": {
        "name": "vosk-model-en-us-0.22",
        "url":  "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
        "size": "~1.8 GB",
    },
}


def _progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        pct = min(downloaded * 100 / total_size, 100)
        bar = "#" * int(pct // 2)
        sys.stdout.write(f"\r  [{bar:<50}] {pct:.1f}%")
        sys.stdout.flush()


def download(which: str = "small"):
    info = MODELS[which]
    dest_dir  = os.path.join(MODELS_DIR, info["name"])
    zip_path  = os.path.join(MODELS_DIR, info["name"] + ".zip")

    if os.path.isdir(dest_dir):
        print(f"✓ {info['name']} already present — skipping download.")
        return

    os.makedirs(MODELS_DIR, exist_ok=True)
    print(f"Downloading {info['name']} ({info['size']}) …")
    urllib.request.urlretrieve(info["url"], zip_path, _progress)
    print()

    print("Extracting …")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(MODELS_DIR)
    os.remove(zip_path)
    print(f"✓ Model extracted to {dest_dir}")


if __name__ == "__main__":
    openwakeword.utils.download_models()
    # which = "small"
    # if len(sys.argv) > 1 and sys.argv[1] in ("small", "large"):
    #     which = sys.argv[1]

    # download(which)

    # if which == "small":
    #     print()
    #     ans = input("Also download the large model for better transcription accuracy? [y/N] ").strip().lower()
    #     if ans == "y":
    #         download("large")

    # print("\nDone. You can now run:  python main.py")
