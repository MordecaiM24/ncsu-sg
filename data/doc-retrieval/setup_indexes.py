import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

"""
This script creates two Pinecone indexes:
- sg-poc-summaries: For storing document summaries (initial search)
- sg-poc-chunks: For storing document chunks (detailed search)
"""

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY in .env")


pc = Pinecone(api_key=PINECONE_API_KEY)


DIMENSION = 1536


existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]


SUMMARY_INDEX_NAME = "sg-poc-summaries"
if SUMMARY_INDEX_NAME not in existing_indexes:
    print(f"Creating summary index: {SUMMARY_INDEX_NAME}")
    pc.create_index(
        name=SUMMARY_INDEX_NAME,
        dimension=DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    print(f"Created {SUMMARY_INDEX_NAME}")
else:
    print(f"Index {SUMMARY_INDEX_NAME} already exists")


CHUNK_INDEX_NAME = "sg-poc-chunks"
if CHUNK_INDEX_NAME not in existing_indexes:
    print(f"Creating chunk index: {CHUNK_INDEX_NAME}")
    pc.create_index(
        name=CHUNK_INDEX_NAME,
        dimension=DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    print(f"Created {CHUNK_INDEX_NAME}")
else:
    print(f"Index {CHUNK_INDEX_NAME} already exists")

print("Setup complete")
