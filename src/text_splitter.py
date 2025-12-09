from langchain_text_splitters import CharacterTextSplitter


def split_text(text: str, chunk_size=1000, chunk_overlap=100):
    try:
        splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return splitter.split_text(text)
    except Exception as e:
        raise RuntimeError(f"Text splitting failed: {e}")
