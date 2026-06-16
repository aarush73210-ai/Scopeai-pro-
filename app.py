import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io

st.set_page_config(page_title="ScopeAI", page_icon="📚", layout="centered")
st.title("📚 ScopeAI - PDF Q&A Bot")
st.caption("Text + Scanned PDF dono chalenge. Upload karo aur poocho")

# Secret check
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception as e:
    st.error(f"❌ Secret Error: {e}")
    st.stop()

uploaded_file = st.file_uploader("PDF File Upload Karo", type="pdf")

if uploaded_file is not None:
    pdf_text = ""

    # Pehle normal text try karo
    try:
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text + "\n"
    except:
        pass

    # Agar text nahi mila to OCR chalaao
    if pdf_text.strip() == "":
        st.info("🔍 Scanned PDF detect hua. OCR se text nikal raha hu... Wait karo")
        try:
            uploaded_file.seek(0) # File pointer reset karo
            images = convert_from_bytes(uploaded_file.read())
            for i, image in enumerate(images):
                with st.spinner(f"Page {i+1}/{len(images)} padh raha hu..."):
                    text = pytesseract.image_to_string(image, lang='eng+hin')
                    pdf_text += text + "\n"
            st.success("✅ OCR complete! Text nikal gaya.")
        except Exception as e:
            st.error(f"OCR Error: {e}")
            st.stop()

    if pdf_text.strip() == "":
        st.error("PDF se text nahi nikal paaya.")
        st.stop()

    st.success(f"✅ PDF ready! Total {len(pdf_text)} characters mile.")

    question = st.text_input("PDF se kya poochna hai?", placeholder="Jaise: Syllabus mein kitne subject hain?")

    if st.button("Jawab Do", type="primary") and question:
        with st.spinner("Groq Llama3 soch raha hai..."):
            try:
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Sirf diye gaye PDF context se jawab do. Hindi mein jawab do."},
                        {"role": "user", "content": f"PDF Context:\n{pdf_text[:12000]}\n\nSawal: {question}"}
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
