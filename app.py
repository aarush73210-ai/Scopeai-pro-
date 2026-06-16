import streamlit as st
import requests
import base64
from groq import Groq
from PyPDF2 import PdfReader
from PIL import Image
import io

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ScopeAI - Doubt Solver", page_icon="🚀", layout="wide")

# Groq API Key - Render pe Environment Variable se aayegi
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "gsk_your_key_here")

# Initialize Groq
client = Groq(api_key=GROQ_API_KEY)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doubt_count" not in st.session_state:
    st.session_state.doubt_count = 0
if "is_pro" not in st.session_state:
    st.session_state.is_pro = False

FREE_LIMIT = 5

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🚀 ScopeAI")
    st.caption("GenZ ka Apna Doubt Solver")

    selected_class = st.selectbox("Class Select Kar", ["Class 6", "Class 7", "Class 8", "Class 9", "Class 10", "Class 11", "Class 12"], index=4)

    st.divider()

    # Usage Counter
    if not st.session_state.is_pro:
        remaining = FREE_LIMIT - st.session_state.doubt_count
        st.warning(f"Free Doubts Left: {remaining}/{FREE_LIMIT}")
        if st.button("⚡ Go Pro ₹49/month", use_container_width=True):
            st.toast("Payment gateway coming soon! Abhi Pro free hai 😉")
            st.session_state.is_pro = True
            st.rerun()
    else:
        st.success("✨ Pro User - Unlimited Doubts")

    st.divider()
    if st.button("🗑️ Chat Clear Karo", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Made with ❤️ for Students")

# ---------------- MAIN APP ----------------
st.title(f"ScopeAI 💡 {selected_class}")
st.caption("Photo kheech, PDF daal, ya type kar. Doubt solve ho jayega bhai!")

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📎 NCERT Question ya Notes ka Photo/PDF daal", type=["png", "jpg", "jpeg", "pdf"])

file_text = ""
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            file_text += page.extract_text()
        st.info(f"PDF padh liya: {len(file_text)} characters")
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=300)
        st.info("Image mil gayi. Ab neeche doubt likho ki isme kya puchna hai.")

# ---------------- CHAT INPUT ----------------
if prompt := st.chat_input("Yahan doubt likh bhai..."):

    # Check limit
    if not st.session_state.is_pro and st.session_state.doubt_count >= FREE_LIMIT:
        st.error("Free limit khatam! Pro le ₹49/month mein unlimited doubts 💎")
        st.stop()

    # Add user message
    full_prompt = prompt
    if file_text:
        full_prompt = f"Ye PDF ka content hai:\n{file_text[:3000]}\n\nUser ka doubt: {prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI Response
    with st.chat_message("assistant"):
        with st.spinner("Sooch raha hu bhai... 🧠"):
            try:
                system_prompt = f"""Tu ScopeAI hai, GenZ ka dost + teacher.
                User {selected_class} mein hai.
                NCERT ke hisaab se answer de, Hinglish mein, memes/example ke saath.
                Step-by-step samjha, boring mat hona.
                Last mein puch 'Samajh aaya kya bhai?'
                Agar question image/PDF se hai to uska reference de."""

                response = client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )

                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # Increase count
                if not st.session_state.is_pro:
                    st.session_state.doubt_count += 1

            except Exception as e:
                st.error(f"Error aa gaya bhai 😭: {str(e)}")
                st.info("Groq API key check kar Render ke Environment mein")

# ---------------- FOOTER ----------------
st.divider()
st.caption("ScopeAI v1.0 | Bhai doubt solve na ho to paise wapas 😎 | Made for Students")
