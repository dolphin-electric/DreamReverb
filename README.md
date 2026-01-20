# DreamReverb

A small CLI that generates slow, reverbed versions of music. It applies a low‑pass filter, distance gain, delay, reverb, tremolo, and then slows the audio down. Output is MP3 by default (highest quality), with a WAV flag for lossless.

## Requirements

- Python 3.12+

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
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
python main.py --output /path/to/folder
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
- Custom folder: `--output` writes to that directory with the default filename

## Notes

- Pitch is preserved by default; use `--pitch up/down` to shift by 1/3 octave.
- Output file is written as `<stem>_reverb_slow.(mp3|wav)` in the input folder unless `--output` is provided.
