import streamlit as st
import os
import base64
import tempfile
import plotly.express as px
import pandas as pd
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from groq import Groq
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import speech_recognition as sr
import io
import re

# ----------------- CONFIG -----------------
st.set_page_config(page_title="ScopeAI Pro", page_icon="🧠", layout="wide")

# Dark UI CSS
st.markdown("""
<style>
   .stApp { background-color: #0E1117; color: #FAFAFA; }
   .stChatMessage { background-color: #262730; border-radius: 10px; padding: 10px; }
    h1, h2, h3 { color: #00D4FF!important; }
</style>
""", unsafe_allow_html=True)

# ----------------- GROQ SETUP -----------------
# Secrets se key lega
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("🚨 GROQ_API_KEY set nahi hai! Streamlit Secrets mein daalo.")
    st.stop()

# LATEST MODEL - Ye chalega 100%
MODEL_NAME = "llama-3.1-8b-instant"

# ----------------- SESSION STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

# ----------------- HELPER FUNCTIONS -----------------
def trim_text(text, max_chars=15000):
    """Groq ki token limit se bachne ke liye text chota karo"""
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[NOTE: Document bahut lamba tha, isliye starting ka part hi use kiya gaya hai]"
    return text

def extract_text_from_pdf(pdf_path):
    """PDF se text nikalo - OCR + Normal dono"""
    text = ""
    try:
        # Pehle normal text extract karo
        images = convert_from_path(pdf_path, dpi=200, first_page=1, last_page=10) # Sirf 10 page tak
        for i, image in enumerate(images):
            st.toast(f"Page {i+1}/10 scan kar raha hu...")
            # OCR se text
            page_text = pytesseract.image_to_string(image, lang='eng+hin')
            text += f"\n--- Page {i+1} ---\n{page_text}"
        return text
    except Exception as e:
        st.error(f"PDF Read Error: {e}")
        return ""

def extract_text_from_image(image):
    """Photo se text nikalo"""
    try:
        return pytesseract.image_to_string(image, lang='eng+hin')
    except Exception as e:
        st.error(f"Image Read Error: {e}")
        return ""

def auto_generate_graph(text):
    """Text mein marks/digits ho to auto graph banao"""
    try:
        # Pattern: Subject: 80, Hindi - 75
        pattern = r'([A-Za-z ]+)[:\-]\s*(\d{1,3})'
        matches = re.findall(pattern, text)
        if len(matches) >= 2:
            df = pd.DataFrame(matches, columns=['Subject', 'Marks'])
            df['Marks'] = pd.to_numeric(df['Marks'])
            df['Subject'] = df['Subject'].str.strip()
            fig = px.bar(df, x='Subject', y='Marks', title='Auto Generated Marks Graph', color='Subject')
            st.plotly_chart(fig, use_container_width=True)
            return True
    except:
        pass
    return False

def speech_to_text(audio_bytes):
    """Voice ko text mein badlo"""
    try:
        r = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language='hi-IN')
        return text
    except:
        return ""

def text_to_speech(text):
    """Text ko voice mein badlo"""
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

def get_groq_response():
    """Groq se jawab lao with error handling"""
    try:
        # Context trim karo taaki BadRequest na aaye
        pdf_context = trim_text(st.session_state.pdf_text, 12000)

        system_prompt = f"""You are ScopeAI Pro, ek helpful AI study buddy.
        User ne ye document upload kiya hai: {st.session_state.pdf_name}
        Document ka content: {pdf_context}

        Rules:
        1. Hamesha document ke base pe jawab do
        2. Agar answer document mein nahi hai to bolo "Ye information document mein nahi hai"
        3. Hinglish mein dosti se baat karo
        4. Chote-chote points mein samjhao"""

        # Last 6 messages hi bhejo taaki token kam lage
        messages_to_send = [{"role": "system", "content": system_prompt}]
        messages_to_send += st.session_state.messages[-6:]

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages_to_send,
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Groq Error: {str(e)}\n\nThodi der baad try karo ya API key check karo."

# ----------------- UI -----------------
st.title("🧠 ScopeAI Pro - Tera Personal Study Buddy")
st.caption("PDF, Photo, Voice sab samajhta hu | OCR + Graph + Memory")

# Sidebar
with st.sidebar:
    st.header("📁 File Upload")
    uploaded_file = st.file_uploader("PDF ya Photo daalo", type=['pdf', 'png', 'jpg', 'jpeg'])

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            with st.spinner("PDF padh raha hu... OCR mein time lagta hai"):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                st.session_state.pdf_text = extract_text_from_pdf(tmp_path)
                st.session_state.pdf_name = uploaded_file.name
                os.unlink(tmp_path)
                st.success(f"✅ {uploaded_file.name} read ho gaya!")
                auto_generate_graph(st.session_state.pdf_text)

        elif uploaded_file.type.startswith('image'):
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            with st.spinner("Photo se text nikal raha hu..."):
                img_text = extract_text_from_image(image)
                st.session_state.pdf_text += f"\n\n--- Image Text ---\n{img_text}"
                st.session_state.pdf_name = "Image + PDF"
                st.success("✅ Photo read ho gayi!")
                auto_generate_graph(img_text)

    st.divider()
    if st.button("🗑️ Chat Clear Karo"):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.session_state.pdf_name = ""
        st.rerun()

# Chat History Display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Voice + Text Input
col1, col2 = st.columns([6,1])
with col2:
    audio_bytes = audio_recorder(text="", icon_size="2x", neutral_color="#00D4FF")
with col1:
    prompt = st.chat_input("Kuch bhi pooch...")

# Voice Input Handle
if audio_bytes:
    with st.spinner("Sunn raha hu..."):
        voice_text = speech_to_text(audio_bytes)
        if voice_text:
            prompt = voice_text
            st.toast(f"🎤 Tune bola: {voice_text}")
        else:
            st.toast("❌ Awaz samajh nahi aayi, phir bol")

# Chat Logic
if prompt:
    # User message add karo
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Response
    with st.chat_message("assistant"):
        with st.spinner("Soch raha hu..."):
            if not st.session_state.pdf_text and not st.session_state.messages:
                response = "Bhai pehle koi PDF ya Photo upload kar de, tabhi toh jawab dunga 😅"
            else:
                response = get_groq_response()

            st.markdown(response)

            # Voice Output
            audio_fp = text_to_speech(response)
            if audio_fp:
                st.audio(audio_fp, format='audio/mp3')

    # Assistant message save karo
    st.session_state.messages.append({"role": "assistant", "content": response})
