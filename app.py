"""Simple desktop speech-to-text application."""

from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import speech_recognition as sr


class SpeechToTextApp:
    """Tkinter interface for transcribing audio recordings."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Speech-to-Text Transcription")
        self.root.geometry("760x520")
        self.root.minsize(620, 420)

        self.audio_path: Path | None = None
        self.file_label = tk.StringVar(value="No audio file selected")
        self.status = tk.StringVar(value="Ready")

        self._build_interface()

    def _build_interface(self) -> None:
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Speech-to-Text Transcription",
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor=tk.W)
        ttk.Label(
            container,
            text="Select an audio recording and convert spoken words into text.",
        ).pack(anchor=tk.W, pady=(4, 18))

        file_frame = ttk.Frame(container)
        file_frame.pack(fill=tk.X)

        ttk.Button(
            file_frame,
            text="Choose Audio File",
            command=self.choose_audio,
        ).pack(side=tk.LEFT)
        ttk.Label(file_frame, textvariable=self.file_label).pack(
            side=tk.LEFT, padx=12, fill=tk.X, expand=True
        )

        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=14)

        self.transcribe_button = ttk.Button(
            actions,
            text="Transcribe",
            command=self.start_transcription,
            state=tk.DISABLED,
        )
        self.transcribe_button.pack(side=tk.LEFT)
        ttk.Button(actions, text="Copy Text", command=self.copy_text).pack(
            side=tk.LEFT, padx=8
        )
        ttk.Button(actions, text="Save as TXT", command=self.save_text).pack(
            side=tk.LEFT
        )
        ttk.Button(actions, text="Clear", command=self.clear_text).pack(
            side=tk.RIGHT
        )

        text_frame = ttk.Frame(container)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.output = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            padx=10,
            pady=10,
            undo=True,
        )
        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.output.yview
        )
        self.output.configure(yscrollcommand=scrollbar.set)
        self.output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(container, textvariable=self.status).pack(
            anchor=tk.W, pady=(10, 0)
        )

    def choose_audio(self) -> None:
        filename = filedialog.askopenfilename(
            title="Choose an audio recording",
            filetypes=[
                ("Supported audio", "*.wav *.aiff *.aif *.flac"),
                ("WAV files", "*.wav"),
                ("AIFF files", "*.aiff *.aif"),
                ("FLAC files", "*.flac"),
                ("All files", "*.*"),
            ],
        )
        if not filename:
            return

        self.audio_path = Path(filename)
        self.file_label.set(self.audio_path.name)
        self.status.set("Audio selected. Click Transcribe to begin.")
        self.transcribe_button.configure(state=tk.NORMAL)

    def start_transcription(self) -> None:
        if self.audio_path is None:
            messagebox.showwarning("No audio", "Please choose an audio file first.")
            return

        self.transcribe_button.configure(state=tk.DISABLED)
        self.status.set("Listening and transcribing…")
        threading.Thread(target=self._transcribe, daemon=True).start()

    def _transcribe(self) -> None:
        recognizer = sr.Recognizer()

        try:
            with sr.AudioFile(str(self.audio_path)) as source:
                audio = recognizer.record(source)

            # Google Web Speech API is convenient for a small educational project.
            # It requires an active internet connection.
            transcription = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            self.root.after(
                0,
                self._show_error,
                "Speech was not clear enough to understand.",
            )
        except sr.RequestError as error:
            self.root.after(
                0,
                self._show_error,
                f"Speech recognition service error: {error}",
            )
        except (ValueError, OSError) as error:
            self.root.after(
                0,
                self._show_error,
                f"Could not read this audio file: {error}",
            )
        except Exception as error:
            self.root.after(0, self._show_error, f"Unexpected error: {error}")
        else:
            self.root.after(0, self._show_result, transcription)

    def _show_result(self, transcription: str) -> None:
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, transcription)
        self.status.set("Transcription complete.")
        self.transcribe_button.configure(state=tk.NORMAL)

    def _show_error(self, message: str) -> None:
        self.status.set("Transcription failed.")
        self.transcribe_button.configure(state=tk.NORMAL)
        messagebox.showerror("Transcription error", message)

    def copy_text(self) -> None:
        text = self.output.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Nothing to copy", "There is no text to copy yet.")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status.set("Text copied to clipboard.")

    def save_text(self) -> None:
        text = self.output.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Nothing to save", "There is no text to save yet.")
            return

        filename = filedialog.asksaveasfilename(
            title="Save transcription",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if filename:
            Path(filename).write_text(text, encoding="utf-8")
            self.status.set(f"Saved to {Path(filename).name}.")

    def clear_text(self) -> None:
        self.output.delete("1.0", tk.END)
        self.status.set("Text cleared.")


def main() -> None:
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    SpeechToTextApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
