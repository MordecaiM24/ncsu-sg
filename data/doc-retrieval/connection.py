import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
SUMMARY_INDEX_NAME = "sg-poc-summaries"
CHUNK_INDEX_NAME = "sg-poc-chunks"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate OpenAI API key
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in .env")

# Validate API key
if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY in .env")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Get all existing indexes
existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

# Validate that our indexes exist
if SUMMARY_INDEX_NAME not in existing_indexes:
    raise ValueError(f"Index '{SUMMARY_INDEX_NAME}' does not exist")
if CHUNK_INDEX_NAME not in existing_indexes:
    raise ValueError(f"Index '{CHUNK_INDEX_NAME}' does not exist")


def get_embedding() -> Embeddings:
    """Get the OpenAI embedding model."""
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        dimensions=1536,  # Default dimension for text-embedding-3-small
        api_key=OPENAI_API_KEY,
    )


# Create vector stores for both summary and chunks
summary_index = pc.Index(SUMMARY_INDEX_NAME)
chunk_index = pc.Index(CHUNK_INDEX_NAME)

# Use the same embedding model for both to ensure consistency
embedding_model = get_embedding()

summary_vector_store = PineconeVectorStore(
    index=summary_index, embedding=embedding_model
)
chunk_vector_store = PineconeVectorStore(index=chunk_index, embedding=embedding_model)


def get_summary_vector_store():
    """Get the vector store for document summaries."""
    return summary_vector_store


def get_chunk_vector_store():
    """Get the vector store for document chunks."""
    return chunk_vector_store
