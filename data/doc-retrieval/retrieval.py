from connection import get_vector_store


def retrieve(query: str, k: int = 1):
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query=query, k=k)
    return results


def health(str):
    return {"health": f"{str}"}
