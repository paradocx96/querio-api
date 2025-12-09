import google.generativeai as genai


def configure_llm(api_key: str):
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        raise RuntimeError(f"Failed to configure Google LLM: {e}")


def answer_query(db, query: str, model="gemini-2.5-flash"):
    try:
        docs = db.similarity_search(query, k=3)
        context = "\n".join([doc.page_content for doc in docs])

        prompt = f"Answer based on the context below:\n\n{context}\n\nQuery: {query}"

        llm = genai.GenerativeModel(model)
        response = llm.generate_content(prompt)

        return response.text

    except Exception as e:
        raise RuntimeError(f"LLM query failed: {e}")
