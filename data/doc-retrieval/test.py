import os
import json
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from connection import get_vector_store

INPUT_DIR = "./cleaned_json"


def index_documents():
    vector_store = get_vector_store()

    docs = []
    for file in os.listdir(INPUT_DIR):
        file_path = os.path.join(INPUT_DIR, file)
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)
        doc = Document(
            metadata={
                "id": content["id"],
                "version": content["version"],
                "long_title": content["long_title"],
                "short_title": content["short_title"],
                "sponsors": content["sponsors"],
                "secondary_sponsors": content["secondary_sponsors"],
                "first_reading": content["first_reading"],
                "second_reading": content["second_reading"],
                "result": content["result"],
                "session": content["session"],
            },
            page_content=content["full_text"],
        )
        docs.append(doc)

    # process only first 10 docs for testing
    docs = docs[:10]

    chain = (
        {"doc": lambda x: x.page_content}
        | ChatPromptTemplate.from_template("Summarize the following document:\n\n{doc}")
        | ChatOpenAI(model="gpt-4o-mini", max_retries=0)
        | StrOutputParser()
    )

    ids = [doc.metadata["id"] for doc in docs]
    summaries = chain.batch(docs, batch_size=5)

    vector_store.add_documents(documents=docs, ids=ids)

    print(summaries)
