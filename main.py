from __future__ import annotations

from pathlib import Path

import click
import numpy as np
from pedalboard import Delay, Gain, LowpassFilter, Pedalboard, Reverb
from pedalboard.io import AudioFile
from pedalboard_native.utils import time_stretch
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

_BANNER = r"""
    ____                            ____                      __  
   / __ \________  ____ _____ ___  / __ \___ _   _____  _____/ /_ 
  / / / / ___/ _ \/ __ `/ __ `__ \/ /_/ / _ \ | / / _ \/ ___/ __ \
 / /_/ / /  /  __/ /_/ / / / / / / _, _/  __/ |/ /  __/ /  / /_/ /
/_____/_/   \___/\__,_/_/ /_/ /_/_/ |_|\___/|___/\___/_/  /_.___/ 
"""

_LOFI_NIGHT = {
    "cutoff_hz": 1200.0,
    "gain_db": -6.0,
    "reverb": dict(room_size=0.6, damping=0.5, wet_level=0.25, dry_level=0.75, width=0.9),
    "delay": dict(delay_seconds=0.28, feedback=0.25, mix=0.18),
    "tremolo": dict(rate_hz=3.5, depth=0.35),
    "speed": 0.7,
}


def _apply_tremolo(audio: np.ndarray, samplerate: float, rate_hz: float, depth: float) -> np.ndarray:
    if depth <= 0:
        return audio
    num_samples = audio.shape[-1]
    t = np.arange(num_samples, dtype=np.float32) / float(samplerate)
    lfo = 1.0 - depth * (0.5 * (1.0 + np.sin(2.0 * np.pi * rate_hz * t)))
    return audio * lfo


@click.command()
@click.option(
    "--input-path",
    "input_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    prompt="Enter path to audio file",
)
@click.option(
    "--pitch",
    type=click.Choice(["down", "none", "up"]),
    default="none",
    show_default=True,
    help="Pitch shift by 1/3 octave (down or up) or keep unchanged.",
)
@click.option(
    "--wav",
    is_flag=True,
    help="Write WAV (lossless) instead of MP3.",
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Custom output file path (overrides default name).",
)
@click.option(
    "--extra-slow",
    is_flag=True,
    help="Slow down more than the default.",
)
@click.option(
    "--fast",
    is_flag=True,
    help="Speed up compared to the default.",
)
def main(
    input_path: Path,
    pitch: str,
    wav: bool,
    output_path: Path | None,
    extra_slow: bool,
    fast: bool,
) -> None:
    console = Console()
    console.print(_BANNER, style="bold plum2")
    console.print()

    in_path = input_path.expanduser().resolve()
    if output_path is not None:
        out_path = output_path.expanduser().resolve()
        ext = out_path.suffix.lower().lstrip(".")
        if ext == "wav":
            wav = True
        elif ext == "mp3":
            wav = False
        else:
            raise click.ClickException("Output file must end with .mp3 or .wav")
    else:
        ext = "wav" if wav else "mp3"
        out_path = in_path.with_name(f"{in_path.stem}_reverb_slow.{ext}")

    reverb = Reverb(**_LOFI_NIGHT["reverb"])
    delay = Delay(**_LOFI_NIGHT["delay"])
    muffle = LowpassFilter(cutoff_frequency_hz=_LOFI_NIGHT["cutoff_hz"])
    distance = Gain(gain_db=_LOFI_NIGHT["gain_db"])
    board = Pedalboard([muffle, distance, delay, reverb])
    speed = _LOFI_NIGHT["speed"]
    if extra_slow and fast:
        raise click.ClickException("Choose only one of --extra-slow or --fast.")
    if extra_slow:
        speed = 0.6
    elif fast:
        speed = 0.85

    with Progress(
        SpinnerColumn(style="plum2"),
        TextColumn("[progress.description]{task.description}", style="light_cyan3"),
        BarColumn(style="grey39", complete_style="bright_yellow"),
        TextColumn("{task.completed}/{task.total}", style="bright_yellow"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Reading audio", total=4)

        with AudioFile(str(in_path)) as f:
            audio = f.read(f.frames)
            samplerate = f.samplerate
            num_channels = f.num_channels
        progress.update(task, advance=1, description="Applying effects")

        processed = board.process(audio, samplerate)
        processed = _apply_tremolo(processed, samplerate, **_LOFI_NIGHT["tremolo"])
        progress.update(task, advance=1, description="Time stretching")

        semitones = 0
        if pitch == "up":
            semitones = 4
        elif pitch == "down":
            semitones = -4

        slowed = time_stretch(
            processed,
            samplerate,
            stretch_factor=speed,
            pitch_shift_in_semitones=semitones,
        )
        progress.update(task, advance=1, description="Writing output")

        audiofile_kwargs = {}
        if not wav:
            audiofile_kwargs["quality"] = 320

        with AudioFile(
            str(out_path),
            "w",
            samplerate,
            num_channels=num_channels,
            **audiofile_kwargs,
        ) as out_f:
            out_f.write(slowed)
        progress.update(task, advance=1, description="Done")

    console.print(f"Wrote: [bold pale_turquoise1]{out_path}[/bold pale_turquoise1]")


if __name__ == "__main__":
    main()
