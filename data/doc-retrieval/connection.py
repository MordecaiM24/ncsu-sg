import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeEmbeddings

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
vector_store = PineconeVectorStore(
    index=index,
    embedding=OllamaEmbeddings(model="nomic-embed-text"),
)


def get_vector_store():
    return vector_store
