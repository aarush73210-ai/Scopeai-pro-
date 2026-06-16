import streamlit as st
import os
from groq import Groq
import base64
from PyPDF2 import PdfReader
import time
import hashlib

# --- 1. CONFIG ---
st.set_page_config(page_title="ScopeAI Pro Max 🖤", page_icon="🚀", layout="wide")

# --- 2. GENZ BLACK PRO MAX CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&family=JetBrains+Mono&display=swap');

   .stApp {
        background: #000;
        background-image:
            radial-gradient(circle at 10% 20%, rgba(0, 245, 255, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(180, 0, 255, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(255, 0, 255, 0.05) 0%, transparent 50%);
        font-family: 'Space Grotesk', sans-serif;
        color: #e0e0e0;
    }

   .stApp::before {
        content: '';
        position: fixed;
        width: 100%;
        height: 100%;
        background-image:
            radial-gradient(2px 2px at 20% 30%, #00f5ff, transparent),
            radial-gradient(2px 2px at 60% 70%, #b400ff, transparent),
            radial-gradient(1px 1px at 50% 50%, #ff00ff, transparent);
        background-size: 200% 200%;
        animation: particles 20s linear infinite;
        pointer-events: none;
        opacity: 0.3;
    }

    @keyframes particles {
        0% { background-position: 0% 0%; }
        100% { background-position: 100% 100%; }
    }

   .stChatMessage {
        background: rgba(15, 15, 25, 0.6);
        backdrop-filter: blur(24px);
        border-radius: 24px;
        padding: 24px;
        border: 1px solid rgba(0, 245, 255, 0.2);
        box-shadow:
            0 8px 32px 0 rgba(0, 0, 0, 0.5),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateY(30px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    h1 {
        text-align: center;
        font-weight: 700;
        font-size: 3.5rem!important;
        background: linear-gradient(90deg, #00f5ff, #00d4ff, #b400ff, #ff00ff, #00f5ff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glowGradient 3s linear infinite;
        margin-bottom: 8px!important;
        letter-spacing: -1px;
    }

    @keyframes glowGradient {
        0% { background-position: 0% center; filter: drop-shadow(0 0 30px rgba(0, 245, 255, 0.6)); }
        50% { background-position: 100% center; filter: drop-shadow(0 0 40px rgba(180, 0, 255, 0.8)); }
        100% { background-position: 0% center; filter: drop-shadow(0 0 30px rgba(0, 245, 255, 0.6)); }
    }

   .subtitle {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 40px;
        letter-spacing: 4px;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }

   .stChatInput > div > div > input {
        background: rgba(20, 20, 30, 0.8)!important;
        backdrop-filter: blur(24px);
        border: 2px solid rgba(0, 245, 255, 0.3)!important;
        border-radius: 20px!important;
        color: #fff!important;
        padding: 18px 24px!important;
        font-size: 1rem!important;
        transition: all 0.3s ease;
    }

   .stChatInput > div > div > input:focus {
        border: 2px solid #00f5ff!important;
        box-shadow: 0 0 30px rgba(0, 245, 255, 0.4), inset 0 0 20px rgba(0, 245, 255, 0.1)!important;
    }

    [data-testid="stSidebar"] {
        background: rgba(5, 5, 10, 0.9);
        backdrop-filter: blur(24px);
        border-right: 1px solid rgba(0, 245, 255, 0.2);
    }

   .stFileUploader {
        background: rgba(0, 245, 255, 0.03);
        border: 2px dashed rgba(0, 245, 255, 0.4);
        border-radius: 20px;
        padding: 24px;
        transition: all 0.3s ease;
    }

   .stFileUploader:hover {
        border: 2px dashed #00f5ff;
        background: rgba(0, 245, 255, 0.08);
        box-shadow: 0 0 30px rgba(0, 245, 255, 0.3);
        transform: scale(1.02);
    }

   .stButton > button {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.2), rgba(180, 0, 255, 0.2));
        border: 1px solid rgba(0, 245, 255, 0.4);
        border-radius: 16px;
        color: #00f5ff;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }

   .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.4), rgba(180, 0, 255, 0.4));
        border: 1px solid #00f5ff;
        box-shadow: 0 0 25px rgba(0, 245, 255, 0.5);
        transform: translateY(-2px);
    }

   .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.15), rgba(180, 0, 255, 0.15));
        border: 1px solid rgba(0, 245, 255, 0.4);
    }

   .stCodeBlock {
        background: rgba(0, 0, 0, 0.5)!important;
        border: 1px solid rgba(0, 245, 255, 0.2)!important;
        border-radius: 12px!important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
   .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown("<h1>ScopeAI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>// powered by groq • built for genz • no cap • no repeat</p>", unsafe_allow_html=True)

# --- 4. GROQ SETUP ---
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    st.error("Bruh API key missing hai 😭 Render > Environment mein GROQ_API_KEY daal")
    st.stop()

# --- 5. SESSION STATE INIT + ANTI-REPEAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Yo bestie! 🖤 ScopeAI Pro Max here.\n\nPDF, image, ya sawal - kuch bhi drop karo. NCERT ka boss hu main fr 💯\n\n*Tip: Short sawal = 2 line reply, Long sawal = Full breakdown*"
    }]

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "last_msg_hash" not in st.session_state:
    st.session_state.last_msg_hash = ""

