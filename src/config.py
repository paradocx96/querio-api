import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    GENAI_API_KEY = os.getenv("GENAI_API_KEY")
    # Get the project root directory (parent of src)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PDF_FOLDER = os.path.join(BASE_DIR, "data")
    CHROMA_DB = os.path.join(BASE_DIR, "chroma_db")


settings = Settings()
