from fastapi import FastAPI
from retrieval import retrieve, retrieve_with_reranking, get_document_metadata
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
import os.path
import anthropic
import time
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

anthropic_client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
)


class DocQuery(BaseModel):
    query: str
    doc_id: Optional[str] = None
    top_k: Optional[int] = 3


class ChatRequest(BaseModel):
    messages: List[dict]
    doc_ids: Optional[List[str]] = None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health/{txt}")
async def health(txt):
    return {"text": txt}


@app.post("/doc-retrieval/")
async def doc_retrieval(body: DocQuery):
    """
    Endpoint for retrieving documents based on a query.
    For initial search (without doc_id): Returns document summaries with metadata.
    For follow-up questions (with doc_id): Returns relevant chunks from the specified document.
    """
    query = body.query
    doc_id = body.doc_id
    top_k = body.top_k if body.top_k is not None else 3

    if doc_id:
        results = retrieve_with_reranking(query, doc_id, top_k)

        formatted_results = []
        for doc in results:
            formatted_results.append(
                {
                    "chunk_id": doc.metadata.get("chunk_id"),
                    "doc_id": doc.metadata.get("doc_id"),
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                }
            )

        doc_metadata = get_document_metadata(doc_id)

        return {
            "type": "chunks",
            "doc_metadata": doc_metadata,
            "chunks": formatted_results,
        }
    else:

        results = retrieve(query, top_k)

        formatted_results = []
        for doc in results:
            doc_id = doc.metadata.get("id")
            formatted_results.append(
                {
                    "id": doc_id,
                    "summary": doc.page_content,
                    "metadata": doc.metadata,
                    "excerpt": doc.metadata.get("excerpt", ""),
                }
            )

        return {"type": "summaries", "results": formatted_results}


@app.post("/claude-stream")
async def claude_stream(payload: ChatRequest):
    """
    Streaming endpoint for Claude responses.
    - For initial queries: Uses document summaries for context
    - For follow-up queries with doc_ids: Uses specific document chunks for context
    """
    messages = payload.messages
    doc_ids = payload.doc_ids or []

    def generate():
        try:
            # Check if this is a question about specific documents
            if doc_ids:
                doc_count = len(doc_ids)
                yield f"Getting detailed information about {doc_count} document{'s' if doc_count > 1 else ''}...\n\n"

                # Extract the latest user query
                latest_query = ""
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        latest_query = msg.get("content", "")
                        break

                # Create context from all selected documents
                content = []

                # Process each document
                for doc_id in doc_ids:
                    # Get relevant chunks for this question and document
                    chunks = retrieve_with_reranking(latest_query, doc_id, k=2)

                    if not chunks:
                        continue

                    # Get document metadata
                    doc_metadata = get_document_metadata(doc_id)

                    # Add document metadata as context
                    content.append(
                        {
                            "type": "document",
                            "source": {
                                "type": "text",
                                "media_type": "text/plain",
                                "data": f"Document ID: {doc_id}\nTitle: {doc_metadata.get('long_title')}\nShort Title: {doc_metadata.get('short_title')}\nResult: {doc_metadata.get('result')}",
                            },
                            "title": f"Document {doc_id} Metadata",
                            "citations": {"enabled": True},
                        }
                    )

                    # Add chunks from this document
                    for chunk in chunks:
                        content.append(
                            {
                                "type": "document",
                                "source": {
                                    "type": "text",
                                    "media_type": "text/plain",
                                    "data": chunk.page_content,
                                },
                                "title": f"Document {doc_id} (Chunk {chunk.metadata.get('chunk_id')})",
                                "citations": {"enabled": True},
                            }
                        )

                if not content:
                    yield "I couldn't find relevant information in these documents. Please try a different question."
                    return

                # Add the user query
                content.append({"type": "text", "text": latest_query})

                # Create augmented messages
                augmented_messages = [{"role": "user", "content": content}]
                augmented_messages.extend(messages[1:])

                # Stream response from Claude
                with anthropic_client.messages.stream(
                    max_tokens=1024,
                    messages=augmented_messages,
                    model="claude-3-5-haiku-20241022",
                ) as stream:
                    for text in stream.text_stream:
                        yield text

            else:
                # This is an initial query - use general document search
                yield "Searching for relevant legislation...\n\n"

                # Extract the query from the messages
                query = ""
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        query = msg.get("content", "")
                        break

                # Get relevant document summaries
                results = retrieve(query, k=3)

                if not results:
                    yield "I couldn't find any relevant legislation. Please try a different question."
                    return

                # Create context from document summaries
                content = []
                for doc in results:
                    doc_id = doc.metadata.get("id")
                    content.append(
                        {
                            "type": "document",
                            "source": {
                                "type": "text",
                                "media_type": "text/plain",
                                "data": doc.page_content,
                            },
                            "title": f"Document {doc_id} Summary",
                            "citations": {"enabled": True},
                        }
                    )

                    # Add excerpt from the full text
                    excerpt = doc.metadata.get("excerpt", "")
                    if excerpt:
                        content.append(
                            {
                                "type": "document",
                                "source": {
                                    "type": "text",
                                    "media_type": "text/plain",
                                    "data": excerpt,
                                },
                                "title": f"Document {doc_id} Excerpt",
                                "citations": {"enabled": True},
                            }
                        )

                # Add the user query
                content.append({"type": "text", "text": query})

                # Create augmented messages
                augmented_messages = [{"role": "user", "content": content}]
                augmented_messages.extend(messages[1:])

                # Stream response from Claude
                with anthropic_client.messages.stream(
                    max_tokens=1024,
                    messages=augmented_messages,
                    model="claude-3-5-haiku-20241022",
                ) as stream:
                    for text in stream.text_stream:
                        yield text

        except Exception as e:
            yield f"\n\nError during streaming: {str(e)}"

    return StreamingResponse(generate(), media_type="text/event-stream")