if "last_submit_time" not in st.session_state:
    st.session_state.last_submit_time = 0

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🚀 Control Panel")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.pdf_text = ""
        st.session_state.last_msg_hash = ""
        st.rerun()

    st.markdown("---")
    st.markdown("### 📎 Upload Files")
    st.markdown("<p style='color: #666; font-size: 0.8rem;'>Max 200MB • PDF/Image only</p>", unsafe_allow_html=True)

    pdf_file = st.file_uploader("NCERT PDF", type="pdf", label_visibility="collapsed")
    img_file = st.file_uploader("Question Image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

    if pdf_file:
        try:
            with st.spinner("PDF padh raha hu bestie... 📚"):
                pdf_reader = PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages[:5]:
                    text += page.extract_text()
                st.session_state.pdf_text = text[:3000]
                st.success(f"PDF loaded! {len(st.session_state.pdf_text)} chars")
        except Exception as e:
            st.error(f"PDF error: {str(e)[:50]}")

    st.markdown("---")
    st.markdown("### ⚡ Stats")
    st.markdown(f"<p style='color: #00f5ff;'>Messages: {len(st.session_state.messages)}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #b400ff;'>Model: Llama 3.3</p>", unsafe_allow_html=True)

    if len(st.session_state.messages) > 1:
        chat_text = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button(
            "💾 Download Chat",
            chat_text,
            file_name="scopeai_chat.txt",
            use_container_width=True
        )

# --- 7. SHOW CHATS ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 8. CHAT INPUT + ANTI-REPEAT LOGIC ---
if prompt := st.chat_input("Spill your doubt bestie... 👀"):

    # ANTI-REPEAT CHECK 1: Hash compare
    msg_hash = hashlib.md5(prompt.encode()).hexdigest()

    # ANTI-REPEAT CHECK 2: Time gap - 2 sec ke andar same msg block
    current_time = time.time()
    time_gap = current_time - st.session_state.last_submit_time

    if msg_hash == st.session_state.last_msg_hash and time_gap < 2:
        st.warning("Bruh spam mat kar 😭 Same msg dobara bhej raha hai. 2 sec ruk ja")
        st.stop()

    # Update trackers
    st.session_state.last_msg_hash = msg_hash
    st.session_state.last_submit_time = current_time

    # ANTI-REPEAT CHECK 3: Last user msg se compare
    if len(st.session_state.messages) > 1:
        last_user_msg = next((m for m in reversed(st.session_state.messages) if m["role"] == "user"), None)
        if last_user_msg and last_user_msg["content"] == prompt:
            st.warning("Bestie ye sawaal abhi poocha tha 😅 Alag sawaal bhej")
            st.stop()

    # Prepare message with image
    if img_file:
        try:
            img_bytes = img_file.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode()
            message_content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
            ]
            model_to_use = "llama-3.2-90b-vision-preview"
        except:
            st.error("Image load nahi hui bestie 😭")
            st.stop()
    else:
        message_content = prompt
        model_to_use = "llama-3.3-70b-versatile"

    # Add PDF context
    if st.session_state.pdf_text:
        prompt_with_context = f"Answer ONLY from this NCERT context: {st.session_state.pdf_text}\n\nQ: {prompt}"
        message_content = prompt_with_context if not img_file else [
            {"type": "text", "text": prompt_with_context},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
        ]

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # System prompt
    if len(prompt.split()) < 8:
        system_msg = "You are ScopeAI Pro Max, a GenZ NCERT tutor. Reply in 2-3 lines ONLY. Use Hinglish + GenZ slang: fr, no cap, bestie, lowkey, bussin. Be accurate but chill."
    else:
        system_msg = "You are ScopeAI Pro Max, a GenZ NCERT tutor. Give detailed step-by-step NCERT answers. Use Hinglish + GenZ vibe naturally: fr, lowkey, bestie, no cap, slay. Make it fun but 100% correct."

    # Generate response
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking fr... 🧠"):
                stream = client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {"role": "system", "content": system_msg},
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]],
                    ],
                    stream=True,
                    temperature=0.7,
                    max_tokens=1024,
                )
                response = st.write_stream(stream)
        except Exception as e:
            response = f"Bruh error aa gaya 😭: {str(e)[:100]}\n\nRetry karo bestie ya Groq API limit check karo."
            st.error(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
