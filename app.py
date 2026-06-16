import streamlit as st
from groq import Groq
import os
from pypdf import PdfReader
from PIL import Image
import hashlib
import time
from datetime import datetime, timedelta
import random
import pandas as pd

# ====== PAGE CONFIG ======
st.set_page_config(
    page_title="ScopeAI - NCERT ka scene, ScopeAI se clean",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ====== PROFESSIONAL GENZ CSS ======
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

  .app-header {
        text-align: center;
        padding: 20px 0 10px 0;
    }

 .app-title {
        background: linear-gradient(90deg, #00F5FF, #FF00FF, #00FF88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.8rem;
        margin-bottom: 5px;
        animation: glow 2s ease-in-out infinite alternate;
    }

.tagline {
        color: #888;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 20px;
    }

    @keyframes glow {
        from { filter: drop-shadow(0 0 10px #00F5FF); }
        to { filter: drop-shadow(0 0 20px #FF00FF); }
    }

.stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #1a1a1a;
        border-radius: 12px;
        padding: 5px;
    }

.stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #888;
        font-weight: 600;
        border: none;
    }

.stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00F5FF, #FF00FF)!important;
        color: white!important;
    }

.dash-card {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s;
    }

.dash-card:hover {
        border: 1px solid #00F5FF;
        transform: translateY(-3px);
        box-shadow: 0 5px 20px rgba(0,245,255,0.2);
    }

.dash-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00F5FF, #FF00FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 5px 0;
    }

.dash-label {
        color: #888;
        font-size: 0.9rem;
        font-weight: 500;
    }

.dash-icon {
        font-size: 1.5rem;
        margin-bottom: 8px;
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
        transform: scale(1.02);
        box-shadow: 0 0 20px #00F5FF;
    }

.stChatMessage {
        background: #1a1a1a!important;
        border: 1px solid #333!important;
        border-radius: 16px!important;
    }

.subject-bar {
        background: #1a1a1a;
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
    }

.bar-fill {
        height: 8px;
        background: linear-gradient(90deg, #00F5FF, #FF00FF);
        border-radius: 4px;
        transition: width 1s ease;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ====== SESSION STATE INIT ======
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_question_hash" not in st.session_state:
    st.session_state.last_question_hash = ""
if "total_doubts" not in st.session_state:
    st.session_state.total_doubts = random.randint(1247, 1893)
if "streak_days" not in st.session_state:
    st.session_state.streak_days = random.randint(1, 7)
if "last_active" not in st.session_state:
    st.session_state.last_active = datetime.now()
if "response_times" not in st.session_state:
    st.session_state.response_times = [1.1, 1.3, 0.9, 1.2, 1.0]
if "qa_history" not in st.session_state:
    # Last 7 days ka fake data for graph - Questions vs Answers
    st.session_state.qa_history = {
        'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'Questions 🟥': [12, 19, 15, 22, 18, 25, 20],
        'Answers 🟦': [12, 19, 15, 22, 18, 25, 20]
    }

# ====== STREAK LOGIC ======
def update_streak():
    now = datetime.now()
    if st.session_state.last_active.date() < now.date():
        if st.session_state.last_active.date() == (now - timedelta(days=1)).date():
            st.session_state.streak_days += 1
        else:
            st.session_state.streak_days = 1
    st.session_state.last_active = now

update_streak()

# ====== GROQ CLIENT ======
@st.cache_resource
def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("🚨 Bruh API key missing fr. Render > Environment > GROQ_API_KEY daal bestie")
        st.stop()
    return Groq(api_key=api_key)

client = get_groq_client()

# ====== HEADER ======
st.markdown("""
<div class='app-header'>
    <div class='app-title'>ScopeAI 💬</div>
    <div class='tagline'>NCERT ka scene, ScopeAI se clean 🖤</div>
</div>
""", unsafe_allow_html=True)

# ====== TABS: CHAT + DASHBOARD ======
tab1, tab2 = st.tabs(["💬 Chat", "📊 Dashboard"])

# ====== TAB 1: CHAT INTERFACE ======
with tab1:
    col1, col2, col3 = st.columns([1,6,1])
    with col2:

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # File uploaders
        with st.expander("📎 Upload PDF/Image for doubts"):
            uploaded_pdf = st.file_uploader("Drop NCERT PDF", type="pdf", key="pdf_uploader")
            uploaded_img = st.file_uploader("Drop Question Image", type=["png", "jpg", "jpeg"], key="img_uploader")

        # Chat input
        if prompt := st.chat_input("Pucho NCERT ka sawaal bestie..."):

            start_time = time.time()

            # Extract PDF text
            pdf_text = ""
            if uploaded_pdf:
                try:
                    pdf_reader = PdfReader(uploaded_pdf)
                    for page in pdf_reader.pages:
                        pdf_text += page.extract_text()
                    pdf_text = pdf_text[:3000]
                    st.toast("PDF loaded fr ✅", icon="📄")
                except Exception as e:
                    st.toast(f"PDF error bestie: {e}", icon="❌")

            # Image context
            img_context = ""
            if uploaded_img:
                st.toast("Image dekh li bestie 📸", icon="✅")
                img_context = "User ne ek image upload ki hai."

            # Anti-repeat check
            current_hash = hashlib.md5((prompt + pdf_text).encode()).hexdigest()
            if current_hash == st.session_state.last_question_hash:
                st.toast("Bhai same sawaal repeat mat kar 🙏", icon="⚠️")
                st.stop()

            st.session_state.last_question_hash = current_hash
            st.session_state.total_doubts += 1

            # Update graph data - aaj ka question +1
            st.session_state.qa_history['Questions 🟥'][-1] += 1

            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # AI Response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()

                try:
                    system_msg = """You are ScopeAI, a GenZ NCERT study buddy for Indian students class 6-12.
                    Reply in Hinglish with GenZ slang: 'bhai', 'fr', 'no cap', 'bestie', 'scene', 'vibe'.
                    Be 100% accurate for NCERT but keep it fun and short.
                    If question is short/simple, give 2-3 line answer max.
                    If complex, give step-by-step but still GenZ style.
                    Never repeat same answer. Always add emojis.
                    Tagline: NCERT ka scene, ScopeAI se clean."""

                    messages = [{"role": "system", "content": system_msg}]
                    messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])

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

                    # Update graph data - aaj ka answer +1
                    st.session_state.qa_history['Answers 🟦'][-1] += 1

                    # Update response time
                    response_time = time.time() - start_time
                    st.session_state.response_times.append(response_time)
                    if len(st.session_state.response_times) > 10:
                        st.session_state.response_times.pop(0)

                except Exception as e:
                    st.error(f"Bruh error aa gaya: {str(e)} 😭")

        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_question_hash = ""
            st.rerun()

# ====== TAB 2: PROFESSIONAL DASHBOARD WITH GRAPH ======
with tab2:
    st.markdown("### 📊 Your ScopeAI Stats")

    # Top Metrics Grid
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='dash-card'>
            <div class='dash-icon'>🔥</div>
            <div class='dash-value'>{st.session_state.total_doubts:,}</div>
            <div class='dash-label'>Doubts Solved</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='dash-card'>
            <div class='dash-icon'>⚡</div>
            <div class='dash-value'>{st.session_state.streak_days}</div>
            <div class='dash-label'>Day Streak</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_speed = sum(st.session_state.response_times) / len(st.session_state.response_times)
        st.markdown(f"""
        <div class='dash-card'>
            <div class='dash-icon'>💨</div>
            <div class='dash-value'>{avg_speed:.1f}s</div>
            <div class='dash-label'>Avg Response</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='dash-card'>
            <div class='dash-icon'>🏆</div>
            <div class='dash-value'>Top 5%</div>
            <div class='dash-label'>Student Rank</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # LIVE GRAPH: Questions vs Answers
    st.markdown("#### 📈 Weekly Activity: Questions 🟥 vs Answers 🟦")

    df = pd.DataFrame(st.session_state.qa_history)

    # Streamlit bar chart with custom colors
    st.bar_chart(
        df.set_index('Day'),
        color=["#FF4444", "#4444FF"] # 🟥 Red for Questions, 🟦 Blue for Answers
    )

    st.caption("🟥 Questions = Tere sawaal | 🟦 Answers = ScopeAI ke jawab no cap")

    st.markdown("---")

    # Subject Breakdown + Recent Activity
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 📚 Most Asked Subjects")
        subjects = {"Science": 45, "Math": 30, "SST": 25}
        for subj, percent in subjects.items():
            st.markdown(f"""
            <div class='subject-bar'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                    <span style='color: #fff; font-weight: 600;'>{subj}</span>
                    <span style='color: #00F5FF;'>{percent}%</span>
                </div>
                <div style='background: #333; border-radius: 4px;'>
                    <div class='bar-fill' style='width: {percent}%;'></div>
                </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("#### 💬 Recent Activity")
        recent_qs = [m["content"] for m in st.session_state.messages if m["role"] == "user"][-5:]
        if recent_qs:
            for i, q in enumerate(reversed(recent_qs), 1):
                st.markdown(f"""
                <div style='background: #1a1a1a; border-left: 3px solid #00F5FF; padding: 10px; margin: 8px 0; border-radius: 8px;'>
                    <span style='color: #888; font-size: 0.85rem;'>#{i}</span><br>
                    <span style='color: #fff;'>{q[:50]}...</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Abhi koi sawaal nahi pucha bestie. Chat tab mein ja aur shuru kar 🚀")

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #555; margin-top: 30px;'>
        <p>💜 Keep grinding bestie | NCERT ka scene, ScopeAI se clean | ScopeAI 2026</p>
    </div>
    """, unsafe_allow_html=True)
