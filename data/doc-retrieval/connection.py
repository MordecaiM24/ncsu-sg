import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeEmbeddings
from langchain_core.embeddings import Embeddings

EMBEDDING_MODE = os.getenv("EMBEDDING_MODE", "remote")


def get_embedding() -> Embeddings:
    if EMBEDDING_MODE == "local":
        return OllamaEmbeddings(model="nomic-embed-text")
    elif EMBEDDING_MODE == "none":

        class DummyEmbeddings(Embeddings):
            def embed_query(self, text: str) -> list[float]:
                raise RuntimeError("embedding shouldn't be called in 'none' mode")

            def embed_documents(self, texts: list[str]) -> list[list[float]]:
                raise RuntimeError("embedding shouldn't be called in 'none' mode")

        return DummyEmbeddings()
    else:
        raise ValueError(f"unknown EMBEDDING_MODE: {EMBEDDING_MODE}")


load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "sg-poc"

if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY in .env")

# init pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# check if index exists
existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

if INDEX_NAME not in existing_indexes:
    raise ValueError(f"Index '{INDEX_NAME}' does not exist")


# set up vector store
index = pc.Index(INDEX_NAME)
vector_store = PineconeVectorStore(index=index, embedding=get_embedding())


def get_vector_store():
    return vector_store
