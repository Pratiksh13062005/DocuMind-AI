import os
from io import BytesIO

import streamlit as st
from pypdf import PdfReader
from google import genai


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="DocuMind AI | Smart PDF Workspace",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# STYLING
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --bg: #0b1020;
        --panel: #121a2e;
        --panel2: #17223a;
        --text: #edf3ff;
        --muted: #9aa9c4;
        --accent: #8b7cff;
        --accent2: #42d6c5;
        --line: rgba(173, 190, 230, .15);
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background:
          radial-gradient(ellipse at 10% 0%, rgba(104, 89, 255, .19), transparent 34%),
          radial-gradient(ellipse at 95% 12%, rgba(41, 211, 190, .10), transparent 28%),
          var(--bg);
        color: var(--text);
    }
    [data-testid="stHeader"] { background: rgba(11,16,32,.75); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111a30 0%, #0d1426 100%);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] * { color: var(--text); }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }

    .brand {
        font-family: 'Manrope', sans-serif;
        font-size: 1.45rem; font-weight: 800; letter-spacing: -.7px;
        color: #fff; margin: .3rem 0 .1rem;
    }
    .brand span { color: #a99dff; }
    .muted { color: var(--muted); }
    .hero {
        padding: 2.3rem 2.4rem;
        border: 1px solid rgba(169,157,255,.25);
        border-radius: 24px;
        background: linear-gradient(120deg, rgba(116,98,255,.22), rgba(39,197,183,.10)),
                    rgba(18,26,46,.88);
        box-shadow: 0 18px 55px rgba(0,0,0,.18);
        margin-bottom: 1.3rem;
    }
    .eyebrow {
        color: #9eece2; text-transform: uppercase; letter-spacing: 2px;
        font-size: .72rem; font-weight: 800;
    }
    .hero h1 {
        color: white; font-family: 'Manrope', sans-serif;
        font-size: clamp(2rem, 4vw, 3.2rem); line-height: 1.12;
        letter-spacing: -1.5px; margin: .55rem 0 .7rem;
    }
    .hero p { color: #bdc9e0; font-size: 1.04rem; max-width: 760px; }
    .gradient-text { background: linear-gradient(90deg,#b7adff,#66e5d4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .section-title {
        font-family: 'Manrope', sans-serif; font-weight: 800;
        font-size: 1.35rem; color: #f4f6ff; margin: 1.2rem 0 .8rem;
    }
    .feature-card, .info-card {
        background: linear-gradient(145deg, rgba(24,35,59,.96), rgba(17,26,45,.96));
        border: 1px solid var(--line); border-radius: 18px;
        padding: 1.25rem 1.35rem; min-height: 150px;
    }
    .feature-card .icon { font-size: 1.7rem; }
    .feature-card h3 { color: #fff; font-size: 1.04rem; margin: .55rem 0 .35rem; }
    .feature-card p { color: var(--muted); font-size: .91rem; margin: 0; }
    div[data-testid="stMetric"] {
        background: rgba(23,34,58,.8); border: 1px solid var(--line);
        padding: 14px 16px; border-radius: 15px;
    }
    div[data-testid="stMetric"] label { color: var(--muted); }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff; }
    .status-pill {
        display: inline-block; padding: 5px 11px; border-radius: 30px;
        background: rgba(66,214,197,.12); color: #83eee0;
        border: 1px solid rgba(66,214,197,.25); font-size: .78rem; font-weight: 700;
    }
    .small-note { color: var(--muted); font-size: .82rem; }
    .stButton > button, .stDownloadButton > button {
        border: 0; border-radius: 11px; font-weight: 700;
        background: linear-gradient(100deg,#8b7cff,#5b9bff);
        color: white; padding: .58rem 1rem;
        transition: .2s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border: 0; color: white; filter: brightness(1.12);
        transform: translateY(-1px);
    }
    .stTextInput input, .stTextArea textarea {
        background: #111b30 !important; color: #f4f6ff !important;
        border: 1px solid var(--line) !important; border-radius: 10px !important;
    }
    [data-testid="stFileUploader"] {
        background: rgba(20,31,53,.55); border: 1px dashed rgba(169,157,255,.5);
        border-radius: 16px; padding: 10px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(22,33,56,.8); border-radius: 10px 10px 0 0;
        padding: 10px 16px; color: #cbd5e8;
    }
    hr { border-color: var(--line); }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
DEFAULTS = {
    "pdf_text": "",
    "pdf_name": "",
    "chat_history": [],
    "summary": "",
    "user_api_key": "",
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def get_api_key():
    """Read the API key from sidebar input, Streamlit secrets, or environment."""
    if st.session_state.get("user_api_key"):
        return st.session_state.user_api_key.strip()

    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
        if secret_key:
            return str(secret_key).strip()
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY", "").strip()


def ask_gemini(prompt, api_key=None):
    """Send a prompt to Gemini and return a readable error instead of crashing."""
    key = api_key or get_api_key()
    if not key:
        return (
            "API key is missing. Add your Gemini API key in the sidebar, "
            "or configure GEMINI_API_KEY in Streamlit Secrets."
        )

    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        answer = getattr(response, "text", None)
        return answer.strip() if answer else "Gemini returned an empty response."
    except Exception as exc:
        error_text = str(exc)
        if "401" in error_text or "API_KEY_INVALID" in error_text:
            return "Gemini authentication failed. Please check that your API key is valid."
        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            return "Gemini rate limit or quota reached. Please wait a little and try again."
        if "503" in error_text or "UNAVAILABLE" in error_text:
            return "Gemini is temporarily busy (503). Please try again in a few moments."
        return f"Gemini request failed: {error_text}"


def extract_pdf_text(pdf_file):
    """Extract selectable text from a PDF file."""
    try:
        reader = PdfReader(BytesIO(pdf_file.getvalue()))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                return "", "This PDF is password-protected. Please upload an unlocked PDF."

        pages_text = []
        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages_text.append(f"--- Page {page_number} ---\n{page_text.strip()}")

        full_text = "\n\n".join(pages_text).strip()
        if not full_text:
            return "", (
                "No selectable text was found. This may be a scanned PDF; "
                "OCR support is required for scanned pages."
            )
        return full_text, None
    except Exception as exc:
        return "", f"Could not read this PDF: {exc}"


def make_document_prompt(question):
    # Keep the prompt within a practical size for the selected Gemini model.
    document = st.session_state.pdf_text[:60000]
    return f"""
You are DocuMind AI, a careful document assistant.
Answer the user's question primarily from the supplied document.
Do not invent facts. If the document does not contain the answer, say so.
Use clear headings or bullet points when useful. Reply in the same language
as the user's question (English or Hindi are both supported).

DOCUMENT: {st.session_state.pdf_name}

DOCUMENT TEXT:
{document}

USER QUESTION:
{question}
"""


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand">📘 Docu<span>Mind</span> AI</div>'
        '<div class="small-note">Your intelligent PDF workspace</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    page = st.radio(
        "WORKSPACE",
        ["🏠 Overview", "📄 Documents", "✨ AI Assistant", "ℹ️ About"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.markdown("### 🔐 AI connection")
    entered_key = st.text_input(
        "Gemini API key",
        type="password",
        value=st.session_state.user_api_key,
        placeholder="Paste your API key",
        help="Your key is kept in this Streamlit session. Do not share it.",
    )
    st.session_state.user_api_key = entered_key.strip()

    if get_api_key():
        st.markdown('<span class="status-pill">● API key configured</span>', unsafe_allow_html=True)
    else:
        st.caption("Add a Gemini API key to enable AI features.")

    st.markdown("---")
    if st.session_state.pdf_name:
        st.success(f"Active PDF\n\n{st.session_state.pdf_name}")
    else:
        st.info("No document loaded yet.")
    st.caption("Built with Streamlit · Google Gemini")


# ---------------------------------------------------------
# OVERVIEW
# ---------------------------------------------------------
if page == "🏠 Overview":
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">READ LESS. UNDERSTAND MORE.</div>
          <h1>Meet your documents'<br><span class="gradient-text">new best friend.</span></h1>
          <p>Upload a PDF, discover the important details, create a quick summary,
          and chat with your document using AI — all in one clean workspace.</p>
          <span class="status-pill">✦ AI-powered document intelligence</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Everything you need, in one place</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    cards = [
        ("📂", "Simple PDF upload", "Bring your PDF into one organized workspace and extract its readable text."),
        ("💬", "Ask in natural language", "Ask questions and get answers grounded in the uploaded document."),
        ("⚡", "Instant key takeaways", "Generate a clear summary to understand long documents faster."),
    ]
    for col, (icon, title, desc) in zip((c1, c2, c3), cards):
        with col:
            st.markdown(
                f'<div class="feature-card"><div class="icon">{icon}</div>'
                f'<h3>{title}</h3><p>{desc}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown("")
    left, right = st.columns([1.4, 1])
    with left:
        st.markdown('<div class="section-title">🚀 Get started</div>', unsafe_allow_html=True)
        st.write("1. Open **Documents** from the sidebar.")
        st.write("2. Upload a text-based PDF and select **Process PDF**.")
        st.write("3. Open **AI Assistant** to ask questions or create a summary.")
        if st.button("Open document workspace →", use_container_width=True):
            st.info("Choose **Documents** in the sidebar to upload your PDF.")
    with right:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("**Your workspace**")
        st.metric("Document status", "Ready" if st.session_state.pdf_text else "Waiting for PDF")
        st.metric("Chat messages", len(st.session_state.chat_history))
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# DOCUMENTS
# ---------------------------------------------------------
elif page == "📄 Documents":
    st.markdown('<div class="section-title">📄 Document library</div>', unsafe_allow_html=True)
    st.write("Upload a PDF to extract its text and make it ready for AI analysis.")

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        help="Select a PDF stored on your computer.",
    )

    if uploaded_file:
        size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        st.caption(f"Selected: **{uploaded_file.name}** · {size_mb:.2f} MB")
        if st.button("⚡ Process this PDF", type="primary", use_container_width=True):
            with st.spinner("Reading your document..."):
                text, error = extract_pdf_text(uploaded_file)
            if error:
                st.error(error)
            else:
                st.session_state.pdf_text = text
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.chat_history = []
                st.session_state.summary = ""
                st.success("Your PDF has been processed successfully!")

    if st.session_state.pdf_text:
        st.markdown("---")
        st.markdown('<div class="section-title">Document insights</div>', unsafe_allow_html=True)
        words = len(st.session_state.pdf_text.split())
        pages = st.session_state.pdf_text.count("--- Page ")
        m1, m2, m3 = st.columns(3)
        m1.metric("📄 File", st.session_state.pdf_name)
        m2.metric("📝 Words extracted", f"{words:,}")
        m3.metric("📚 Pages with text", f"{pages:,}")

        with st.expander("Preview extracted text", expanded=False):
            st.text_area(
                "Extracted PDF content",
                value=st.session_state.pdf_text[:30000],
                height=300,
                disabled=True,
            )
            if len(st.session_state.pdf_text) > 30000:
                st.caption("Preview limited to the first 30,000 characters.")

        st.download_button(
            "⬇️ Download extracted text",
            data=st.session_state.pdf_text,
            file_name="documind_extracted_text.txt",
            mime="text/plain",
        )
        if st.button("🗑️ Remove current document"):
            st.session_state.pdf_text = ""
            st.session_state.pdf_name = ""
            st.session_state.chat_history = []
            st.session_state.summary = ""
            st.rerun()
    else:
        st.markdown(
            '<div class="info-card"><b>✨ Your document will appear here</b>'
            '<p class="muted">After processing, you will see document statistics, a text preview, '
            'and a download option.</p></div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------
# AI ASSISTANT
# ---------------------------------------------------------
elif page == "✨ AI Assistant":
    st.markdown('<div class="section-title">✨ Your AI document assistant</div>', unsafe_allow_html=True)
    if st.session_state.pdf_text:
        st.success(f"Using document: {st.session_state.pdf_name}")
    else:
        st.info("No PDF is loaded. You can still use general AI chat.")

    tab_chat, tab_summary = st.tabs(["💬 Ask a question", "🪄 Smart summary"])

    with tab_chat:
        for item in st.session_state.chat_history:
            with st.chat_message(item["role"]):
                st.markdown(item["content"])

        question = st.chat_input("Ask something about your PDF...")
        if question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            if st.session_state.pdf_text:
                prompt = make_document_prompt(question)
            else:
                prompt = (
                    "You are DocuMind AI. Answer clearly and accurately. "
                    "Support English and Hindi. Use examples when useful.\n\n"
                    f"USER QUESTION:\n{question}"
                )

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = ask_gemini(prompt)
                st.markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

        if st.session_state.chat_history and st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()

    with tab_summary:
        st.write("Create a structured overview of the currently loaded PDF.")
        if not st.session_state.pdf_text:
            st.warning("Upload and process a PDF first to generate its summary.")
        else:
            if st.button("✨ Generate document summary", use_container_width=True):
                summary_prompt = f"""
Create a useful summary of this document.
Include:
1. A short overview
2. The most important points
3. Important names, dates, figures, or terms (if present)
4. A brief conclusion
Do not add facts that are not in the document.
Write in clear, simple language.

DOCUMENT:
{st.session_state.pdf_text[:60000]}
"""
                with st.spinner("Creating your summary..."):
                    st.session_state.summary = ask_gemini(summary_prompt)

            if st.session_state.summary:
                st.markdown(st.session_state.summary)
                st.download_button(
                    "⬇️ Download summary",
                    data=st.session_state.summary,
                    file_name="documind_summary.txt",
                    mime="text/plain",
                )


# ---------------------------------------------------------
# ABOUT
# ---------------------------------------------------------
elif page == "ℹ️ About":
    st.markdown('<div class="section-title">ℹ️ About DocuMind AI</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">ABOUT THE PROJECT</div>
          <h1>Make every page<br><span class="gradient-text">easier to understand.</span></h1>
          <p>DocuMind AI is a PDF question-answering workspace built with Python,
          Streamlit, and Google's Gemini generative AI.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    a, b = st.columns(2)
    with a:
        st.markdown("### 🧰 Technology stack")
        st.write("- Python")
        st.write("- Streamlit")
        st.write("- Google Gemini API (`google-genai`)")
        st.write("- pypdf for PDF text extraction")
    with b:
        st.markdown("### ✨ Main features")
        st.write("- PDF upload and text extraction")
        st.write("- Document-based question answering")
        st.write("- AI-generated document summaries")
        st.write("- Chat history and text downloads")
    st.caption("Note: scanned/image-only PDFs need OCR, which is not included in this version.")


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.markdown(
    '<p class="small-note" style="text-align:center;">'
    '📘 DocuMind AI · Built with Python, Streamlit & Google Gemini · © 2026'
    '</p>',
    unsafe_allow_html=True,
)
