"""
AI Video Assistant With RAG - Streamlit UI
Run with:  streamlit run app.py
"""
import html
import io
import math
import os
import re
import tempfile
import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.rag_engine import build_rag_chain, ask_question

st.set_page_config(page_title="Meeting Assistant", page_icon="🎙️", layout="wide")

# ── Styling ───────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Sora:wght@600;700&display=swap');
:root{--ink:#16213E;--muted:#5B6785;--accent:#2F5BEA;--accent-soft:#E8EEFF;--line:#E1E6F2;--paper:#FFFFFF;--coral:#FF6B57;}
.stApp{font-family:'DM Sans',sans-serif;color:var(--ink);}
h1,h2,h3,h4{font-family:'Sora',sans-serif !important;letter-spacing:-0.02em;color:var(--ink);}
#MainMenu,footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:2.2rem;max-width:1080px;}

/* Sidebar */
section[data-testid="stSidebar"]{background:var(--paper);border-right:1px solid var(--line);}
section[data-testid="stSidebar"] .block-container{padding-top:1.5rem;}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:.4rem;}
.brand-mark{display:flex;align-items:center;gap:3px;height:34px;}
.brand-mark span{width:4px;border-radius:2px;background:var(--accent);}
.brand-name{font-family:'Sora',sans-serif;font-weight:700;font-size:1.15rem;line-height:1.1;}
.brand-sub{color:var(--muted);font-size:.85rem;margin-bottom:1.4rem;}
.side-label{font-weight:700;font-size:.9rem;margin:1.1rem 0 .3rem;}

