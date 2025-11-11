import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from pptx import Presentation
from PIL import Image
import pytesseract
import io

# --- Explicitly set Tesseract path (adjust if needed) ---
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Page config
st.set_page_config(page_title="Docex: Study Assistant", layout="wide")
st.title("📚 Docex — Your Study Assistant")

# ---- Extraction Functions ----
def extract_text_from_pdf(file):
    text = ""
    file_bytes = file.read()
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for i, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            if page_text.strip():
                text += f"\n--- Page {i} ---\n{page_text}"
            else:
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_text = pytesseract.image_to_string(img)
                text += f"\n--- Page {i} (OCR) ---\n{ocr_text}"
    return text.strip()

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs]).strip()

def extract_text_from_pptx(file):
    prs = Presentation(file)
    text = ""
    for i, slide in enumerate(prs.slides, start=1):
        slide_text = []
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                slide_text.append(shape.text)
        if slide_text:
            text += f"\n--- Slide {i} ---\n" + "\n".join(slide_text)
    return text.strip()

def extract_text_from_txt(file):
    return file.read().decode("utf-8").strip()

def extract_text_from_image(file):
    img = Image.open(file)
    return pytesseract.image_to_string(img).strip()

# ---- Tabs ----
tab1, tab2 = st.tabs(["📂 Upload Materials", "❓ Ask Questions"])

# ----- Tab 1: Upload Materials -----
with tab1:
    st.header("Upload Your Study Materials")
    uploaded_files = st.file_uploader(
        "📤 Upload PDFs, DOCX, PPTX, TXT, or images:",
        type=["pdf", "docx", "pptx", "txt", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
        for file in uploaded_files:
            st.subheader(f"📂 {file.name}")
            try:
                if file.type == "application/pdf":
                    extracted_text = extract_text_from_pdf(file)
                elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    extracted_text = extract_text_from_docx(file)
                elif file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                    extracted_text = extract_text_from_pptx(file)
                elif file.type == "text/plain":
                    extracted_text = extract_text_from_txt(file)
                elif file.type.startswith("image/"):
                    extracted_text = extract_text_from_image(file)
                else:
                    st.warning(f"⚠️ Unsupported file type: {file.type}")
                    continue

                if extracted_text:
                    with st.expander("📝 View Extracted Text", expanded=False):
                        st.text_area("Extracted Text", extracted_text, height=400)
                else:
                    st.warning("⚠️ No text could be extracted from this file.")

            except Exception as e:
                st.error(f"❌ Error extracting text: {e}")

# ----- Tab 2: Ask Questions -----
with tab2:
    st.header("Ask Questions from Your Materials")
    question_input = st.text_area("Type your question here:")

    uploaded_question_file = st.file_uploader(
        "Or upload a question file (PDF, TXT, Image):",
        type=["pdf", "txt", "png", "jpg", "jpeg"]
    )

    if st.button("Get Answer"):
        st.info("🧠 Processing your question...")
        answer = "This is where your answer will appear once processing is implemented."
        st.success(answer)
