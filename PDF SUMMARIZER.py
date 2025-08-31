import streamlit as st
from PyPDF2 import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

# --------- Function to Extract Text from PDF ---------
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""  # Handle empty pages
    return full_text.strip()

# --------- Function to Generate PDF from Text ---------
def generate_pdf_from_text(text):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    lines = text.split("\n")
    y = 750

    for line in lines:
        if y < 40:
            c.showPage()
            y = 750
        c.drawString(50, y, line[:110])
        y -= 15

    c.save()
    buffer.seek(0)
    return buffer

# --------- Streamlit App Layout ---------
st.set_page_config(page_title="PDF Extract & Download", layout="centered")
st.title("📄 Smart Extract")

uploaded_file = st.file_uploader("📤 Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("📖 Extracting text from PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_file)

    if pdf_text:
        with st.expander("📃 View Extracted Text"):
            st.text_area("Extracted Text", pdf_text, height=300)

        # Generate new PDF
        generated_pdf = generate_pdf_from_text(pdf_text)

        # Download button
        st.download_button(
            label="💾 Download Generated PDF",
            data=generated_pdf,
            file_name="extracted_text.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("⚠️ Could not extract text from this PDF.")
