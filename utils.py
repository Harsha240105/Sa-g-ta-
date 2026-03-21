"""
Utility helpers for file handling, audio conversion, and optional voice-over mixing.
"""

from __future__ import annotations

import io
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable

import librosa
from pydub import AudioSegment


def ensure_directories(directories: Iterable[Path]) -> None:
    """
    Create folders if they do not already exist.
    """
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """
    Keep filename safe and simple for local storage.
    """
    path = Path(filename)
    clean_stem = re.sub(r"[^a-zA-Z0-9_-]+", "_", path.stem).strip("_")
    clean_stem = clean_stem or "audio_file"
    clean_suffix = path.suffix.lower() if path.suffix else ".wav"
    return f"{clean_stem}{clean_suffix}"


def save_uploaded_file(uploaded_file, upload_dir: Path) -> Path:
    """
    Save Streamlit uploaded file to the uploads folder with a timestamp.
    """
    ensure_directories([upload_dir])
    safe_name = sanitize_filename(uploaded_file.name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_path = upload_dir / f"{timestamp}_{safe_name}"
    saved_path.write_bytes(bytes(uploaded_file.getbuffer()))
    return saved_path


def convert_to_wav(input_path: Path) -> Path:
    """
    Convert an input audio file to WAV if it is not already WAV.
    """
    input_path = Path(input_path)
    if input_path.suffix.lower() == ".wav":
        return input_path

    wav_path = input_path.with_suffix(".wav")
    audio = AudioSegment.from_file(input_path)
    audio.export(wav_path, format="wav")
    return wav_path


def read_binary_file(file_path: Path) -> bytes:
    """
    Read file bytes for Streamlit audio playback.
    """
    return Path(file_path).read_bytes()


def get_streamlit_audio_format(audio_path: Path) -> str:
    """
    Return best MIME format string for Streamlit audio component.
    """
    suffix = Path(audio_path).suffix.lower()
    if suffix == ".mp3":
        return "audio/mpeg"
    return "audio/wav"


def get_audio_duration_seconds(audio_path: Path) -> float:
    """
    Return audio length in seconds.
    """
    return float(librosa.get_duration(path=str(audio_path)))


def mix_voice_over_instrumental(
    instrumental_path: Path, voice_bytes: bytes, output_dir: Path
) -> Path:
    """
    Overlay recorded user voice on top of instrumental and export as WAV.
    """
    ensure_directories([output_dir])

    instrumental_audio = AudioSegment.from_file(instrumental_path)
    voice_audio = AudioSegment.from_file(io.BytesIO(voice_bytes), format="wav")

    # Slightly increase voice volume so it is easier to hear.
    boosted_voice = voice_audio + 4
    mixed_audio = instrumental_audio.overlay(boosted_voice, position=0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mixed_path = output_dir / f"voiceover_mix_{timestamp}.wav"
    mixed_audio.export(mixed_path, format="wav")
    return mixed_path
