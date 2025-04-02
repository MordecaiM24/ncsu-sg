import os
import json
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from connection import get_vector_store
from collections import defaultdict

INPUT_DIR = "./cleaned_json"


def get_file_priority(filename):
    if any(tag in filename for tag in ["vetoed", "failed", "engrossed", "officiated"]):
        return 1
    elif "second_reading" in filename:
        return 2
    elif "first_reading" in filename:
        return 3
    else:
        return 4


def index_documents():
    vector_store = get_vector_store()

    bill_files = defaultdict(list)

    for file in os.listdir(INPUT_DIR):
        file_path = os.path.join(INPUT_DIR, file)
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        bill_id = str(content["id"])
        priority = get_file_priority(file)

        bill_files[bill_id].append((priority, file_path, content))

    docs = []
    ids = []

    for bill_id, file_list in bill_files.items():

        file_list.sort(key=lambda x: x[0])

        _, file_path, content = file_list[0]

        doc = Document(
            metadata={
                "id": str(content["id"]),
                "version": str(content["version"]),
                "long_title": str(content["long_title"]),
                "short_title": str(content["short_title"]),
                "sponsors": str(content["sponsors"]),
                "secondary_sponsors": str(content["secondary_sponsors"]),
                "first_reading": str(content["first_reading"]),
                "second_reading": str(content["second_reading"]),
                "result": str(content["result"]),
                "session": str(content["session"]),
            },
            page_content=content["full_text"],
        )
        docs.append(doc)
        ids.append(bill_id)

    legislative_names = [
        "_".join(doc.metadata["id"].split("_")[0:2]).upper() for doc in docs
    ]

    bill_type_map = {
        "SB": "Senate Bill",
        "R": "Resolution",
        "FB": "Finance Bill",
        "GB": "Government Bill",
        "AB": "Appropriations Bill",
        "BB": "Budget Bill",
        "SR-A": "Senate Resolution",
    }

    full_legislative_names = []
    for name in legislative_names:
        prefix, number = name.split("_")
        full_name = f"{bill_type_map.get(prefix, prefix)} {number}"
        full_legislative_names.append(full_name)

    chain = (
        {
            "doc": lambda x: x.page_content,
            "leg_name": lambda x: legislative_names[docs.index(x)],
            "full_leg_name": lambda x: full_legislative_names[docs.index(x)],
        }
        | ChatPromptTemplate.from_template(
            'Summarize the following document ({leg_name}):\n\n{doc}. Start with "This document, {leg_name}, or {full_leg_name}), ...".'
        )
        | ChatOpenAI(model="gpt-4o-mini", max_retries=0)
        | StrOutputParser()
    )

    summaries = chain.batch(docs, batch_size=5)
    print("\n\n\nSUMMARIES:\n")
    print(summaries)

    for i in range(len(docs)):
        docs[i] = Document(page_content=summaries[i], metadata=docs[i].metadata)

    vector_store.add_documents(documents=docs, ids=ids)


index_documents()
