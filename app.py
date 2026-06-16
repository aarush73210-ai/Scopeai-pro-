import streamlit as st
from groq import Groq
import base64
from PyPDF2 import PdfReader

# --- 1. LIGHT BLUE THEME + ANIMATION ---
st.set_page_config(page_title="ScopeAI", page_icon="📘", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(-45deg, #e0f7fa, #b2ebf2, #80deea, #4dd0e1);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stChatInput {background-color: white;}
    h1 {color: #01579b; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>📘 ScopeAI - Your NCERT Buddy</h1>", unsafe_allow_html=True)

# --- 2. GROQ SETUP ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. WHATSAPP STYLE 📎 ATTACHMENT ---
with st.sidebar:
    st.header("📎 Upload Here")
    pdf_file = st.file_uploader("Upload NCERT PDF", type="pdf")
    img_file = st.file_uploader("Upload Question Image", type=["png", "jpg", "jpeg"])
    audio_file = st.file_uploader("Upload Voice Question", type=["wav", "mp3", "m4a"])

pdf_text = ""
if pdf_file:
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

# --- 4. SHOW OLD CHATS ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. CHAT INPUT + DEPENDING ON QUESTION LOGIC ---
if prompt := st.chat_input("Apna sawaal poocho ya 📎 se file bhejo..."):
    
    # Agar image bheji hai to
    if img_file:
        img_bytes = img_file.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode()
        prompt = f"Is image mein jo question hai uska answer do: {prompt}"
        message_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
        ]
    else:
        message_content = prompt

    # Agar PDF bheji hai to context add karo
    if pdf_text:
        prompt = f"Is PDF ke context se answer do: {pdf_text[:3000]} \n\nSawaal: {prompt}"
        message_content = prompt

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- 3. DEPENDING ON QUESTION: Short vs Long ---
    if len(prompt.split()) < 8:
        system_msg = "Give a short, direct answer in 2-3 lines. Hinglish mein."
    else:
        system_msg = "Give detailed step-by-step NCERT style answer. Hinglish mein."

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": message_content},
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
