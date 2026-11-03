import streamlit as st
import os
from io import BytesIO
from PyPDF2 import PdfReader
from google import genai

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #171a21;
}

.main-title {
    font-size: 42px;
    font-weight: bold;
    color: #D4AF37;
    text-align: center;
}

.subtitle {
    color: #aaaaaa;
    text-align: center;
    font-size: 17px;
}

.feature-card {
    background-color: #1c2029;
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #D4AF37;
    margin-bottom: 15px;
}

.stButton button {
    background-color: #D4AF37;
    color: black;
    border-radius: 8px;
    font-weight: bold;
    border: none;
}

.stButton button:hover {
    background-color: #f0c94d;
    color: black;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE
# ==========================================

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "page" not in st.session_state:
    st.session_state.page = "Home"


# ==========================================
# GEMINI API CONFIGURATION
# ==========================================

def get_api_key():

    try:
        if st.secrets.get("GEMINI_API_KEY"):
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY", "")


def get_gemini_response(prompt):

    api_key = get_api_key()

    if not api_key:
        return "Please add your Gemini API Key in Streamlit Secrets."

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text or "No response received from Gemini."

    except Exception as e:
        return f"AI Error: {str(e)}"


# ==========================================
# PDF TEXT EXTRACTION
# ==========================================

def extract_pdf_text(pdf_file):

    try:
        pdf_bytes = BytesIO(pdf_file.getvalue())

        reader = PdfReader(pdf_bytes)

        extracted_text = ""

        for page_number, page in enumerate(reader.pages):

            text = page.extract_text()

            if text:
                extracted_text += (
                    f"\n\nPage {page_number + 1}\n"
                    + text
                )

        return extracted_text

    except Exception as e:
        st.error(f"PDF Extraction Error: {str(e)}")
        return ""


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown(
        "<h1 style='color:#D4AF37;'>📚 DocuMind AI</h1>",
        unsafe_allow_html=True
    )

    st.write("Intelligent Document Question Answering")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Home",
            "Documents",
            "AI Assistant",
            "About"
        ]
    )

    st.session_state.page = page

    st.divider()

    st.subheader("⚙️ API Settings")

    api_key = st.text_input(
        "Gemini API Key",
        value="",
        type="password",
        help="Enter your Google Gemini API Key"
    )

    if api_key:
        st.session_state["user_api_key"] = api_key

    st.caption(
        "Your API key is used to connect with Google Gemini."
    )

    st.divider()

    if st.session_state.pdf_name:

        st.success(
            f"Loaded: {st.session_state.pdf_name}"
        )

    else:

        st.info("No PDF uploaded yet.")


# ==========================================
# API KEY HELPER
# ==========================================

def get_api_key():

    if st.session_state.get("user_api_key"):
        return st.session_state["user_api_key"]

    try:
        if st.secrets.get("GEMINI_API_KEY"):
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY", "")


# ==========================================
# HOME PAGE
# ==========================================

