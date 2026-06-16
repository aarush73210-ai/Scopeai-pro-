import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

# Page config
st.set_page_config(page_title="ScopeAI", page_icon="📚", layout="wide")

# Title
st.title("📚 ScopeAI - PDF Q&A Bot")
st.caption("Upload PDF aur sawaal poocho. Powered by Groq + Llama 3")

# Streamlit Secrets se API Key lena - YE IMPORTANT HAI
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error("⚠️ GROQ_API_KEY nahi mili. Streamlit Secrets mein add karo.")
    st.stop()

# PDF Upload
uploaded_file = st.file_uploader("PDF Upload Karo", type="pdf")

if uploaded_file:
    # PDF padhna
    pdf_reader = PdfReader(uploaded_file)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    # Text dikhana
    with st.expander("📄 PDF ka Text Dekho"):
        st.write(pdf_text[:2000] + "...")

    # Question input
    question = st.text_input("PDF se kya poochna hai?")

    if st.button("Jawab Do") and question:
        with st.spinner("Groq AI soch raha hai..."):
            try:
                # Groq ko prompt bhejna
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "Tum ek helpful assistant ho. Sirf diye gaye PDF context se jawab do. Agar jawab context mein nahi hai to bolo 'Ye PDF mein nahi hai'."
                        },
                        {
                            "role": "user",
                            "content": f"Context: {pdf_text[:8000]}\n\nQuestion: {question}"
                        }
                    ],
                    model="llama3-8b-8192",
                    temperature=0.3,
                    max_tokens=1024
                )

                # Jawab dikhana
                answer = chat_completion.choices[0].message.content
                st.success("✅ Jawab:")
                st.write(answer)

            except Exception as e:
                st.error(f"Error: {str(e)}")
else:
    st.info("👆 Upar PDF upload karo shuru karne ke liye")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit + Groq")
