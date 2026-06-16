import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

st.set_page_config(page_title="ScopeAI", page_icon="📚")
st.title("📚 ScopeAI - PDF Q&A Bot")

# YE LINE SABSE IMPORTANT HAI
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

uploaded_file = st.file_uploader("PDF Upload Karo", type="pdf")

if uploaded_file:
    pdf_reader = PdfReader(uploaded_file)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    question = st.text_input("PDF se kya poochna hai?")

    if st.button("Jawab Do") and question:
        with st.spinner("Groq AI soch raha hai..."):
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Sirf diye gaye PDF context se jawab do."},
                    {"role": "user", "content": f"Context: {pdf_text[:8000]}\n\nQuestion: {question}"}
                ],
                model="llama3-8b-8192"
            )
            st.write(response.choices[0].message.content)
else:
    st.info("👆 PDF upload karo")
