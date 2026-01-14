import tempfile
import os
from typing import Dict

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Global stores (thread-based like your code)
_THREAD_RETRIEVERS: Dict[str, any] = {}
_THREAD_METADATA: Dict[str, dict] = {}

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}   # ← forces CPU, avoids any meta → cuda/cpu move issues
)

def ingest_pdf(file_bytes: bytes, thread_id: str, filename: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(file_bytes)
        path = f.name

    try:
        docs = PyPDFLoader(path).load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_documents(docs)

        vs = FAISS.from_documents(chunks, embeddings)
        _THREAD_RETRIEVERS[thread_id] = vs.as_retriever(k=4)

        _THREAD_METADATA[thread_id] = {
            "filename": filename,
            "documents": len(docs),
            "chunks": len(chunks),
        }
    finally:
        os.remove(path)

def retrieve_context(query: str, thread_id: str):
    retriever = _THREAD_RETRIEVERS.get(thread_id)
    if not retriever:
        return []
    return [d.page_content for d in retriever.invoke(query)]

def thread_document_metadata(thread_id: str):
    return _THREAD_METADATA.get(thread_id, {})
