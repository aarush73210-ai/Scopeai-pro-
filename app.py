import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="ScopeAI - JEE/NEET Tutor", page_icon="⭐")
st.markdown("<h1 style='text-align: center; color: #A78BFA;'>⭐ ScopeAI</h1>", unsafe_allow_html=True)
st.divider()

try:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
except KeyError:
    st.error("😅 GROQ_API_KEY nahi mili! Render > Environment mein add karo")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("JEE/NEET ka sawal pucho..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("ScopeAI soch raha hai..."):
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Tum ScopeAI ho, JEE/NEET tutor. Hinglish mein simple samjhao."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                model="llama-3.1-8b-instant",
                temperature=0.7,
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
