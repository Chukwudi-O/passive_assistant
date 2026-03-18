"""
Overlay Indicator
=================
A tiny always-on-top window at the top-left of the screen that shows the
assistant's current state without ever stealing focus from the user.

States
------
hidden      idle, waiting for wake phrase          (window invisible)
listening   wake phrase heard, recording speech    (blue pulse)
thinking    sending to OpenAI / awaiting reply     (amber spinner)
speaking    playing TTS audio                      (green pulse)

Windows-specific focus tricks
------------------------------
  wm_attributes("-toolwindow", True)   -> no taskbar entry, no activation on click
  wm_attributes("-topmost", True)      -> always on top
  overrideredirect(True)               -> no title bar / border
  transparentcolor                     -> chroma-key background -> round feel
"""

import tkinter as tk
import threading
import math
import time

# ── visual config ──────────────────────────────────────────────────────────────
WINDOW_SIZE = 52
MARGIN_X    = 16
MARGIN_Y    = 16
DOT_R       = 15      # max radius of the animated dot
FPS         = 30

COLORS = {
    "listening": "#4FC3F7",
    "thinking":  "#FFB300",
    "speaking":  "#66BB6A",
}
CHROMA = "#010101"   # transparent background key colour


class OverlayIndicator:
    def __init__(self, state):
        self.state  = state
        self._mode  = "hidden"
        self._lock  = threading.Lock()
        self._root  = None
        self._canvas = None
        self._angle = 0.0
        self._running = True
        self._stop_requested = False

    # ── public API — callable from any thread ──────────────────────────────────

    def show_listening(self):
        self._set_mode("listening")

    def show_thinking(self):
        self._set_mode("thinking")

    def show_speaking(self):
        self._set_mode("speaking")

    def hide(self):
        self._set_mode("hidden")

    def _set_mode(self, mode):
        with self._lock:
            self._mode = mode
        if self._root:
            # thread-safe poke into tkinter's event loop
            try:
                self._root.event_generate("<<Repaint>>", when="tail")
            except Exception:
                pass

    # ── tkinter main loop (runs in a dedicated daemon thread) ─────────────────

    def run(self):
        self._root = tk.Tk()
        root = self._root

        root.overrideredirect(True)
        root.wm_attributes("-topmost", True)
        root.wm_attributes("-toolwindow", True)       # no taskbar, no focus steal
        root.wm_attributes("-transparentcolor", CHROMA)
        root.configure(bg=CHROMA)
        root.resizable(False, False)
        root.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}+{MARGIN_X}+{MARGIN_Y}")

        self._canvas = tk.Canvas(
            root, width=WINDOW_SIZE, height=WINDOW_SIZE,
            bg=CHROMA, highlightthickness=0
        )
        self._canvas.pack()

        # Ignore the custom event — the animation loop handles repainting
        root.bind("<<Repaint>>", lambda e: None)

        self._animate()
        root.mainloop()

    # ── animation loop ─────────────────────────────────────────────────────────

    def _animate(self):
        if not self._root:
            return

        t  = time.time()
        with self._lock:
            mode = self._mode

        c  = self._canvas
        cx = cy = WINDOW_SIZE // 2

        c.delete("all")

        if mode == "thinking":
            self._angle = (self._angle + 7) % 360
            self._draw_spinner(c, cx, cy, COLORS["thinking"])

        elif mode in ("listening", "speaking"):
            color = COLORS[mode]
            pulse = (math.sin(t * 4.5) + 1) / 2      # 0 → 1 → 0
            r     = int(DOT_R * (0.68 + 0.32 * pulse))

            # soft glow ring
            gr = r + 7
            gc = self._blend(color, CHROMA, 0.4)
            c.create_oval(cx - gr, cy - gr, cx + gr, cy + gr,
                          fill=gc, outline="")
            # solid dot
            c.create_oval(cx - r, cy - r, cx + r, cy + r,
                          fill=color, outline="")

        self._root.after(int(1000 / FPS), self._animate)

    def _draw_spinner(self, canvas, cx, cy, color):
        r = DOT_R
        faint = self._blend(color, CHROMA, 0.7)
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           outline=faint, width=3)
        start = self._angle
        canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                          start=start, extent=130,
                          outline=color, width=3, style=tk.ARC)

    @staticmethod
    def _blend(hex_a, hex_b, t):
        """Blend hex_a → hex_b by factor t (0=a, 1=b)."""
        def p(h):
            h = h.lstrip("#")
            return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        r1, g1, b1 = p(hex_a)
        r2, g2, b2 = p(hex_b)
        return "#{:02x}{:02x}{:02x}".format(
            int(r1 + (r2 - r1) * t),
            int(g1 + (g2 - g1) * t),
            int(b1 + (b2 - b1) * t),
        )
