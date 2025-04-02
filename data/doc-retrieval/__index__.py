from fastapi import FastAPI
from retrieval import retrieve, health
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
import os.path
import anthropic
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


app = FastAPI()

origins = ["https://sg.m16b.com/", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

anthropic_client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
)


@app.post("/claude-stream")
async def claude_stream(payload: dict):
    messages = payload.get("messages", [{"role": "user", "content": "hello"}])

    def generate():
        with anthropic_client.messages.stream(
            max_tokens=1024, messages=messages, model="claude-3-7-sonnet-20250219"
        ) as stream:
            for text in stream.text_stream:
                yield text  # streaming each chunk

    return StreamingResponse(generate(), media_type="text/plain")


class DocQuery(BaseModel):
    category: str | None = None
    query: str
    top_k: int | None = None  # only works in 3.10 or above


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health/{txt}")
async def health(txt):
    return {"text": txt}


@app.post("/doc-retrieval/")
async def create_item(body: DocQuery):
    query = body.query
    top_k = body.top_k if body.top_k is not None else 1
    results = retrieve(query, top_k)
    enriched_results = []
    for doc in results:
        doc_id = doc.id
        file_path = f"cleaned_json/{doc_id}.json"
        full_text = ""
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                doc_json = json.load(f)
                full_text = doc_json.get("full_text")
        enriched_results.append(
            {"id": doc.id, "metadata": doc.metadata, "full_text": full_text}
        )
    results = enriched_results

    return {"result": results}
