```python
import streamlit as st
import PyPDF2
import io
from google import genai

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📚",
    layout="wide"
)

# ---------------- GEMINI API ----------------
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = ""

if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception:
        client = None
else:
    client = None

# ---------------- SESSION STATE ----------------
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "file_name" not in st.session_state:
    st.session_state.file_name = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- BLACK & GOLD DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background-color: #080808;
    color: #ffffff;
}

[data-testid="stSidebar"] {
    background-color: #111111;
}

h1, h2, h3 {
    color: #D4AF37 !important;
}

p, label {
    color: #eeeeee;
}

.stButton button {
    background-color: #D4AF37;
    color: black;
    border-radius: 10px;
    border: none;
    font-weight: bold;
}

.stButton button:hover {
    background-color: #F5D76E;
    color: black;
}

.gold-box {
    background: #151515;
    border: 1px solid #D4AF37;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- PDF EXTRACTION ----------------
def extract_pdf_text(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text, len(reader.pages)

    except Exception as e:
        st.error(f"PDF Error: {e}")
        return "", 0


# ---------------- SIDEBAR ----------------
st.sidebar.title("📚 DocuMind AI")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Documents", "AI Assistant"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📄 Upload Document")

uploaded_file = st.sidebar.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)

if uploaded_file is not None:
    if st.session_state.file_name != uploaded_file.name:
        text, pages = extract_pdf_text(uploaded_file)

        st.session_state.pdf_text = text
        st.session_state.file_name = uploaded_file.name

        if text:
            st.sidebar.success("PDF uploaded successfully!")
            st.sidebar.info(f"Pages: {pages}")
        else:
            st.sidebar.warning("No readable text found in PDF.")

if st.session_state.file_name:
    st.sidebar.caption(
        f"Current PDF: {st.session_state.file_name}"
    )

if st.sidebar.button("Remove PDF"):
    st.session_state.pdf_text = ""
    st.session_state.file_name = ""
    st.rerun()


# ---------------- HOME PAGE ----------------
if page == "Home":

    st.title("✨ DocuMind AI")

    st.markdown("""
    <div class="gold-box">
        <h2>Welcome to DocuMind AI</h2>
        <p>
        Your Intelligent AI Assistant for Documents
        and General Questions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="gold-box">
        <h3>📄 PDF Reader</h3>
        <p>Upload and read PDF documents.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="gold-box">
        <h3>🤖 AI Assistant</h3>
        <p>Ask questions and get AI answers.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="gold-box">
        <h3>💬 Smart Chat</h3>
        <p>Chat with AI and explore information.</p>
        </div>
        """, unsafe_allow_html=True)

    st.info("Upload a PDF from the sidebar to get started.")


# ---------------- DOCUMENTS PAGE ----------------
elif page == "Documents":

    st.title("📄 Document Manager")

    if st.session_state.pdf_text:

        st.success("Document loaded successfully!")

        st.write("**File Name:**", st.session_state.file_name)

        st.markdown("### Extracted PDF Text")

        with st.expander("View Document Content"):
            st.text(st.session_state.pdf_text[:20000])

    else:
        st.warning("Please upload a PDF from the sidebar first.")


# ---------------- AI ASSISTANT PAGE ----------------
elif page == "AI Assistant":

    st.title("🤖 DocuMind AI Assistant")

    st.markdown(
        "Ask anything! You can ask general questions "
        "or questions about your uploaded PDF."
    )

    if not client:
        st.error(
            "Gemini API Key not found. "
            "Please check your .streamlit/secrets.toml file."
        )
        st.stop()

    if st.session_state.pdf_text:
        st.success(
            f"Using document: {st.session_state.file_name}"
        )
    else:
        st.info(
            "No PDF uploaded. You can still ask general questions!"
        )

    # Display previous chat
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_question = st.chat_input("Ask me anything...")

    if user_question:

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.markdown(user_question)

        # Create AI prompt
        if st.session_state.pdf_text:

            prompt = f"""
You are DocuMind AI, a helpful and intelligent assistant.

Answer the user's question using the uploaded PDF
when the question is related to the document.

If the answer is not available in the PDF,
answer using your general knowledge.

UPLOADED DOCUMENT:
{st.session_state.pdf_text[:50000]}

USER QUESTION:
{user_question}

Give a clear, accurate and helpful answer.
"""

        else:

            prompt = f"""
You are DocuMind AI, a helpful AI assistant.

Answer the following question clearly and accurately.
You can answer general knowledge, education,
technology, programming and other questions.

USER QUESTION:
{user_question}
"""

        with st.chat_message("assistant"):

            with st.spinner("DocuMind AI is thinking..."):

                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )

                    answer = response.text

                    if not answer:
                        answer = "Sorry, I could not generate an answer."

                    st.markdown(answer)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:
                    st.error(f"Gemini API Error: {e}")

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


# ---------------- FOOTER ----------------
st.sidebar.markdown("---")
st.sidebar.caption("✨ Powered by DocuMind AI")
st.sidebar.caption("Black & Gold Edition")
```
