# import os
# import tempfile
# import streamlit as st
# from dotenv import load_dotenv

# load_dotenv()

# from langchain_community.document_loaders import UnstructuredFileLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import FAISS
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_groq import ChatGroq

# from langchain_classic.chains.combine_documents import create_stuff_documents_chain
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_classic.chains.retrieval import create_retrieval_chain


# st.set_page_config(page_title="Docex: Document Explorer & Summarizer")
# st.title("📄 Docex — Document Explorer & Summarizer")
# st.write("Upload a file and generate an accurate summary using Groq LLM + RAG.")


# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# uploaded_file = st.file_uploader("Upload Document", type=["pdf", "docx", "txt"])


# def save_temp(uploaded):
#     ext = os.path.splitext(uploaded.name)[1]
#     tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
#     tmp.write(uploaded.getbuffer())
#     return tmp.name


# def load_and_split(file_path, chunk_size=1200, chunk_overlap=200):
#     loader = UnstructuredFileLoader(file_path)
#     docs = loader.load()

#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#     )
#     return text_splitter.split_documents(docs)


# def create_vectorstore(chunks):
#     embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
#     return FAISS.from_documents(chunks, embeddings)


# if uploaded_file:
#     st.info("Processing document...")

#     filepath = save_temp(uploaded_file)

#     try:
#         chunks = load_and_split(filepath)
#         st.success(f"Document split into {len(chunks)} chunks!")

#         vectorstore = create_vectorstore(chunks)
#         retriever = vectorstore.as_retriever()

#         prompt = ChatPromptTemplate.from_template("""
# You are an expert summarizer.

# Use ONLY the provided context to answer.

# Context:
# {context}

# Instruction:
# {input}

# Response:
# """)

#         llm = ChatGroq(
#             api_key=GROQ_API_KEY,
#             model="llama-3.1-8b-instant",
#             temperature=0.1
#         )

#         combine_chain = create_stuff_documents_chain(
#             llm=llm,
#             prompt=prompt
#         )

#         rag_chain = create_retrieval_chain(
#             retriever=retriever,
#             combine_docs_chain=combine_chain
#         )

#         st.subheader("Ask anything or generate summary:")
#         query = st.text_area(
#             "Enter your question (or leave empty to generate a full summary)",
#             "Provide a complete summary of this document."
#         )

#         if st.button("Generate Summary"):
#             with st.spinner("Generating summary using RAG..."):
#                 response = rag_chain.invoke({"input": query})

#             st.success("Summary generated!")
#             st.markdown("### 📌 Summary")
#             st.write(response["answer"])

#             with st.expander("Show retrieved context"):
#                 for i, doc in enumerate(response["context"], 1):
#                     st.markdown(f"*Chunk {i}:*")
#                     st.write(doc.page_content)
#                     st.markdown("---")

#     except Exception as e:
#         st.error(f"Error processing document: {str(e)}")
#         st.info("Make sure you have installed: unstructured, unstructured[pdf], unstructured[docx]")

# else:
#     st.info("⬆ Upload a file to begin.")

# st.caption("Docex — Powered by Groq, LangChain, Google Embeddings")


import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Loaders & vector tools
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# LLM
from langchain_groq import ChatGroq

# Chains
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.retrieval import create_retrieval_chain


# ---------------------------
# UI SETUP
# ---------------------------
st.set_page_config(page_title="Docex: Multi-File Document Explorer")
st.title("📚 Docex — Multi-File Document Explorer & Summarizer")
st.write("Upload **multiple documents** and summarize or chat with them using RAG.")


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# ---------------------------
# FILE UPLOAD
# ---------------------------
uploaded_files = st.file_uploader(
    "Upload one or more documents",
    type=[
        "pdf", "docx", "txt", "pptx",
        "png", "jpg", "jpeg",
        "csv", "md", "html", "epub", "json"
    ],
    accept_multiple_files=True
)


def save_temp(uploaded):
    """Save uploaded file to a temp file & return its path"""
    ext = os.path.splitext(uploaded.name)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    tmp.write(uploaded.getbuffer())
    return tmp.name


def load_and_split(file_path, chunk_size=1200, chunk_overlap=200):
    """Load ANY document type using Unstructured"""
    loader = UnstructuredFileLoader(file_path)  # handles ALL types automatically
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return text_splitter.split_documents(docs)


def create_vectorstore(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return FAISS.from_documents(chunks, embeddings)


# ---------------------------
# PROCESS MULTIPLE FILES
# ---------------------------
if uploaded_files:
    st.info("Processing documents...")

    all_chunks = []
    for uploaded in uploaded_files:
        st.write(f"📄 Processing: **{uploaded.name}**")

        try:
            path = save_temp(uploaded)
            chunks = load_and_split(path)

            st.success(f"✔ {uploaded.name} → {len(chunks)} chunks")
            all_chunks.extend(chunks)

        except Exception as e:
            st.error(f"Error loading {uploaded.name}: {e}")

    st.success(f"🎉 Total Chunks from all files: {len(all_chunks)}")

    # Create vectorstore for all files
    vectorstore = create_vectorstore(all_chunks)
    retriever = vectorstore.as_retriever()

    # Prompt template
    prompt = ChatPromptTemplate.from_template("""
You are an expert academic summarizer and question-answering assistant.

You MUST follow these rules:
1. Only use the information strictly provided in the context.
2. If the answer cannot be found in the context, say: 
   “The context does not contain this information.”
3. Do NOT add external knowledge.
4. Keep your answers clear, precise, and technically accurate.
5. When summarizing: focus on key ideas, definitions, and core explanations.
6. When answering questions: cite the exact parts of the context you rely on.

-----------------------
Context:
{context}
-----------------------

Instruction:
{input}

Your Response:
""")

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.1-8b-instant",
        temperature=0.1
    )

    combine_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
    rag_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=combine_chain)

    st.subheader("Ask anything about the uploaded documents:")
    query = st.text_area(
        "Enter your question",
        "Give me a combined summary of all documents."
    )

    if st.button("Generate Response"):
        with st.spinner("Thinking..."):
            response = rag_chain.invoke({"input": query})

        st.success("Done!")
        st.markdown("### 🧾 Response")
        st.write(response["answer"])

        with st.expander("📌 Retrieved context"):
            for i, doc in enumerate(response["context"], 1):
                st.markdown(f"**Chunk {i}:**")
                st.write(doc.page_content)
                st.markdown("---")

else:
    st.info("⬆ Upload at least one file to begin.")


st.caption("Docex — Powered by Groq, LangChain, Google Embeddings")