if st.session_state.page == "Home":

    st.markdown(
        "<div class='main-title'>DocuMind AI</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>"
        "Intelligent Document Question Answering System"
        "</div>",
        unsafe_allow_html=True
    )

    st.write("")

    st.markdown("""
    <div class="feature-card">

    <h2 style="color:#D4AF37;">
    Welcome to DocuMind AI
    </h2>

    <p>
    DocuMind AI is an intelligent document analysis
    application powered by Google Gemini and Streamlit.
    </p>

    <p>
    Upload PDF documents, ask questions, generate summaries
    and understand your documents using Artificial Intelligence.
    </p>

    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("""
        <div class="feature-card">
        <h3>📄 PDF Upload</h3>
        <p>Upload and extract information from PDF documents.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="feature-card">
        <h3>🤖 AI Assistant</h3>
        <p>Ask questions and receive intelligent AI answers.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown("""
        <div class="feature-card">
        <h3>📝 Smart Summary</h3>
        <p>Generate summaries and understand important points.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    if st.button("Get Started"):

        st.session_state.page = "Documents"
        st.rerun()


# ==========================================
# DOCUMENT PAGE
# ==========================================

elif st.session_state.page == "Documents":

    st.title("📄 Document Management")

    st.write(
        "Upload your PDF document to start intelligent analysis."
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a PDF document."
    )

    if uploaded_file:

        if st.button("Process PDF"):

            with st.spinner("Extracting PDF text..."):

                extracted_text = extract_pdf_text(uploaded_file)

                if extracted_text.strip():

                    st.session_state.pdf_text = extracted_text

                    st.session_state.pdf_name = uploaded_file.name

                    st.session_state.chat_history = []

                    st.success("PDF processed successfully!")

                else:

                    st.error(
                        "No readable text found in this PDF. "
                        "Scanned PDFs may require OCR."
                    )

    if st.session_state.pdf_text:

        st.divider()

        st.subheader("📊 Document Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Document",
                st.session_state.pdf_name
            )

        with col2:
            st.metric(
                "Characters",
                f"{len(st.session_state.pdf_text):,}"
            )

        with col3:
            st.metric(
                "Words",
                f"{len(st.session_state.pdf_text.split()):,}"
            )

        st.divider()

        st.subheader("📖 Extracted Text")

        with st.expander("View Document Text"):

            st.text_area(
                "PDF Content",
                value=st.session_state.pdf_text[:50000],
                height=350
            )

        st.download_button(
            label="⬇️ Download Extracted Text",
            data=st.session_state.pdf_text,
            file_name="extracted_document.txt",
            mime="text/plain"
        )

        if st.button("Remove Current Document"):

            st.session_state.pdf_text = ""
            st.session_state.pdf_name = ""
            st.session_state.chat_history = []

            st.rerun()


# ==========================================
# AI ASSISTANT PAGE
# ==========================================

elif st.session_state.page == "AI Assistant":

    st.title("🤖 AI Document Assistant")

    st.write(
        "Ask questions about your uploaded PDF or ask general questions."
    )

    if st.session_state.pdf_name:

        st.success(
            f"Active Document: {st.session_state.pdf_name}"
        )

    else:

        st.info(
            "No PDF uploaded. You can still ask general AI questions."
        )

    st.divider()

    # DISPLAY CHAT HISTORY

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # USER QUESTION

    user_question = st.chat_input(
        "Ask anything about your document..."
    )

    if user_question:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_question
            }
        )

        with st.chat_message("user"):

            st.markdown(user_question)

        # BUILD PROMPT

        if st.session_state.pdf_text:

            document_text = st.session_state.pdf_text[:50000]

            prompt = f"""
You are DocuMind AI, an intelligent document assistant.

Answer the user's question using the uploaded PDF.

DOCUMENT NAME:
{st.session_state.pdf_name}

DOCUMENT CONTENT:
{document_text}

USER QUESTION:
{user_question}

INSTRUCTIONS:

1. Give clear and accurate answers.
2. Use the uploaded document whenever relevant.
3. Do not invent information that is not in the document.
4. If the answer is not available in the document,
   clearly explain that.
5. If the user asks a general knowledge question,
   answer using your general knowledge.
6. Support English and Hindi.
7. Use headings and bullet points when appropriate.
"""

        else:

            prompt = f"""
You are DocuMind AI, a helpful AI assistant.

Answer the following question clearly and accurately.

USER QUESTION:
{user_question}

Support English and Hindi.
Use examples and bullet points when useful.
"""

        # GENERATE AI RESPONSE

        with st.chat_message("assistant"):

            with st.spinner("DocuMind AI is thinking..."):

                answer = get_gemini_response(prompt)

                st.markdown(answer)

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    st.divider()

    if st.button("🗑️ Clear Chat History"):

        st.session_state.chat_history = []

        st.rerun()


# ==========================================
# ABOUT PAGE
# ==========================================

elif st.session_state.page == "About":

    st.title("ℹ️ About DocuMind AI")

    st.markdown("""
    ### DocuMind AI

    DocuMind AI is an AI-powered document question
    answering application.

    **Technologies Used:**

    - Python
    - Streamlit
    - Google Gemini API
    - PyPDF2
    - Generative Artificial Intelligence

    **Key Features:**

    - PDF document uploading
    - PDF text extraction
    - AI-powered question answering
    - Document summarization
    - Interactive chat interface
    - English and Hindi support

    **Purpose:**

    The purpose of this project is to make document
    understanding easier using Artificial Intelligence.

    **Deployment:**

    Streamlit Community Cloud.
    """)

    st.divider()

    st.markdown(
        "<h3 style='color:#D4AF37;'>Thank you for using DocuMind AI!</h3>",
        unsafe_allow_html=True
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown(
    """
    <center>
    <p style="color:gray;">
    © 2026 DocuMind AI | Powered by Google Gemini
    and Streamlit
    </p>
    </center>
    """,
    unsafe_allow_html=True
)
