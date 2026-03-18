"""
launch.pyw
==========
Run this file with pythonw.exe to launch the assistant silently
(no console window) on Windows.

  pythonw launch.pyw

Or right-click → Open With → Python (pythonw.exe)

You can also create a Windows shortcut:
  Target:  C:\Path\To\pythonw.exe  C:\Path\To\voice_assistant\launch.pyw
  Start in: C:\Path\To\voice_assistant\
"""

import subprocess
import sys
import os

# Launch main.py with pythonw so no console appears
script = os.path.join(os.path.dirname(__file__), "main.py")
pythonw = sys.executable.replace("python.exe", "pythonw.exe")

subprocess.Popen([pythonw, script])
