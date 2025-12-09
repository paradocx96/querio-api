import os
import fitz


def load_pdfs(folder_path: str) -> str:
    text = ""

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"PDF folder not found: {folder_path}")

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)

            try:
                with fitz.open(file_path) as doc:
                    for page in doc:
                        text += page.get_text()
                text += "\n"

            except Exception as e:
                raise RuntimeError(f"Error reading {filename}: {e}")

    return text
