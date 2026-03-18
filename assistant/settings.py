"""
Settings dialog.
Opens a Tk Toplevel for editing config. Uses wm_attributes("-toolwindow", True)
so it doesn't grab persistent focus from the foreground application —
the user can click away and the window simply sits in the background.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class SettingsDialog:
    def __init__(self, parent_root, state, listener):
        self.state    = state
        self.listener = listener
        
        # Debug: Print the entire state config
        

        win = tk.Toplevel(parent_root)
        win.title("Voice Assistant — Settings")
        win.resizable(False, False)
        # win.wm_attributes("-toolwindow", True)   # no persistent focus grab
        win.wm_attributes("-topmost",    True)
        win.grab_release()                        # don't capture all events

        # ── padding helper ────────────────────────────────────────────────────
        pad = {"padx": 10, "pady": 6}

        frame = ttk.Frame(win, padding=14)
        frame.grid(sticky="nsew", row=0, column=0)
        
        # Configure window grid to allow frame to expand
        win.grid_rowconfigure(0, weight=1)
        win.grid_columnconfigure(0, weight=1)

        row = 0

        # ── Wake phrase ───────────────────────────────────────────────────────
        ttk.Label(frame, text="Wake phrase:").grid(row=row, column=0, sticky="w", **pad)
        wake_value = state.get("wake_phrase", "Chat.")
        
        self._wake_var = tk.StringVar()
        wake_entry = ttk.Entry(frame, textvariable=self._wake_var, width=32)
        wake_entry.grid(row=row, column=1, sticky="ew", **pad)
        wake_entry.insert(0, wake_value)
        
        row += 1
        

        # ── API key ───────────────────────────────────────────────────────────
        ttk.Label(frame, text="Gemini API key:").grid(row=row, column=0, sticky="w", **pad)
        api_key_value = state.get("gemini_api_key", "")
        
        self._key_var = tk.StringVar()
        key_entry = ttk.Entry(frame, textvariable=self._key_var, width=32, show="*")
        key_entry.grid(row=row, column=1, sticky="ew", **pad)
        key_entry.insert(0, api_key_value)
        
        row += 1

        # ── Model ─────────────────────────────────────────────────────────────
        ttk.Label(frame, text="Gemini model:").grid(row=row, column=0, sticky="w", **pad)
        model_value = state.get("gemini_model", "gemini-pro-2.0-flash")
        
        self._model_var = tk.StringVar()
        model_box = ttk.Combobox(frame, textvariable=self._model_var, width=30,
                                  values=["gemini-pro-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"])
        model_box.grid(row=row, column=1, sticky="ew", **pad)
        model_box.set(model_value)
        
        row += 1

        # ── TTS rate ──────────────────────────────────────────────────────────
        ttk.Label(frame, text="TTS speed (wpm):").grid(row=row, column=0, sticky="w", **pad)
        rate_value = state.get("tts_rate", 175)

        self._rate_var = tk.IntVar()
        rate_scale = ttk.Scale(frame, variable=self._rate_var, from_=100, to=300,
                  orient="horizontal", length=200)
        rate_scale.grid(row=row, column=1, sticky="ew", **pad)
        self._rate_var.set(rate_value)
      
        row += 1

       

        # ── Silence threshold ─────────────────────────────────────────────────
        ttk.Label(frame, text="Mic sensitivity:").grid(row=row, column=0, sticky="w", **pad)
        thresh_value = state.get("silence_threshold", 700)
        
        self._thresh_var = tk.IntVar()
        thresh_scale = ttk.Scale(frame, variable=self._thresh_var, from_=200, to=2000,
                  orient="horizontal", length=200)
        thresh_scale.grid(row=row, column=1, sticky="ew", **pad)
        self._thresh_var.set(thresh_value)
        
        ttk.Label(frame, text="(lower = more sensitive)").grid(row=row, column=2, sticky="w", **pad)
        row += 1
        

        # ── System prompt ─────────────────────────────────────────────────────
        ttk.Label(frame, text="System prompt:").grid(row=row, column=0, sticky="nw", **pad)
        prompt_value = state.get("system_prompt", "")
        
        self._prompt_text = tk.Text(frame, width=40, height=4, wrap="word")
        self._prompt_text.insert("1.0", prompt_value)
        
        self._prompt_text.grid(row=row, column=1, columnspan=2, sticky="ew", **pad)
        row += 1

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=10)
        ttk.Button(btn_frame, text="Save",   command=self._save).pack(side="left",  padx=6)
        ttk.Button(btn_frame, text="Cancel", command=self._quit).pack(side="left", padx=6)
        
        self._win    = win

        # Centre on screen
        try:
            win.update()  # Force full layout calculation
            w, h = win.winfo_width(), win.winfo_height()
            sw   = win.winfo_screenwidth()
            sh   = win.winfo_screenheight()
            # print(f"[Settings] Window size: {w}x{h}, Screen: {sw}x{sh}")
            win.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")
            print(f"[Settings] Window opened successfully")
        except Exception as e:
            print(f"[Settings] Warning: Could not center window: {e}")

    def _save(self):
        self.state.set("wake_phrase",        self._wake_var.get().strip())
        api_key = self._key_var.get().strip()
        self.state.set("gemini_api_key",     api_key)
        print(f"[Settings] Saved API key: {api_key[:20]}..." if api_key else "[Settings] Saved empty API key")
        self.state.set("gemini_model",       self._model_var.get().strip())
        self.state.set("tts_rate",           int(self._rate_var.get()))
        self.state.set("silence_threshold",  int(self._thresh_var.get()))
        self.state.set("system_prompt",      self._prompt_text.get("1.0", "end").strip())


        messagebox.showinfo("Saved", "Settings saved.", parent=self._win)
        self._win.destroy()

    def _quit(self):
        self._win.destroy()