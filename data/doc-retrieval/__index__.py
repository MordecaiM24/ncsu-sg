from fastapi import FastAPI
from retrieval import retrieve, health
from pydantic import BaseModel


class DocQuery(BaseModel):
    category: str | None = None
    query: str
    top_k: int | None = None  # only works in 3.10 or above


app = FastAPI()


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
    return {"result": results}
