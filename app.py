import streamlit as st
from groq import Groq
import os
from pypdf import PdfReader
from PIL import Image
import base64
import hashlib

# ====== PAGE CONFIG ======
st.set_page_config(
    page_title="ScopeAI - NCERT ka scene, ScopeAI se clean",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ====== GENZ BLACK THEME CSS ======
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

  .main {
        background: #0a0a0a;
    }

  .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
    }

    h1 {
        background: linear-gradient(90deg, #00F5FF, #FF00FF, #00FF88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem!important;
        text-align: center;
        animation: glow 2s ease-in-out infinite alternate;
        margin-bottom: 0px;
    }

   .tagline {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 30px;
        font-weight: 500;
    }

    @keyframes glow {
        from { filter: drop-shadow(0 0 10px #00F5FF); }
        to { filter: drop-shadow(0 0 20px #FF00FF); }
    }

  .stButton>button {
        background: linear-gradient(90deg, #00F5FF, #FF00FF);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s;
    }

  .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px #00F5FF;
    }

  .stChatMessage {
        background: #1a1a1a!important;
        border: 1px solid #333!important;
        border-radius: 16px!important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ====== SESSION STATE ======
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_question_hash" not in st.session_state:
    st.session_state.last_question_hash = ""

# ====== GROQ CLIENT ======
@st.cache_resource
def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("🚨 Bruh API key missing fr. Render > Environment > GROQ_API_KEY daal bestie")
        st.stop()
    return Groq(api_key=api_key)

client = get_groq_client()

# ====== HEADER WITH TAGLINE ======
st.markdown("<h1>ScopeAI 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>NCERT ka scene, ScopeAI se clean 🖤</p>", unsafe_allow_html=True)

# ====== ANTI-REPEAT HASH ======
def get_question_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

# ====== MAIN LOGIC ======
col1, col2, col3 = st.columns([1,6,1])
with col2:

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # File uploaders
    with st.expander("📎 Upload PDF/Image for doubts"):
        uploaded_pdf = st.file_uploader("Drop NCERT PDF", type="pdf")
        uploaded_img = st.file_uploader("Drop Question Image", type=["png", "jpg", "jpeg"])

    # Chat input
    if prompt := st.chat_input("Pucho NCERT ka sawaal bestie..."):

        # Extract PDF text if uploaded
        pdf_text = ""
        if uploaded_pdf:
            try:
                pdf_reader = PdfReader(uploaded_pdf)
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text()
                pdf_text = pdf_text[:3000] # Limit for RAM
                st.toast("PDF loaded fr ✅", icon="📄")
            except Exception as e:
                st.toast(f"PDF error bestie: {e}", icon="❌")

        # Check image uploaded
        img_context = ""
        if uploaded_img:
            st.toast("Image dekh li bestie 📸", icon="✅")
            img_context = "User ne ek image upload ki hai. Question image se related ho sakta hai."

        # Anti-repeat check
        current_hash = get_question_hash(prompt + pdf_text)
        if current_hash == st.session_state.last_question_hash:
            st.toast("Bhai same sawaal repeat mat kar 🙏", icon="⚠️")
            st.stop()

        st.session_state.last_question_hash = current_hash

        # Add user message
        full_prompt = prompt
        if pdf_text:
            full_prompt = f"PDF Context: {pdf_text}\n\nQuestion: {prompt}"
        if img_context:
            full_prompt = f"{img_context}\n\nQuestion: {prompt}"

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI Response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            try:
                # System prompt for GenZ vibe + NCERT accuracy
                system_msg = """You are ScopeAI, a GenZ NCERT study buddy for Indian students class 6-12.
                Reply in Hinglish with GenZ slang: 'bhai', 'fr', 'no cap', 'bestie', 'scene', 'vibe'.
                Be 100% accurate for NCERT but keep it fun and short.
                If question is short/simple, give 2-3 line answer max.
                If complex, give step-by-step but still GenZ style.
                Never repeat same answer. Always add emojis.
                If user uploads PDF, use that context to answer.
                If user uploads image, assume question is about that image.
                Tagline: NCERT ka scene, ScopeAI se clean."""

                messages = [{"role": "system", "content": system_msg}]
                messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])

                # Stream response
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024,
                    stream=True
                )

                full_response = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"Bruh error aa gaya: {str(e)} 😭 Check API key ya model name")

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_question_hash = ""
        st.rerun()

# ====== FOOTER ======
st.markdown("<p style='text-align: center; color: #444; margin-top: 50px;'>Made with 💜 for NCERT students | NCERT ka scene, ScopeAI se clean | ScopeAI 2026</p>", unsafe_allow_html=True)
