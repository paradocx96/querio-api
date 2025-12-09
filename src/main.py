import os
import sys
import warnings
from contextlib import contextmanager
from io import StringIO

# Disable ChromaDB telemetry before any imports
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Filter out Python version warnings from Google AI
warnings.filterwarnings("ignore", category=FutureWarning, module="google.api_core")

from config import settings
from pdf_handler import load_pdfs
from rag_pipeline import configure_llm, answer_query
from text_splitter import split_text
from vector_store import create_vectorstore


@contextmanager
def suppress_stderr():
    """Temporarily suppress stderr to hide ChromaDB telemetry errors"""
    original_stderr = sys.stderr
    sys.stderr = StringIO()
    try:
        yield
    finally:
        sys.stderr = original_stderr


def main():
    try:
        configure_llm(settings.GENAI_API_KEY)

        print("Loading PDFs...")
        text = load_pdfs(settings.PDF_FOLDER)

        print("Splitting text...")
        chunks = split_text(text)

        print("Creating vector database...")
        with suppress_stderr():
            vectordb = create_vectorstore(chunks, settings.CHROMA_DB)

        print("System ready!")
        while True:
            query = input("\nAsk a question (or type 'exit'): ")

            if query.lower() == "exit":
                break

            with suppress_stderr():
                answer = answer_query(vectordb, query)
            print("\nAI Response:", answer)

    except Exception as e:
        print("\nFATAL ERROR:", e)


if __name__ == "__main__":
    main()
