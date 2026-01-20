# Dream Reverb

```
    ____                            ____                      __  
   / __ \________  ____ _____ ___  / __ \___ _   _____  _____/ /_ 
  / / / / ___/ _ \/ __ `/ __ `__ \/ /_/ / _ \ | / / _ \/ ___/ __ \
 / /_/ / /  /  __/ /_/ / / / / / / _, _/  __/ |/ /  __/ /  / /_/ /
/_____/_/   \___/\__,_/_/ /_/ /_/_/ |_|\___/|___/\___/_/  /_.___/ 
```

A small CLI that generates slow, reverbed versions of music. It applies a low‑pass filter, distance gain, delay, reverb, tremolo, and then slows the audio down. Output is MP3 by default (highest quality), with a WAV flag for lossless.

## Requirements

- Python 3.12+
- `uv`

## Setup

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Options

```bash
python main.py --pitch up
python main.py --pitch down
python main.py --extra-slow
python main.py --fast
python main.py --wav
python main.py --output /path/to/out.mp3
python main.py --output /path/to/out.wav
```

## What it does

- Low‑pass filter (muffle highs)
- Gain reduction (distance)
- Delay + reverb (space)
- Tremolo (soft motion)
- Time‑stretch (slowdown)
- Optional pitch shift (+/- 4 semitones)

## Output

- Default: MP3 at quality 320 kbps
- Lossless: `--wav`
- Custom: `--output` to choose a full path (must end with .mp3 or .wav)

## Notes

- Pitch is preserved by default; use `--pitch up/down` to shift by 1/3 octave.
- Output file is written next to the input as `<stem>_reverb_slow.(mp3|wav)` unless `--output` is provided.
