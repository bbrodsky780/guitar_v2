# Guitar Trainer Game

This small project provides a basic desktop application to help practice guitar chords. The program listens to your microphone, displays which chord to play, waits until the chord is recognized, and times how quickly you move from one chord to the next.

## Features

- Calibration step to capture how your guitar sounds for each chord.
- Simple countdown before recording each chord.
- Tracks the total time to play a series of chords and keeps your best score.
- Minimal Tkinter interface.

## Requirements

- Python 3.8+
- `numpy`
- `sounddevice` (for audio capture)
- `tkinter` (usually included with Python on most systems)

Install dependencies with:

```bash
pip install numpy sounddevice
```

## Running

```
python guitar_game.py
```

When the window appears:

1. Click **Calibrate** and follow the prompts to record each chord.
2. After calibration, click **Start Game** to begin playing. The app will display a chord name, count down, and listen until the correct chord is detected.
3. After all chords are played, your total time is shown. Try to beat your record!

Note: Proper chord recognition depends on a good microphone and quiet surroundings. This is a very simple frequency-based matcher and may not work perfectly for all setups.
