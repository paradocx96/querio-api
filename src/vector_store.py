import os

import chromadb
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"


def create_vectorstore(chunks, persist_dir):
    if not chunks:
        raise ValueError("No text chunks provided.")

    try:
        documents = [Document(page_content=chunk) for chunk in chunks]
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Create ChromaDB client with telemetry disabled
        client_settings = chromadb.config.Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
        client = chromadb.PersistentClient(
            path=persist_dir,
            settings=client_settings
        )

        vectordb = Chroma.from_documents(
            documents=documents,
            embedding=embedding_model,
            client=client,
            persist_directory=persist_dir
        )

        return vectordb

    except Exception as e:
        raise RuntimeError(f"Vector store creation failed: {e}")
