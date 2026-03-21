"""
Streamlit app for AI-based vocal and instrumental separation.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from audio_processing import separate_audio_file
from utils import (
    convert_to_wav,
    ensure_directories,
    get_audio_duration_seconds,
    get_streamlit_audio_format,
    mix_voice_over_instrumental,
    read_binary_file,
    save_uploaded_file,
)


# ---------- Project folders ----------
BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
VOCALS_DIR = OUTPUTS_DIR / "vocals"
INSTRUMENTAL_DIR = OUTPUTS_DIR / "instrumental"
VOICEOVER_DIR = OUTPUTS_DIR / "voiceovers"

ensure_directories([UPLOADS_DIR, OUTPUTS_DIR, VOCALS_DIR, INSTRUMENTAL_DIR, VOICEOVER_DIR])


# ---------- Streamlit page setup ----------
st.set_page_config(page_title="AI Vocal & Instrument Separation", layout="centered")
st.title("AI-Based Vocal & Instrument Separation for Interactive Music Experience")
st.write(
    "Upload an MP3/WAV file, separate vocals and instrumental using Spleeter, "
    "and optionally record your voice over the instrumental."
)

if "processed_result" not in st.session_state:
    st.session_state.processed_result = None


# ---------- Upload section ----------
uploaded_file = st.file_uploader("Upload Audio File", type=["mp3", "wav"])

if uploaded_file is not None:
    st.subheader("Original Audio Preview")
    st.audio(uploaded_file.getvalue(), format=uploaded_file.type or "audio/wav")

    if st.button("Process Audio", type="primary"):
        status_placeholder = st.empty()
        try:
            status_placeholder.info("Saving uploaded file...")
            saved_path = save_uploaded_file(uploaded_file, UPLOADS_DIR)

            status_placeholder.info("Converting file to WAV format (if required)...")
            wav_path = convert_to_wav(saved_path)

            status_placeholder.info("Running AI model (Spleeter) to separate tracks...")
            result = separate_audio_file(wav_path, OUTPUTS_DIR)
            result["original_uploaded_path"] = str(saved_path)
            st.session_state.processed_result = result

            status_placeholder.success("Processing completed successfully.")
        except Exception as exc:
            st.session_state.processed_result = None
            status_placeholder.error(f"Processing failed: {exc}")


# ---------- Results section ----------
if st.session_state.processed_result:
    result = st.session_state.processed_result
    original_path = Path(result["original_uploaded_path"])
    vocals_path = Path(result["vocals_path"])
    instrumental_path = Path(result["instrumental_path"])

    st.subheader("Separated Results")
    st.success("Vocal and instrumental tracks generated and saved.")
    st.write(f"Approximate duration: `{result['duration_seconds']} seconds`")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Original**")
        st.audio(
            read_binary_file(original_path),
            format=get_streamlit_audio_format(original_path),
        )
        st.caption(f"Length: {get_audio_duration_seconds(original_path):.2f}s")
    with col2:
        st.write("**Vocals**")
        st.audio(read_binary_file(vocals_path), format="audio/wav")
        st.caption(f"Length: {get_audio_duration_seconds(vocals_path):.2f}s")

    st.write("**Instrumental**")
    st.audio(read_binary_file(instrumental_path), format="audio/wav")
    st.caption(f"Length: {get_audio_duration_seconds(instrumental_path):.2f}s")

    st.info(f"Saved vocals: {vocals_path}")
    st.info(f"Saved instrumental: {instrumental_path}")

    # ---------- Optional voice-over recording ----------
    st.subheader("Optional: Record Your Voice Over Instrumental")
    st.write("Record from your microphone and generate a quick voice-over mix.")

    if hasattr(st, "audio_input"):
        recorded_voice = st.audio_input("Click to start voice recording")

        if recorded_voice is not None:
            st.audio(recorded_voice.getvalue(), format="audio/wav")

            if st.button("Create Voice-Over Mix"):
                mix_status = st.empty()
                try:
                    mix_status.info("Mixing recorded voice with instrumental...")
                    mixed_path = mix_voice_over_instrumental(
                        instrumental_path=instrumental_path,
                        voice_bytes=recorded_voice.getvalue(),
                        output_dir=VOICEOVER_DIR,
                    )
                    mix_status.success("Voice-over mix created successfully.")
                    st.audio(read_binary_file(mixed_path), format="audio/wav")
                    st.info(f"Saved voice-over mix: {mixed_path}")
                except Exception as exc:
                    mix_status.error(f"Voice-over creation failed: {exc}")
    else:
        st.warning(
            "Your Streamlit version does not support microphone input (`st.audio_input`). "
            "Please upgrade Streamlit for this optional feature."
        )
