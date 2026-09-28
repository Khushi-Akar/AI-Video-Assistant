# AI Video Assistant With RAG

Turn any YouTube video or meeting recording into a transcript, a written summary, and a chatbot you can ask questions.

Paste a YouTube link or upload an audio or video file, pick the language, and the app transcribes it, summarises it, and lets you chat with the content using retrieval-augmented generation (RAG).

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-video-assistant-4e9e3srpcuzfaawnyh4v25.streamlit.app/)

## Live demo

Try the app here: **https://ai-video-assistant-4e9e3srpcuzfaawnyh4v25.streamlit.app/**

Tip: on the live app, use file upload for the most reliable results, because YouTube often blocks downloads from cloud servers. Start with a short recording (2 to 3 minutes).

## Features

- **Two input types:** a YouTube link or an uploaded audio/video file
- **English transcription** using OpenAI Whisper, running locally and free
- **Hindi and Hinglish transcription** using Sarvam AI, translated to English
- **Bullet-point summary** of the full recording
- **Chat with your recording** using RAG: questions are answered only from the transcript
- **Full transcript view**
- **Export** the report as PDF or TXT
- **Live progress checklist** while a recording is processed

## Tech stack

| Area | Tools |
| --- | --- |
| Language | Python |
| Speech to text (English) | OpenAI Whisper (local) |
| Speech to text (Hindi/Hinglish) | Sarvam AI |
| LLM pipeline | LangChain (LCEL) |
| LLM | Groq API |
| Vector database | ChromaDB |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` (local, free) |
| Audio download and processing | yt-dlp, pydub, FFmpeg |
| UI | Streamlit |
| PDF export | ReportLab |

## How it works

```
YouTube link / file
        |
   audio_processor   download, convert, split into chunks
        |
   transcriber       Whisper (English) or Sarvam AI (Hindi/Hinglish)
        |
   summarizer        chunk summaries combined into one final summary
        |
   vector_store      transcript split, embedded, stored in ChromaDB
        |
   rag_engine        retrieve relevant chunks, answer with Groq
        |
   app.py            Streamlit interface
```

## Project structure

```
AI Video Assistant With RAG/
├── .streamlit/
│   └── config.toml        Streamlit theme
├── core/
│   ├── extractor.py       Action items, decisions, open questions (not shown in the UI)
│   ├── rag_engine.py      RAG chain and question answering
│   ├── summarizer.py      Summary and title generation
│   ├── transcriber.py     Whisper and Sarvam transcription
│   └── vector_store.py    ChromaDB build and load
├── utils/
│   └── audio_processor.py Download, convert and chunk audio
├── app.py                 Streamlit app
├── main.py                Command-line version of the pipeline
├── requirements.txt
├── packages.txt           System packages for Streamlit Cloud (FFmpeg)
├── .env.example           Template for your API keys
└── .gitignore
```

## Getting started

### Requirements

- Python 3.10 to 3.12 (3.12 recommended)
- [FFmpeg](https://ffmpeg.org/download.html) installed and on your PATH
  - Windows: `winget install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- A free [Groq API key](https://console.groq.com/keys)
- A [Sarvam AI key](https://www.sarvam.ai) (only needed for Hindi/Hinglish)

### Installation

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

python -m venv .venv
```

Activate the environment:

```bash
# Windows (PowerShell)
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and add your keys:

```
GROQ_API_KEY=your_groq_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
```

Optional settings:

```
WHISPER_MODEL=base          # tiny, base, small, medium. Smaller is faster.
SARVAM_STT_MODEL=saaras:v2.5
```

Never commit your `.env` file. It is listed in `.gitignore`.

### Run the app

```bash
streamlit run app.py
```

Or use the command-line version:

```bash
python main.py
```

## Usage

1. Choose the language spoken in the recording: **English** or **Hindi / Hinglish**.
2. Paste a YouTube link or upload an audio/video file.
3. Click **Process meeting** and wait for the checklist to finish.
4. Use **Chat** to ask questions, **Summary** and **Transcript** to read, and **Export** to download the report.

Start with a short video (2 to 3 minutes) to check that everything works. Long recordings take a long time to transcribe on a CPU.

## Deploying on Streamlit Community Cloud

This project is deployed at: https://ai-video-assistant-4e9e3srpcuzfaawnyh4v25.streamlit.app/

To deploy your own copy:

1. Push the repo to GitHub.
2. Create the app and open **Advanced settings**. Set the Python version to **3.12**.
3. Make sure the repo has `packages.txt` containing `ffmpeg`.
4. In **Settings → Secrets**, add your keys in TOML format:

```toml
GROQ_API_KEY = "your_groq_key"
SARVAM_API_KEY = "your_sarvam_key"
WHISPER_MODEL = "base"
SARVAM_STT_MODEL = "saaras:v2.5"
```

Things to know:

- YouTube often blocks downloads from cloud servers. File upload is the reliable option there.
- The free tier has limited memory. Use the `base` or `tiny` Whisper model.
- Free Streamlit apps go to sleep after a period of inactivity. If the live demo shows a sleeping page, click the wake-up button and wait a moment.

## Known limitations

- Whisper on a CPU is slow for long recordings.
- Hindi/Hinglish audio is sent to Sarvam in 25-second pieces and returned as English text.
- The chat answers only from the transcript. If the answer isn't there, it says so.
- Action items, key decisions and open questions are implemented in `core/extractor.py` but are not shown in the interface.

## Roadmap

- Show action items, decisions and open questions in the UI
- Real download progress for YouTube links
- Support for more languages
- Saved history of past recordings

## License

Add a license of your choice, for example MIT.