/* Buttons */
.stButton>button,.stDownloadButton>button{border-radius:10px;font-weight:700;padding:.65rem 1rem;border:1px solid var(--line);transition:transform .12s ease, box-shadow .12s ease;}
.stButton>button[kind="primary"]{background:var(--accent);color:#fff;border:none;box-shadow:0 6px 16px rgba(47,91,234,.28);}
.stButton>button[kind="primary"]:hover{transform:translateY(-1px);box-shadow:0 8px 20px rgba(47,91,234,.36);}
.stDownloadButton>button{background:var(--paper);color:var(--ink);}
.stDownloadButton>button:hover{border-color:var(--accent);color:var(--accent);}
[data-testid="stFileUploaderDropzone"]{border:1.5px dashed #B7C3E6;border-radius:12px;background:#F8FAFF;}
section[data-testid="stSidebar"] input{border-radius:10px !important;}

/* Hero */
.hero{padding:2.2rem 2.4rem 2rem;background:var(--paper);border:1px solid var(--line);border-radius:22px;margin-bottom:1.8rem;box-shadow:0 10px 30px rgba(22,33,62,.05);}
.hero h1{font-size:2.7rem;line-height:1.1;margin:0 0 .7rem;max-width:640px;}
.hero p{color:var(--muted);font-size:1.08rem;max-width:560px;margin:0 0 1.4rem;line-height:1.55;}
.wave{display:flex;align-items:center;gap:4px;height:74px;}
.wave span{display:block;width:5px;height:var(--h);border-radius:3px;background:var(--accent);animation:pulse 1.7s ease-in-out infinite;animation-delay:var(--d);}
.wave span:nth-child(3n){opacity:.5;}
.wave span:nth-child(11n){background:var(--coral);}
@keyframes pulse{0%,100%{transform:scaleY(.4);}50%{transform:scaleY(1);}}
@media (prefers-reduced-motion:reduce){.wave span{animation:none;}}

/* Steps */
.steps{display:grid;grid-template-columns:repeat(3,1fr);background:var(--paper);border:1px solid var(--line);border-radius:18px;overflow:hidden;}
.step{padding:1.4rem 1.5rem;border-right:1px solid var(--line);}
.step:last-child{border-right:none;}
.step-n{display:inline-flex;width:28px;height:28px;border-radius:50%;background:var(--accent-soft);color:var(--accent);font-weight:700;align-items:center;justify-content:center;margin-bottom:.7rem;}
.step h3{font-size:1.02rem;margin:0 0 .35rem;}
.step p{color:var(--muted);font-size:.93rem;margin:0;line-height:1.5;}
.tech{color:var(--muted);font-size:.85rem;margin-top:1.2rem;}
@media (max-width:760px){.steps{grid-template-columns:1fr;}.step{border-right:none;border-bottom:1px solid var(--line);}.hero h1{font-size:2rem;}}

/* Results header + stats */
.res-title{font-family:'Sora',sans-serif;font-weight:700;font-size:2rem;line-height:1.2;margin:0 0 .3rem;}
.res-meta{color:var(--muted);margin-bottom:1.2rem;}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:1.4rem;}
.stat{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:.9rem 1.1rem;}
.stat b{display:block;font-family:'Sora',sans-serif;font-size:1.6rem;line-height:1.2;}
.stat span{color:var(--muted);font-size:.85rem;}
.stat.hl{background:var(--accent);border-color:var(--accent);}
.stat.hl b,.stat.hl span{color:#fff;}
@media (max-width:760px){.stats{grid-template-columns:repeat(2,1fr);}}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{gap:6px;border-bottom:none;flex-wrap:wrap;}
.stTabs [data-baseweb="tab"]{height:40px;padding:0 16px;border-radius:999px;background:transparent;color:var(--muted);font-weight:700;}
.stTabs [aria-selected="true"]{background:var(--accent-soft);color:var(--accent);}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none;}
.stTabs [data-baseweb="tab-panel"]{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:1.6rem 1.8rem;margin-top:.8rem;line-height:1.65;}
[data-testid="stChatMessage"]{background:#F6F8FD;border-radius:14px;}
.stTextArea textarea{font-family:'DM Sans',sans-serif;line-height:1.6;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "chat" not in st.session_state:
    st.session_state.chat = []
if "language_label" not in st.session_state:
    st.session_state.language_label = "English"


# ── Helpers ───────────────────────────────────────────────────────────────────
def clean_youtube_url(url: str) -> str:
    """Keep only the single video ID so yt-dlp never downloads a whole playlist."""
    from urllib.parse import urlparse, parse_qs
    try:
        p = urlparse(url)
        host = (p.netloc or "").lower()
        if "youtu.be" in host:
            vid = p.path.strip("/").split("/")[0]
            return f"https://www.youtube.com/watch?v={vid}" if vid else url
        if "youtube.com" in host:
            vid = parse_qs(p.query).get("v", [None])[0]
            if vid:
                return f"https://www.youtube.com/watch?v={vid}"
    except Exception:
        pass
    return url


def build_txt(r: dict) -> str:
    return (
        f"{r['title']}\n{'=' * len(r['title'])}\n"
        f"Generated: {datetime.now():%Y-%m-%d %H:%M}\n\n"
        f"SUMMARY\n-------\n{r['summary']}\n\n"
        f"FULL TRANSCRIPT\n---------------\n{r['transcript']}\n"
    )


def build_pdf(r: dict) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

    def clean(text: str) -> str:
        # Built-in PDF fonts only support cp1252, so drop emojis/unsupported chars
        text = str(text).encode("cp1252", "replace").decode("cp1252")
        text = html.escape(text)
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"^\s*[-*]\s+", "&bull; ", text, flags=re.M)
        return text.replace("\n", "<br/>")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=50, rightMargin=50,
                            topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    story = [Paragraph(clean(r["title"]), styles["Title"]), Spacer(1, 12)]
    for heading, body in [
        ("Summary", r["summary"]),
        ("Full Transcript", r["transcript"]),
    ]:
        story.append(Paragraph(heading, styles["Heading2"]))
        story.append(Paragraph(clean(body), styles["BodyText"]))
        story.append(Spacer(1, 12))
    doc.build(story)
    return buf.getvalue()


def fmt_time(seconds: float) -> str:
    seconds = int(seconds)
    return f"{seconds // 60}m {seconds % 60:02d}s"


def run_pipeline_with_progress(source: str, language: str) -> dict:
    steps = [
        "Downloading and preparing the audio",
        "Transcribing the recording",
        "Writing the title and summary",
        "Indexing the transcript for chat",
    ]
    started = time.time()

    with st.status("Processing your meeting...", expanded=True) as status:
        board = st.empty()

        def show(active: int):
            lines = []
            for i, name in enumerate(steps):
                if i < active:
                    lines.append(f"✅ {name}")
                elif i == active:
                    lines.append(f"⏳ **{name}**")
                else:
                    lines.append(f"⬜ {name}")
            board.markdown("\n\n".join(lines))

        show(0)
        chunks = process_input(source)

        show(1)
        transcript = transcribe_all(chunks, language)

        show(2)
        title = generate_title(transcript)
        summary = summarize(transcript)

        show(3)
        rag_chain = build_rag_chain(transcript)

        board.markdown("\n\n".join(f"✅ {s}" for s in steps))
        status.update(
            label=f"Your meeting is ready ({fmt_time(time.time() - started)})",
            state="complete", expanded=False,
        )

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "rag_chain": rag_chain,
    }


# ── Sidebar ───────────────────────────────────────────────────────────────────
mini_bars = "".join(
    f'<span style="height:{h}px"></span>' for h in (12, 22, 32, 18, 26, 10)
)
with st.sidebar:
    st.markdown(
        f'<div class="brand"><div class="brand-mark">{mini_bars}</div>'
        '<div class="brand-name">Meeting Assistant</div></div>'
        '<div class="brand-sub">Turn any recording into notes you can chat with.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">Language spoken</div>', unsafe_allow_html=True)
    language_label = st.radio(
        "Language spoken", ["English", "Hindi / Hinglish"],
        label_visibility="collapsed",
    )
    language = "english" if language_label == "English" else "hinglish"

    st.markdown('<div class="side-label">Recording</div>', unsafe_allow_html=True)
    input_type = st.radio(
        "Recording source", ["YouTube link", "Upload a file"],
        horizontal=True, label_visibility="collapsed",
    )

    source, uploaded = None, None
    if input_type == "YouTube link":
        source = st.text_input(
            "YouTube link", placeholder="Paste a YouTube link",
            label_visibility="collapsed",
        )
    else:
        uploaded = st.file_uploader(
            "Audio or video file",
            type=["mp3", "wav", "m4a", "mp4", "mkv", "webm", "mov", "ogg"],
            label_visibility="collapsed",
        )

    st.write("")
    process_clicked = st.button("Process meeting", type="primary", use_container_width=True)

    if st.session_state.result and st.button("Start a new meeting", use_container_width=True):
        st.session_state.result = None
        st.session_state.chat = []
        st.rerun()

# ── Run pipeline ──────────────────────────────────────────────────────────────
if process_clicked:
    if input_type == "YouTube link" and not source:
        st.sidebar.error("Paste a YouTube link to continue.")
    elif input_type == "Upload a file" and uploaded is None:
        st.sidebar.error("Upload an audio or video file to continue.")
    else:
        try:
            if uploaded is not None:
                suffix = os.path.splitext(uploaded.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded.getbuffer())
                    source = tmp.name
            st.session_state.result = run_pipeline_with_progress(clean_youtube_url(source.strip()), language)
            st.session_state.language_label = language_label
            st.session_state.chat = []
        except Exception as e:
            st.error(f"Processing stopped: {e}. Check the link or file, then try again.")

# ── Main area ─────────────────────────────────────────────────────────────────
result = st.session_state.result

if not result:
    bars = "".join(
        f'<span style="--h:{22 + int(46 * abs(math.sin(i * 0.7) * math.cos(i * 0.23)))}px;'
        f'--d:{(i % 7) * 0.13:.2f}s"></span>'
        for i in range(52)
    )
    st.markdown(
        '<div class="hero"><h1>Every meeting, turned into notes and answers.</h1>'
        '<p>Add a YouTube link or a recording. You get a written summary and a full transcript, '
        'and you can ask the recording anything.</p>'
        f'<div class="wave">{bars}</div></div>'
        '<div class="steps">'
        '<div class="step"><div class="step-n">1</div><h3>Add a recording</h3>'
        '<p>Paste a YouTube link or upload audio or video. English and Hindi/Hinglish are supported.</p></div>'
        '<div class="step"><div class="step-n">2</div><h3>Read the summary</h3>'
        '<p>Get a bullet summary and the full transcript of what was said.</p></div>'
        '<div class="step"><div class="step-n">3</div><h3>Ask and export</h3>'
        '<p>Chat with the transcript, then download the report as PDF or TXT.</p></div></div>'
        '<div class="tech">Runs on Whisper, Sarvam AI, Groq and ChromaDB.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="res-title">{html.escape(result["title"])}</div>'
        f'<div class="res-meta">Transcribed in {html.escape(st.session_state.language_label)}.</div>',
        unsafe_allow_html=True,
    )

    views = ["Chat", "Summary", "Transcript", "Export"]
    if hasattr(st, "segmented_control"):
        view = st.segmented_control(
            "View", views, default="Chat", key="view", label_visibility="collapsed"
        ) or "Chat"
    else:
        view = st.radio("View", views, horizontal=True, key="view", label_visibility="collapsed")

    if view == "Summary":
        with st.container(border=True):
            st.markdown(result["summary"])

    elif view == "Transcript":
        st.text_area("Full transcript", result["transcript"], height=460,
                     label_visibility="collapsed")

    elif view == "Export":
        st.markdown("#### Download the full report")
        st.caption("Includes the summary and the full transcript.")
        safe_name = re.sub(r"[^\w\-]+", "_", result["title"]).strip("_") or "meeting_report"
        col1, col2 = st.columns(2)
        col1.download_button(
            "Download TXT", build_txt(result),
            file_name=f"{safe_name}.txt", mime="text/plain", use_container_width=True,
        )
        try:
            col2.download_button(
                "Download PDF", build_pdf(result),
                file_name=f"{safe_name}.pdf", mime="application/pdf", use_container_width=True,
            )
        except Exception as e:
            col2.error(f"The PDF could not be created: {e}. Download the TXT instead.")

    else:  # Chat: messages above, input pinned to the bottom of the page
        if not st.session_state.chat:
            st.caption("Try: What is this recording about? What did the speaker say about the main topic?")
        for msg in st.session_state.chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        question = st.chat_input("Ask about the meeting")
        if question:
            st.session_state.chat.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("Searching the transcript..."):
                    answer = ask_question(result["rag_chain"], question)
                st.markdown(answer)
            st.session_state.chat.append({"role": "assistant", "content": answer})