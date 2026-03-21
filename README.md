# AI-Based Vocal and Instrument Separation (Streamlit + Spleeter)

This project lets users upload a song (`.mp3` or `.wav`), separate it into vocals and instrumental tracks using Spleeter, and optionally record a voice-over on top of the instrumental.

## Features
- Upload audio in `.mp3` or `.wav`.
- Separate into two stems:
  - vocals
  - instrumental
- Preview original and processed tracks in the Streamlit UI.
- Optional microphone voice-over and quick mix export.
- Auto-save generated files to local output folders.

## Tech Stack
- Python
- Streamlit
- Spleeter
- Librosa
- SoundFile
- Pydub
- NumPy

## Project Structure
```text
project/
|-- app.py
|-- audio_processing.py
|-- utils.py
|-- requirements.txt
|-- .gitignore
|-- README.md
|-- uploads/
|   `-- .gitkeep
`-- outputs/
    |-- .gitkeep
    |-- vocals/
    |   `-- .gitkeep
    |-- instrumental/
    |   `-- .gitkeep
    `-- voiceovers/
        `-- .gitkeep
```

## Setup
1. Open terminal in the `project/` directory.
2. Create and activate a virtual environment.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Install FFmpeg (required for MP3 handling and Spleeter audio I/O).
- Windows: install FFmpeg and ensure `ffmpeg` + `ffprobe` are on `PATH`
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt install ffmpeg`

## Run
Use this from inside `project/`:

```bash
python -m streamlit run app.py
```

Then open the URL shown in terminal (usually `http://localhost:8501`).

## Usage
1. Upload a `.mp3` or `.wav`.
2. Click **Process Audio**.
3. Listen to original, vocals, and instrumental outputs.
4. Optionally record voice and click **Create Voice-Over Mix**.

## Notes
- First run may download Spleeter model weights (internet required once).
- Python `3.10` is recommended for compatibility with this dependency set.
- Generated files are saved under `uploads/` and `outputs/`.

## GitHub Upload Checklist
- Do not upload `.venv/`, model caches, or generated audio files.
- This repo already includes a `.gitignore` configured for those artifacts.
- Initialize and push:

```bash
git init
git add .
git commit -m "Initial commit: AI vocal and instrumental separator"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

## Future Improvements
- Add 4-stem/5-stem separation (drums, bass, piano, etc.).
- Add waveform visualization.
- Add ZIP download for all generated outputs.
