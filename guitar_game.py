import random
import time
import threading
from dataclasses import dataclass
from typing import List, Dict

import numpy as np
try:
    import sounddevice as sd
except ImportError:
    sd = None

@dataclass
class Fingerprint:
    freqs: np.ndarray

class ChordTrainer:
    def __init__(self, sample_rate: int = 44100, duration: float = 1.0, top_n: int = 5):
        self.sample_rate = sample_rate
        self.duration = duration
        self.top_n = top_n
        self.fingerprints: Dict[str, Fingerprint] = {}
        self.best_time: float | None = None

    def record_audio(self) -> np.ndarray:
        if sd is None:
            raise RuntimeError("sounddevice is required for audio capture")
        recording = sd.rec(int(self.sample_rate * self.duration),
                           samplerate=self.sample_rate, channels=1, blocking=True)
        return np.squeeze(recording)

    def compute_fingerprint(self, audio: np.ndarray) -> Fingerprint:
        fft = np.fft.rfft(audio)
        mag = np.abs(fft)
        freqs = np.fft.rfftfreq(len(audio), 1 / self.sample_rate)
        idx = np.argsort(mag)[-self.top_n:]
        return Fingerprint(freqs=np.sort(freqs[idx]))

    def calibrate_chord(self, chord: str) -> None:
        audio = self.record_audio()
        self.fingerprints[chord] = self.compute_fingerprint(audio)

    def detect_chord(self, chord: str) -> bool:
        target = self.fingerprints.get(chord)
        if target is None:
            return False
        audio = self.record_audio()
        fp = self.compute_fingerprint(audio)
        diff = np.mean(np.abs(fp.freqs - target.freqs))
        return diff < 5.0  # hz tolerance

class GameUI:
    def __init__(self, chords: List[str]):
        from tkinter import Tk, Label, Button, StringVar
        self.trainer = ChordTrainer()
        self.chords = chords
        self.root = Tk()
        self.root.title("Guitar Trainer")
        self.msg = StringVar()
        self.label = Label(self.root, textvariable=self.msg, font=("Helvetica", 16))
        self.label.pack(pady=20)
        self.btn_cal = Button(self.root, text="Calibrate", command=self.calibrate)
        self.btn_cal.pack(pady=5)
        self.btn_start = Button(self.root, text="Start Game", command=self.start_game, state="disabled")
        self.btn_start.pack(pady=5)
        self.msg.set("Welcome to Guitar Trainer!")

    def countdown(self, secs: int) -> None:
        for i in range(secs, 0, -1):
            self.msg.set(f"{i}...")
            self.root.update()
            time.sleep(1)

    def calibrate(self) -> None:
        def _cal():
            for chord in self.chords:
                self.msg.set(f"Play {chord} after countdown")
                self.countdown(3)
                self.trainer.calibrate_chord(chord)
                self.msg.set(f"{chord} captured!")
                time.sleep(1)
            self.msg.set("Calibration done.")
            self.btn_start.configure(state="normal")
        threading.Thread(target=_cal).start()

    def wait_for_chord(self, chord: str) -> float:
        start = time.time()
        while not self.trainer.detect_chord(chord):
            self.msg.set(f"Waiting for {chord}...")
            self.root.update()
            time.sleep(0.1)
        return time.time() - start

    def start_game(self) -> None:
        def _play():
            random.shuffle(self.chords)
            total = 0.0
            for chord in self.chords:
                self.msg.set(f"Play {chord}!")
                self.countdown(3)
                elapsed = self.wait_for_chord(chord)
                total += elapsed
                self.msg.set(f"{chord} OK! {elapsed:.2f}s")
                time.sleep(1)
            if self.trainer.best_time is None or total < self.trainer.best_time:
                diff = 0 if self.trainer.best_time is None else self.trainer.best_time - total
                self.trainer.best_time = total
                self.msg.set(f"Time! {total:.2f}s. New record by {diff:.2f}s!")
            else:
                self.msg.set(f"Time! {total:.2f}s. Best: {self.trainer.best_time:.2f}s")
        threading.Thread(target=_play).start()

    def run(self) -> None:
        self.root.mainloop()

if __name__ == "__main__":
    chords = ["A", "B", "C", "D", "E"]
    ui = GameUI(chords)
    ui.run()
