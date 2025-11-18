# import streamlit as st
# import concurrent.futures
# import time

# from settings import GROQ_API_KEY
# from rag_utils import (
#     save_temp,
#     extract_chunks,
#     build_vector_db,
#     build_rag_chain
# )

# st.set_page_config(page_title="Docex: AI Document Brain")
# st.title("📚 Docex — AI Document Brain Builder")


# uploaded_files = st.file_uploader(
#     "Upload documents (any type)",
#     type=None,
#     accept_multiple_files=True
# )


# # STEP 1: Extract
# if uploaded_files:
#     st.info("Extracting text from files...")

#     file_paths = [save_temp(f) for f in uploaded_files]
#     all_chunks = []

#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         results = executor.map(extract_chunks, file_paths)

#     # with st.expander("preview extracted chunks"):
#     #     st.write(results)

#     for r in results:
#         all_chunks.extend(r)

#     st.session_state["chunks"] = all_chunks
#     st.success(f"Extracted {len(all_chunks)} chunks.")
# else:
#     st.session_state["chunks"] = None



# # STEP 2: Build Vector DB
# if st.session_state["chunks"]:

#     if st.button("Create Brain"):
#         with st.spinner("Building vector database..."):
#             vectorstore = build_vector_db(st.session_state["chunks"])
#             st.session_state["retriever"] = vectorstore.as_retriever()

#         st.success("Brain built successfully! 🎉")



# # STEP 3: RAG Query
# if "retriever" in st.session_state:

#     query = st.text_area("Ask anything:", "Give me a summary")

#     if st.button("Run Query"):
#         rag = build_rag_chain(st.session_state["retriever"], GROQ_API_KEY)

#         with st.spinner("Thinking..."):
#             answer = rag.invoke({"input": query})

#         st.write("### 🧠 Answer")
#         st.write(answer["answer"])

#         with st.expander("Retrieved Context"):
#             for i, doc in enumerate(answer["context"], 1):
#                 st.write(f"Chunk {i}:")
#                 st.write(doc.page_content)
#                 st.write("---")


# # app.py (snippet)
# import streamlit as st
# from rag_utils import save_temp, process_files, build_vector_db, build_rag_chain, save_benchmark_logs
# from settings import GROQ_API_KEY
# import os

# st.set_page_config(page_title="Docex: Fast AI Document Brain")
# st.title("📚 Docex — Fast RAG Builder")

# uploaded_files = st.file_uploader("Upload documents", accept_multiple_files=True)
# if uploaded_files:
#     # save uploaded to temp files
#     file_paths = [save_temp(f) for f in uploaded_files]

#     # UI placeholders for per-file status
#     file_status_boxes = {os.path.basename(p): st.empty() for p in file_paths}
#     overall_progress = st.progress(0)
#     log_box = st.empty()

#     # Define callback for progress updates coming from rag_utils.process_files
#     def progress_cb(info):
#         # info may be per-file or overall
#         if info.get("file"):
#             fname = info["file"]
#             status = info["status"]
#             if status == "started":
#                 file_status_boxes[fname].info(f"⏳ {fname}: extracting...")
#             elif status == "done":
#                 file_status_boxes[fname].success(f"✅ {fname}: done — {info.get('chunks',0)} chunks in {round(info.get('elapsed',0),2)}s")
#             elif status == "failed":
#                 file_status_boxes[fname].error(f"❌ {fname}: failed: {info.get('error')}")
#         else:
#             # overall progress
#             if info.get("status") == "progress":
#                 overall_progress.progress(int(info.get("percent", 0)))
#                 log_box.text(f"Processed {info.get('completed')}/{info.get('total')} files")

#     # Run parallel extraction
#     st.info("Starting extraction (parallel)...")
#     chunks, logs = process_files(file_paths, max_workers=4, progress_callback=progress_cb)

#     st.success(f"Extraction complete — {logs['_summary']['total_chunks']} chunks from {logs['_summary']['files']} files.")
    

#     # Optionally save logs
#     save_path = save_benchmark_logs(logs, out_path="docex_benchmarks.json")
#     if save_path:
#         st.write(f"Saved benchmark logs to `{save_path}`")

