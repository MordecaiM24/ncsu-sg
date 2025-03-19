from fastapi import FastAPI
from retrieval import health

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health/{txt}")
async def retrieve(txt):
    return health(txt)
