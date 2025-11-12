# text_processing.py
"""
Handles text cleaning, normalization, and chunking for Docex Study Assistant.
- Text Cleaning & Normalization (manual)
- Chunking / Context Splitting (LangChain)
"""

import re
from langchain.text_splitter import TokenTextSplitter


# -----------------------------
# 3️⃣ TEXT CLEANING & NORMALIZATION
# -----------------------------

RE_PAGE = re.compile(r"--- Page \d+ ---|Page \d+ of \d+", re.IGNORECASE)
RE_CHAPTER = re.compile(r"CHAPTER\s+\d+\s*[-:]*\s*", re.IGNORECASE)
RE_MISC = re.compile(r"(Document ID:.*|Confidential.*)")
RE_PUNCT = re.compile(r"([.!?]){2,}")
RE_SPACE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = RE_PAGE.sub("", text)
    text = RE_CHAPTER.sub("", text)
    text = RE_MISC.sub("", text)
    text = RE_PUNCT.sub(r"\1", text)
    text = RE_SPACE.sub(" ", text)
    return text.strip()


# -----------------------------
# CHUNKING (CONTEXT SPLITTING)
# -----------------------------

splitter = TokenTextSplitter(
    model_name="gpt-3.5-turbo",  # your embedding model later
    chunk_size=600,
    chunk_overlap=50
)

def chunk_text(cleaned_text: str, chunk_size: int = 600, chunk_overlap: int = 50):
    """
    Split cleaned text into overlapping token-based chunks.
    Ensures consistent chunking and true semantic overlap.
    """
    if not cleaned_text.strip():
        return []

    raw_chunks = splitter.split_text(cleaned_text)

     # Assign unique IDs to each chunk
    chunks = [{"id": f"chunk_{i+1}", "text": text} for i, text in enumerate(raw_chunks)]

    # Debug info (optional)
    print(f"Total chunks: {len(chunks)}")
    for ch in chunks[:5]:
        print(f"{ch['id']} — {len(ch['text'].split())} words, preview: {ch['text'][:100]!r}")

    return chunks