import streamlit as st
import os
from groq import Groq
import base64
from PyPDF2 import PdfReader

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="ScopeAI 🖤", page_icon="🚀", layout="wide")

# --- 2. GENZ BLACK THEME CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: #0a0a0a;
        background-image: 
            radial-gradient(circle at 20% 50%, #1a1a2e 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, #16213e 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, #0f3460 0%, transparent 50%);
        font-family: 'Space Grotesk', sans-serif;
        color: #e0e0e0;
    }
    
    /* Glassmorphism Cards */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin-bottom: 16px;
        animation: slideUp 0.3s ease-out;
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Heading Glow */
    h1 {
        text-align: center;
        font-weight: 700;
        font-size: 3rem !important;
        background: linear-gradient(90deg, #00f5ff, #00d4ff, #b400ff, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow 3s ease-in-out infinite;
        margin-bottom: 8px !important;
    }
    
    @keyframes glow {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(0, 245, 255, 0.5)); }
        50% { filter: drop-shadow(0 0 40px rgba(180, 0, 255, 0.8)); }
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1rem;
        margin-bottom: 30px;
        letter-spacing: 2px;
    }
    
    /* Chat Input */
    .stChatInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
        border-radius: 16px !important;
        color: #fff !important;
        padding: 16px !important;
    }
    
    .stChatInput > div > div > input:focus {
        border: 1px solid #00f5ff !important;
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.3) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 10, 0.8);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stFileUploader {
        background: rgba(255, 255, 255, 0.03);
        border: 2px dashed rgba(0, 245, 255, 0.3);
        border-radius: 16px;
        padding: 20px;
    }
    
    .stFileUploader:hover {
        border: 2px dashed #00f5ff;
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.2);
    }
    
    /* User Message */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.1), rgba(180, 0, 255, 0.1));
        border: 1px solid rgba(0, 245, 255, 0.3);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown("<h1>ScopeAI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>NO CAP • JUST NCERT • GENZ MODE</p>", unsafe_allow_html=True)

# --- 4. GROQ SETUP - FIXED MODEL ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Yo! ScopeAI here fr 🖤 Drop your NCERT doubts, upload PDF or image. We gotchu bestie 💅"}]

# --- 5. SIDEBAR - UPLOAD ---
with st.sidebar:
    st.markdown("### 📎 Attach Files")
    st.markdown("<p style='color: #888; font-size: 0.85rem;'>Upload kr bhai, main padh lunga</p>", unsafe_allow_html=True)
    pdf_file = st.file_uploader("NCERT PDF", type="pdf", label_visibility="collapsed")
    img_file = st.file_uploader("Question Image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### ⚡ Vibe Check")
    st.markdown("<p style='color: #00f5ff; font-size: 0.9rem;'>Model: Llama 3.3 70B</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #b400ff; font-size: 0.9rem;'>Vision: Llama 3.2 90B</p>", unsafe_allow_html=True)

pdf_text = ""
if pdf_file:
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

# --- 6. SHOW CHATS ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 7. CHAT LOGIC ---
if prompt := st.chat_input("Spill the tea... what's your doubt? 👀"):
    
    if img_file:
        img_bytes = img_file.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode()
        message_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
        ]
        model_to_use = "llama-3.2-90b-vision-preview"
    else:
        message_content = prompt
        model_to_use = "llama-3.3-70b-versatile"

    if pdf_text:
        prompt_with_context = f"Answer from this NCERT PDF context only: {pdf_text[:3000]} \n\nQuestion: {prompt}"
        message_content = prompt_with_context

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # GenZ tone system prompt
    if len(prompt.split()) < 8:
        system_msg = "You are ScopeAI, a GenZ NCERT tutor. Reply in 2-3 lines max. Use Hinglish with GenZ slang like 'fr', 'no cap', 'bestie'. Be direct and helpful."
    else:
        system_msg = "You are ScopeAI, a GenZ NCERT tutor. Explain step-by-step in Hinglish with GenZ vibe. Use 'fr', 'lowkey', 'bestie', 'no cap' naturally. Keep it NCERT accurate but chill."

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=model_to_use,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": message_content},
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
