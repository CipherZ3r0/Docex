# embeddings_manager.py
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langsmith.integrations.otel import configure
from text_processing import clean_text, chunk_text
from dotenv import load_dotenv
load_dotenv()
configure(project_name="doces-embeddings")

# 🔐 ENVIRONMENT SETUP

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

if not LANGSMITH_API_KEY:
    raise ValueError("LANGSMITH_API_KEY not found in environment variables.")

os.environ["LANGSMITH_TRACING_v2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Docex Study Assistant"  # optional but helps in LangSmith dashboard


# ⚙️ Initialize Embedding Model

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")


# 🔧 Create Embeddings Function

def create_embeddings_from_text(text: str):
   
    # Clean, chunk, and embed text. LangSmith will automatically trace all runs.
    
    if not text.strip():
        print(" No text provided.")
        return []

    cleaned = clean_text(text)
    chunks = chunk_text(cleaned)

    embedded_chunks = []
     # Create embeddings for each chunk
    for chunk in chunks:
        print(f"Embedding chunk ID: {chunk['id']}")
        try:
            print("trying to create embedding chunk_embedding.py")
            vector = embeddings.embed_query(chunk["text"])
            embedded_chunks.append({
                "id": chunk["id"],
                "text": chunk["text"],
                "embedding": vector
            })
            print(f"embedded length: {len(vector)} chunk_embedding.py")
        except Exception as e:
            print(f"Error embedding {chunk['id']}: {e}")
    print(f"Created {len(embedded_chunks)} embeddings.")
    print(f"embedded_chunks sample: {embedded_chunks[:1]}")
    return embedded_chunks


# Test Run
if __name__ == "__main__":
    text = "Machine learning models help generate embeddings for text similarity search."
    results = create_embeddings_from_text(text)
    print(f" Example embedding length: {len(results[0]['embedding'])}")
    print(results[0])
