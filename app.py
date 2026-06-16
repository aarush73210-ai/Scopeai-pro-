import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import io
import re
from streamlit_mic_recorder import mic_recorder

# ========== PAGE CONFIG - GENZ DARK UI ==========
st.set_page_config(page_title="ScopeAI Pro", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# Custom CSS - Dark Professional GenZ Vibe
st.markdown("""
<style>
   .stApp { background: #0E1117; color: #FAFAFA; }
   .stChatMessage { background: #1E1E2E; border-radius: 15px; padding: 1rem; margin: 0.5rem 0; }
   .stButton>button {
        background: linear-gradient(90deg, #7F5AF0 0%, #2CB67D 100%);
        color: white; border: none; border-radius: 10px; font-weight: 600;
    }
   .stButton>button:hover { transform: scale(1.02); transition: 0.2s; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 800; }
   .st-emotion-cache-1y4p8pa { padding: 2rem 1rem; }
</style>
""", unsafe_allow_html=True)

# ========== GROQ CLIENT ==========
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"❌ Secret Error: {e}")
    st.stop()

# ========== SESSION STATE ==========
if "messages" not in st.session_state: st.session_state.messages = []
if "pdf_text" not in st.session_state: st.session_state.pdf_text = ""
if "pdf_name" not in st.session_state: st.session_state.pdf_name = ""
if "df" not in st.session_state: st.session_state.df = None

# ========== HELPER FUNCTIONS ==========
@st.cache_data(show_spinner=False)
def extract_text_from_pdf(_file_bytes):
    text = ""
    # Try normal text first
    try:
        pdf_reader = PdfReader(io.BytesIO(_file_bytes))
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text: text += page_text + "\n"
    except: pass

    # OCR if no text found - Poppler fix included
    if not text.strip():
        images = convert_from_bytes(_file_bytes, dpi=200) # Lower DPI = faster
        for i, image in enumerate(images):
            text += pytesseract.image_to_string(image, lang='eng+hin') + "\n"
    return text

def transcribe_audio(audio_bytes):
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3", file=audio_file
        )
        return transcription.text
    except Exception as e:
        st.error(f"Voice Error: {e}")
        return None

def extract_and_plot_data(text):
    # Simple table detection: marks, subjects, numbers
    pattern = r'([A-Za-z ]+)[\s:]+(\d+)' # "Subject: 80" type
    matches = re.findall(pattern, text)
    if len(matches) >= 3:
        df = pd.DataFrame(matches, columns=['Item', 'Value'])
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df = df.dropna()
        if not df.empty:
            st.session_state.df = df
            return True
    return False

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("🚀 ScopeAI Pro")
    st.caption("PDF + Voice + Photo + Graph")

    uploaded_file = st.file_uploader("📄 PDF Upload", type="pdf")
    uploaded_image = st.file_uploader("🖼️ Image Upload", type=["png", "jpg", "jpeg"])

    if st.button("🔄 Reset All", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.session_state.pdf_name = ""
        st.session_state.df = None
        st.rerun()

# ========== MAIN AREA ==========
st.title("💬 ScopeAI Pro")
st.caption("GenZ AI Assistant - Chat, Voice, PDF, Graph sab ek jagah")

# Process PDF
if uploaded_file and uploaded_file.name!= st.session_state.pdf_name:
    with st.spinner("📄 PDF Process ho raha hai..."):
        st.session_state.pdf_text = extract_text_from_pdf(uploaded_file.getvalue())
        st.session_state.pdf_name = uploaded_file.name
        st.session_state.messages = []
        if st.session_state.pdf_text:
            st.toast(f"✅ {uploaded_file.name} loaded!", icon="📚")
            extract_and_plot_data(st.session_state.pdf_text)
        else:
            st.error("PDF se text nahi nikla")

# Process Image
if uploaded_image:
    with st.spinner("🖼️ Image padh raha hu..."):
        img = Image.open(uploaded_image)
        img_text = pytesseract.image_to_string(img, lang='eng+hin')
        if img_text.strip():
            st.session_state.pdf_text += f"\n\nImage Text:\n{img_text}"
            st.toast("✅ Image text add ho gaya!", icon="🖼️")

# Show Graph if data exists
if st.session_state.df is not None:
    with st.expander("📊 Auto-Detected Graph", expanded=True):
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#0E1117')
        ax.set_facecolor('#1E1E2E')
        ax.bar(st.session_state.df['Item'], st.session_state.df['Value'], color='#7F5AF0')
        ax.tick_params(colors='white')
        ax.set_title('Data from PDF', color='white')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Voice + Text Input
col1, col2 = st.columns([6, 1])
with col2:
    audio = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='recorder')

prompt = st.chat_input("Message likho ya mic daba ke bolo...")

# Handle voice input
if audio:
    with st.spinner("🎧 Voice to Text..."):
        voice_text = transcribe_audio(audio['bytes'])
        if voice_text: prompt = voice_text

# Handle chat
if prompt:
    if not st.session_state.pdf_text:
        st.warning("Pehle PDF ya Image upload karo bhai")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 AI soch raha hai..."):
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are ScopeAI Pro. Context: {st.session_state.pdf_text[:12000]}. Reply in Hinglish, GenZ style, short and helpful. Use emojis. Remember chat history."},
                    *st.session_state.messages
                ],
                model="llama3-8b-8192",
                temperature=0.3
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
