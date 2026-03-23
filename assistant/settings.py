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
        

        ttk.Label(frame, text="Wake Phrase:").grid(row=row, column=0, sticky="w", **pad)
        model_value = state.get("wake_phrase", "")
        
        self._wake_phrase_combobox = ttk.Combobox(frame, width=30,
                                  values=["hey jarvis", "alexa"])
        self._wake_phrase_combobox.grid(row=row, column=1, sticky="ew", **pad)
        self._wake_phrase_combobox.set(model_value)
        
        row += 1
        

        # ── API key ───────────────────────────────────────────────────────────
        ttk.Label(frame, text="Gemini API key:").grid(row=row, column=0, sticky="w", **pad)
        api_key_value = state.get("gemini_api_key", "")
        
        self._key_entry = ttk.Entry(frame, width=32, show="*")
        self._key_entry.grid(row=row, column=1, sticky="ew", **pad)
        self._key_entry.insert(0, api_key_value)
        
        row += 1

        # ── Model ─────────────────────────────────────────────────────────────
        ttk.Label(frame, text="Gemini model:").grid(row=row, column=0, sticky="w", **pad)
        model_value = state.get("gemini_model", "")
        
        self._model_box = ttk.Combobox(frame, width=30,
                                  values=["gemini-pro-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"])
        self._model_box.grid(row=row, column=1, sticky="ew", **pad)
        self._model_box.set(model_value)
        
        row += 1

        # ── System prompt ─────────────────────────────────────────────────────
        ttk.Label(frame, text="System prompt:").grid(row=row, column=0, sticky="nw", **pad)
        prompt_value = state.get("system_prompt", "")
        
        self._prompt_text = tk.Text(frame, width=40, height=4, wrap="word")
        self._prompt_text.insert("1.0", prompt_value)
        
        self._prompt_text.grid(row=row, column=1, columnspan=2, sticky="ew", **pad)

        row += 1

        # ── TTS Rate ───────────────────────────────────────────────────────────
        ttk.Label(frame, text="TTS speed (wpm):").grid(row=row, column=0, sticky="w", **pad)
        tts_rate_value = state.get("tts_rate", "")
        
        self._tts_rate_entry = ttk.Entry(frame, width=32)
        self._tts_rate_entry.grid(row=row, column=1, sticky="ew", **pad)
        self._tts_rate_entry.insert(0, tts_rate_value)
        
        row += 1

        # ── TTS Volume ───────────────────────────────────────────────────────────
        ttk.Label(frame, text="TTS volume:").grid(row=row, column=0, sticky="w", **pad)
        tts_volume_value = state.get("tts_volume", "")
        
        self._tts_volume_entry = ttk.Entry(frame, width=32)
        self._tts_volume_entry.grid(row=row, column=1, sticky="ew", **pad)
        self._tts_volume_entry.insert(0, tts_volume_value)
        
        row += 1

        # ── TTS Voice Index ───────────────────────────────────────────────────────────
        ttk.Label(frame, text="TTS voice index:").grid(row=row, column=0, sticky="w", **pad)
        tts_voice_value = state.get("tts_voice_index", "")
        
        self._tts_voice_entry = ttk.Entry(frame, width=32)
        self._tts_voice_entry.grid(row=row, column=1, sticky="ew", **pad)
        self._tts_voice_entry.insert(0, tts_voice_value)
        
        row += 1

       # ── Silence Threshold ───────────────────────────────────────────────────────────
        ttk.Label(frame, text="Silence threshold:").grid(row=row, column=0, sticky="w", **pad)
        thresh_value = state.get("silence_threshold", "")
        
        self._thresh_entry = ttk.Entry(frame, width=32)
        self._thresh_entry.grid(row=row, column=1, sticky="ew", **pad)
        self._thresh_entry.insert(0, thresh_value)
        
        row += 1

        # ── Silence Duration ───────────────────────────────────────────────────────────
        ttk.Label(frame, text="Silence duration:").grid(row=row, column=0, sticky="w", **pad)
        duration_value = state.get("silence_duration", "")
        
        self._duration_entry = ttk.Entry(frame, width=32)
        self._duration_entry.grid(row=row, column=1, sticky="ew", **pad)
        self._duration_entry.insert(0, duration_value)
        
        row += 1

        # ── MAX Record ───────────────────────────────────────────────────────────
        ttk.Label(frame, text="MAX Record:").grid(row=row, column=0, sticky="w", **pad)
        max_record_value = state.get("max_record_seconds", "")
        
        self._max_record_entry = ttk.Entry(frame, width=32)
        self._max_record_entry.grid(row=row, column=1, sticky="ew", **pad)
        self._max_record_entry.insert(0, max_record_value)
        
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
        self.state.set("wake_phrase",        self._wake_phrase_combobox.get())
        self.state.set("gemini_api_key",     self._key_entry.get())
        # print(f"[Settings] Saved API key: {api_key[:20]}..." if api_key else "[Settings] Saved empty API key")
        self.state.set("gemini_model",       self._model_box.get())
        self.state.set("tts_rate",           float(self._tts_rate_entry.get()))
        self.state.set("tts_volume",         float(self._tts_volume_entry.get()))
        self.state.set("tts_voice_index",    int(self._tts_voice_entry.get()))
        self.state.set("silence_threshold",  float(self._thresh_entry.get()))
        self.state.set("silence_duration",   float(self._duration_entry.get()))
        self.state.set("max_record_seconds", int(self._max_record_entry.get()))
        self.state.set("system_prompt",      self._prompt_text.get("1.0", "end").strip())
    
        messagebox.showinfo("Saved", "Settings saved. Restart the application to apply changes.", parent=self._win)
        self._quit()

    def _quit(self):
        self._win.destroy()