#     # Build vector DB (show simple timing)
#     if st.button("Build Vector DB"):
#         vs, vb_logs = build_vector_db(chunks)
#         st.write("Vector DB built")
#         st.json(vb_logs)
#         st.session_state["retriever"] = vs.as_retriever()

# # RAG chat (same as before)
# if st.session_state.get("retriever"):
#     query = st.text_area("Ask anything:", "Give me a summary of uploaded docs")
#     if st.button("Run RAG Query"):
#         rag = build_rag_chain(st.session_state["retriever"], GROQ_API_KEY)
#         with st.spinner("Thinking..."):
#             answer = rag.invoke({"input": query})
#         st.write("### Answer")
#         st.write(answer["answer"])


# app.py
import streamlit as st
from rag_utils import save_temp, process_files, build_vector_db, build_rag_chain, save_benchmark_logs
from settings import GROQ_API_KEY
import os

st.set_page_config(page_title="Docex: Fast AI Document Brain")
st.title("📚 Docex — Fast RAG Builder")

# Initialize session state flags
if "chunks_created" not in st.session_state:
    st.session_state["chunks_created"] = False
if "chunks" not in st.session_state:
    st.session_state["chunks"] = []
if "logs" not in st.session_state:
    st.session_state["logs"] = {}
if "retriever" not in st.session_state:
    st.session_state["retriever"] = None

uploaded_files = st.file_uploader("Upload documents", accept_multiple_files=True)

if uploaded_files:
    # Save uploaded files to temp paths
    file_paths = [save_temp(f) for f in uploaded_files]

    # UI placeholders
    file_status_boxes = {os.path.basename(p): st.empty() for p in file_paths}
    overall_progress = st.progress(0)
    log_box = st.empty()

    def progress_cb(info):
        """Update per-file and overall progress in Streamlit."""
        if info.get("file"):
            fname = info["file"]
            status = info["status"]
            if status == "started":
                file_status_boxes[fname].info(f"⏳ {fname}: extracting...")
            elif status == "done":
                file_status_boxes[fname].success(
                    f"✅ {fname}: done — {info.get('chunks',0)} chunks in {round(info.get('elapsed',0),2)}s"
                )
            elif status == "failed":
                file_status_boxes[fname].error(f"❌ {fname}: failed: {info.get('error')}")
        else:
            # Overall progress
            if info.get("status") == "progress":
                overall_progress.progress(int(info.get("percent", 0)))
                log_box.text(f"Processed {info.get('completed')}/{info.get('total')} files")

    # Only run extraction if chunks are not already created in this session
    if not st.session_state["chunks_created"]:
        st.info("Starting extraction (parallel)...")
        chunks, logs = process_files(
            file_paths, max_workers=4, progress_callback=progress_cb
        )

        st.session_state["chunks"] = chunks
        st.session_state["logs"] = logs
        st.session_state["chunks_created"] = True

        # Display extraction summary
        st.success(
            f"Extraction complete — {logs['_summary']['total_chunks']} chunks from {logs['_summary']['files']} files."
        )

        # Save benchmark logs
        save_path = save_benchmark_logs(logs, out_path="docex_benchmarks.json")
        if save_path:
            st.write(f"Saved benchmark logs to `{save_path}`")
    else:
        st.info(
            f"✅ Extraction already done — {st.session_state['logs']['_summary']['total_chunks']} chunks from {st.session_state['logs']['_summary']['files']} files."
        )

    # Build vector DB
    if st.button("Build Vector DB"):
        vs, vb_logs = build_vector_db(st.session_state["chunks"])
        st.write("Vector DB built")
        st.json(vb_logs)
        st.session_state["retriever"] = vs.as_retriever()

# RAG Chat
if st.session_state.get("retriever"):
    query = st.text_area("Ask anything:", "Give me a summary of uploaded docs")
    if st.button("Run RAG Query"):
        rag = build_rag_chain(st.session_state["retriever"], GROQ_API_KEY)
        with st.spinner("Thinking..."):
            answer = rag.invoke({"input": query})
        st.write("### Answer")
        st.write(answer["answer"])
