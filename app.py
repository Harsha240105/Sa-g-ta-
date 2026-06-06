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


# ---------- Session state defaults ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "processed_result" not in st.session_state:
    st.session_state.processed_result = None


# ---------- Streamlit page setup ----------
st.set_page_config(page_title="AI Vocal & Instrument Separation", layout="centered")


# ---------- Login page ----------
def login_page() -> None:
    st.title("Login")
    st.write("Sign in with your Gmail to access the app.")

    email = st.text_input("Gmail Address", placeholder="example@gmail.com")
    if st.button("Login", type="primary"):
        if email and "@gmail.com" in email:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("Please enter a valid Gmail address.")


# ---------- Home page ----------
def home_page() -> None:
    st.title("AI-Based Vocal & Instrument Separation for Interactive Music Experience")
    st.write(
        "Upload an MP3/WAV file, separate vocals and instrumental using Spleeter, "
        "and optionally record your voice over the instrumental."
    )

    # ---------- Audio Upload section ----------
    uploaded_file = st.file_uploader("Upload Audio File", type=["mp3", "wav"])

    if uploaded_file is not None:
        st.subheader("Original Audio Preview")
        st.audio(uploaded_file.getvalue(), format=uploaded_file.type or "audio/wav")

        # ---------- Processing section ----------
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

    # ---------- Results section (Vocal Output + Instrumental Output) ----------
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

        # ---------- Download Results section ----------
        st.subheader("Download Results")
        st.write("Download the separated audio files to your computer.")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.download_button(
                label="Download Original",
                data=read_binary_file(original_path),
                file_name=original_path.name,
                mime=get_streamlit_audio_format(original_path),
                use_container_width=True,
            )
        with col_b:
            st.download_button(
                label="Download Vocals",
                data=read_binary_file(vocals_path),
                file_name=vocals_path.name,
                mime="audio/wav",
                use_container_width=True,
            )
        with col_c:
            st.download_button(
                label="Download Instrumental",
                data=read_binary_file(instrumental_path),
                file_name=instrumental_path.name,
                mime="audio/wav",
                use_container_width=True,
            )

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


# ---------- About / Help page ----------
def about_page() -> None:
    st.title("About / Help")

    st.subheader("How It Works")
    st.write(
        "This app uses **Spleeter**, a pre-trained deep learning model, to separate uploaded "
        "songs into vocal and instrumental tracks. Simply upload an MP3 or WAV file, click "
        "**Process Audio**, and the AI model will split the audio into two separate stems."
    )

    st.subheader("Tech Stack")
    st.markdown("""
| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **Streamlit** | Web UI framework |
| **Spleeter** | Pre-trained model for source separation |
| **TensorFlow** | Deep learning backend used by Spleeter |
| **SoundFile** | Reading / writing audio files |
| **Pydub** | Audio format conversion and mixing |
| **NumPy** | Numerical operations on audio arrays |
| **Pandas** | Data handling and analysis |
| **Deep Learning** | AI model architecture for source separation |
| **Audio Signal Processing** | Core techniques for audio manipulation |
""")

    st.subheader("How to Use")
    st.markdown("""
1. **Login** – Enter your Gmail address to access the app.
2. **Home** – Upload an MP3 or WAV file.
3. **Process** – Click the **Process Audio** button to start AI separation.
4. **Preview** – Listen to the original, vocals, and instrumental tracks.
5. **Download** – Use the download buttons to save the separated files.
6. **Voice-Over (Optional)** – Record your voice over the instrumental track.
""")

    st.subheader("Requirements")
    st.write(
        "- Python 3.10 recommended\n"
        "- FFmpeg must be installed and on your system PATH\n"
        "- Internet connection required on first run (downloads Spleeter model weights)"
    )

    st.subheader("Contact")
    st.write(f"Logged in as: **{st.session_state.get('user_email', 'N/A')}**")


# ---------- App flow ----------

# Gate: show login page if not authenticated
if not st.session_state.logged_in:
    login_page()
    st.stop()

# Sidebar for logged-in users
with st.sidebar:
    st.write(f"Logged in as: **{st.session_state.user_email}**")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.processed_result = None
        st.rerun()

    page = st.radio("Navigate", ["Home", "About / Help"], label_visibility="collapsed")

# Manual page switching
if page == "Home":
    home_page()
else:
    about_page()
