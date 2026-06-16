import streamlit as st
import os
from groq import Groq
import base64
from PyPDF2 import PdfReader

# --- 1. LIGHT BLUE THEME + ANIMATION ---
st.set_page_config(page_title="ScopeAI", page_icon="📘", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(-45deg, #e1f5fe, #b3e5fc, #81d4fa, #4fc3f7);
        background-size: 400% 400%;
        animation: gradient 12s ease infinite;
        font-family: 'Poppins', sans-serif;
    }
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #b3e5fc;
    }
    h1 {
        color: #0277bd; 
        text-align: center;
        font-weight: 600;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .stSidebar {
        background-color: rgba(255, 255, 255, 0.8);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>📘 ScopeAI - Your NCERT Buddy</h1>", unsafe_allow_html=True)

# --- 2. GROQ SETUP - FIXED FOR RENDER ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. WHATSAPP STYLE 📎 ATTACHMENT ---
with st.sidebar:
    st.header("📎 Upload Here")
    pdf_file = st.file_uploader("Upload NCERT PDF", type="pdf")
    img_file = st.file_uploader("Upload Question Image", type=["png", "jpg", "jpeg"])

pdf_text = ""
if pdf_file:
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

# --- 4. SHOW OLD CHATS ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. CHAT INPUT + LOGIC ---
if prompt := st.chat_input("Apna sawaal poocho ya 📎 se file bhejo..."):
    
    if img_file:
        img_bytes = img_file.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode()
        message_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
        ]
    else:
        message_content = prompt

    if pdf_text:
        prompt = f"Is PDF ke context se answer do: {pdf_text[:3000]} \n\nSawaal: {prompt}"
        message_content = prompt

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if len(prompt.split()) < 8:
        system_msg = "Give a short, direct answer in 2-3 lines. Hinglish mein."
    else:
        system_msg = "Give detailed step-by-step NCERT style answer. Hinglish mein."

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview" if img_file else "llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": message_content},
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
