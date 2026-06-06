"""
Core audio separation logic using Spleeter.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import soundfile as sf
from spleeter.separator import Separator

from utils import ensure_directories, get_audio_duration_seconds


_SEPARATOR_INSTANCE = None


def get_separator() -> Separator:
    """
    Load the Spleeter 2-stem model once and reuse it.
    """
    global _SEPARATOR_INSTANCE
    if _SEPARATOR_INSTANCE is None:
        _SEPARATOR_INSTANCE = Separator("spleeter:2stems")
    return _SEPARATOR_INSTANCE


def normalize_wav(audio_path: Path, target_peak: float = 0.95) -> None:
    """
    Normalize WAV audio to reduce clipping and keep loudness stable.
    """
    samples, sample_rate = sf.read(str(audio_path))
    peak = np.max(np.abs(samples))

    if peak > 0:
        normalized = (samples / peak) * target_peak
        sf.write(str(audio_path), normalized, sample_rate)


def separate_audio_file(input_audio_path: Path, output_root: Path) -> dict:
    """
    Separate the input file into vocals and instrumental tracks.
    Returns all key output paths and metadata.
    """
    input_audio_path = Path(input_audio_path)
    output_root = Path(output_root)

    vocals_dir = output_root / "vocals"
    instrumental_dir = output_root / "instrumental"
    temp_spleeter_dir = output_root / "_spleeter_temp"
    ensure_directories([vocals_dir, instrumental_dir, temp_spleeter_dir])

    separator = get_separator()
    separator.separate_to_file(
        str(input_audio_path),
        str(temp_spleeter_dir),
        codec="wav",
    )

    temp_track_dir = temp_spleeter_dir / input_audio_path.stem
    source_vocals = temp_track_dir / "vocals.wav"
    source_instrumental = temp_track_dir / "accompaniment.wav"

    if not source_vocals.exists() or not source_instrumental.exists():
        raise FileNotFoundError(
            "Spleeter output files were not found. Check input file and model setup."
        )

    vocals_output_path = vocals_dir / f"{input_audio_path.stem}_vocals.wav"
    instrumental_output_path = (
        instrumental_dir / f"{input_audio_path.stem}_instrumental.wav"
    )

    shutil.copy2(source_vocals, vocals_output_path)
    shutil.copy2(source_instrumental, instrumental_output_path)

    # Clean up Spleeter's per-file staging folder after copying the final tracks.
    shutil.rmtree(temp_track_dir, ignore_errors=True)

    normalize_wav(vocals_output_path)
    normalize_wav(instrumental_output_path)

    return {
        "input_path": str(input_audio_path),
        "vocals_path": str(vocals_output_path),
        "instrumental_path": str(instrumental_output_path),
        "duration_seconds": round(get_audio_duration_seconds(input_audio_path), 2),
    }

