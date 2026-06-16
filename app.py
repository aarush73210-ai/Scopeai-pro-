import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

# Page setup
st.set_page_config(page_title="ScopeAI", page_icon="📚", layout="centered")
st.title("📚 ScopeAI - PDF Q&A Bot")
st.caption("Apni PDF upload karo aur Groq AI se sawal poocho")

# Secret check - Ye zaroori hai
try:
    api_key = st.secrets["GROQ_API_KEY"]
    if not api_key:
        st.error("❌ GROQ_API_KEY Secrets mein nahi mili. Settings mein add karo.")
        st.stop()
    client = Groq(api_key=api_key)
except Exception as e:
    st.error(f"❌ Secret Error: {e}")
    st.stop()

# PDF Upload
uploaded_file = st.file_uploader("PDF File Upload Karo", type="pdf")

if uploaded_file is not None:
    # PDF padho
    pdf_reader = PdfReader(uploaded_file)
    pdf_text = ""
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            pdf_text += text + "\n"

    if pdf_text.strip() == "":
        st.error("PDF se text nahi nikal paaya. Kya scanned PDF hai?")
        st.stop()

    st.success(f"✅ PDF load ho gaya! {len(pdf_reader.pages)} pages mile.")

    # Sawal poocho
    question = st.text_input("PDF se kya poochna hai?", placeholder="Jaise: Is PDF ka summary kya hai?")

    if st.button("Jawab Do", type="primary") and question:
        with st.spinner("Groq Llama3 soch raha hai..."):
            try:
                response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "Tum ek helpful assistant ho. Sirf diye gaye PDF context se jawab do. Agar jawab context mein nahi hai to bolo 'Ye jaankari PDF mein nahi hai'."
                        },
                        {
                            "role": "user",
                            "content": f"PDF Context:\n{pdf_text[:12000]}\n\nUser ka Sawal: {question}"
                        }
                    ],
                    model="llama3-8b-8192",
                    temperature=0.2
                )
                st.subheader("💡 Jawab:")
                st.write(response.choices[0].message.content)

            except Exception as e:
                st.error(f"Groq API Error: {e}")
else:
    st.info("👆 Upar PDF upload karo shuru karne ke liye")
