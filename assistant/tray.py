"""
System Tray Application
=======================
Uses pystray (MIT license) + Pillow (HPND license, open-source).

The tray icon runs on the main thread (required by pystray on Windows).
All menu callbacks that open Tk windows must post onto the Tk event loop
via root.after() to avoid cross-thread Tk calls.

Tray menu
---------
  ● Listening  /  ○ Paused   (toggle)
  ─────────────────────────────────
  Settings …
  ─────────────────────────────────
  Quit
"""

import threading
import tkinter as tk
import pystray
from PIL import Image, ImageDraw
import queue

from .settings import SettingsDialog


# ── Icon drawing ───────────────────────────────────────────────────────────────

def _make_icon(active: bool = True) -> Image.Image:
    """
    Draw a 64×64 tray icon.
    Active  (listening)  → bright teal microphone silhouette on dark bg
    Inactive (paused)    → grey microphone on dark bg
    """
    size  = 64
    img   = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw  = ImageDraw.Draw(img)

    bg    = (30,  32,  36,  255)
    fg    = (79, 195, 247, 255) if active else (120, 120, 120, 255)

    # Background circle
    draw.ellipse([0, 0, size - 1, size - 1], fill=bg)

    # Microphone body (rounded rect)
    draw.rounded_rectangle([22, 8, 42, 38], radius=10, fill=fg)

    # Stand arc  (approximate with a rectangle + ellipse)
    draw.arc([14, 24, 50, 50], start=0, end=180, fill=fg, width=3)

    # Stand stem
    draw.line([32, 50, 32, 56], fill=fg, width=3)

    # Base bar
    draw.line([24, 56, 40, 56], fill=fg, width=3)

    return img


# ── Tray App ───────────────────────────────────────────────────────────────────

class TrayApp:
    def __init__(self, state, listener, overlay):
        self.state    = state
        self.listener = listener
        self.overlay  = overlay
        self._tk_root = None   # created in Tk thread
        self._icon    = None
        self._tk_ready = threading.Event()  # signal when Tk is ready
        self._tk_queue = queue.Queue()  # thread-safe queue for Tk thread messages

    def run(self):
        """Start the tray icon. Blocks until Quit is chosen."""

        # Start Tk event loop in a separate thread FIRST
        # This thread will own the Tk root and process all Tk calls
        tk_thread = threading.Thread(target=self._run_tk_loop, daemon=True)
        tk_thread.start()
        
        # Wait for Tk to be ready before starting pystray
        print("[Tray] Waiting for Tk event loop to start...")
        self._tk_ready.wait(timeout=5)
        print("[Tray] Tk event loop ready, starting pystray...")

        menu = pystray.Menu(
            pystray.MenuItem(
                lambda item: "● Listening" if self.state.is_listening() else "○ Paused",
                self._toggle_listening,
                default=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings …",   self._open_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit",          self._quit),
        )

        self._icon = pystray.Icon(
            name  = "VoiceAssistant",
            icon  = _make_icon(active=True),
            title = "Voice Assistant",
            menu  = menu,
        )
        print("[Tray] Starting tray icon...")
        # Run pystray on the main thread (Windows requirement)
        self._icon.run()
        

    # ── Tk loop ────────────────────────────────────────────────────────────────

    def _run_tk_loop(self):
        """Create and manage the hidden Tk root; process events for dialog windows."""
        try:
            # Create Tk root IN this thread so it owns the main loop
            self._tk_root = tk.Tk()
            self._tk_root.withdraw()
            self._tk_root.wm_attributes("-toolwindow", True)
            print("[Tray] Tk root created in event loop thread")
            
            # Signal that Tk is ready
            self._tk_ready.set()
            
            # Process Tk events until app is shutting down
            while self.state.running:
                try:
                    self._tk_root.update()
                    
                    # Check for queued messages from other threads
                    try:
                        while True:
                            msg = self._tk_queue.get_nowait()
                            if msg == "show_settings":
                                self._show_settings_window()
                    except queue.Empty:
                        pass
                    
                    import time; time.sleep(0.02)
                except tk.TclError:
                    # Window was destroyed
                    break
        except Exception as e:
            print(f"[Tray] Tk loop fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                if self._tk_root:
                    self._tk_root.destroy()
            except Exception:
                pass
            print("[Tray] Tk loop ended")

    # ── Menu callbacks ─────────────────────────────────────────────────────────

    def _toggle_listening(self, icon, item):
        is_on = self.state.is_listening()
        self.state.set_listening(not is_on)
        icon.icon = _make_icon(active=not is_on)
        print(f"[Tray] Listening {'paused' if is_on else 'resumed'}.")

    def _open_settings(self, icon, item):
        """Callback from pystray (main thread) - queue the settings window creation."""
        print("[Tray] Settings button clicked")
        self._tk_queue.put("show_settings")
        print("[Tray] Settings request queued")

    def _show_settings_window(self):
        """Called from Tk thread - safe to use Tk calls directly."""
        try:
            print("[Tray] Creating settings window...")
            SettingsDialog(self._tk_root, self.state, self.listener)
            print("[Tray] Settings window opened successfully.")
        except Exception as e:
            print(f"[Tray] Failed to open settings: {e}")
            import traceback
            traceback.print_exc()

    def _quit(self, icon, item):
        print("[Tray] Quitting …")
        self.state.running = False
        self.listener.stop()
        icon.stop()
