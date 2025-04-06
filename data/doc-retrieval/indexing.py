import os
import json
import time
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from connection import get_summary_vector_store, get_chunk_vector_store
from collections import defaultdict
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
    summary_vector_store = get_summary_vector_store()
    chunk_vector_store = get_chunk_vector_store()

    bill_files = defaultdict(list)

    for file in os.listdir(INPUT_DIR):
        file_path = os.path.join(INPUT_DIR, file)
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        bill_id = str(content["id"])
        priority = get_file_priority(file)

        bill_files[bill_id].append((priority, file_path, content))

    summary_docs = []
    chunk_docs = []
    summary_ids = []
    chunk_ids = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    for i, (bill_id, file_list) in enumerate(bill_files.items()):
        if i >= 5:
            break

        file_list.sort(key=lambda x: x[0])
        _, file_path, content = file_list[0]

        metadata = {
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
        }

        summary_doc = Document(
            metadata=metadata,
            page_content=content["full_text"],
        )
        summary_docs.append(summary_doc)
        summary_ids.append(bill_id)

        chunks = text_splitter.split_text(content["full_text"])
        for i, chunk_text in enumerate(chunks):

            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_id"] = i
            chunk_metadata["total_chunks"] = len(chunks)
            chunk_metadata["doc_id"] = bill_id

            chunk_doc = Document(
                metadata=chunk_metadata,
                page_content=chunk_text,
            )
            chunk_docs.append(chunk_doc)
            chunk_ids.append(f"{bill_id}_chunk_{i}")

    legislative_names = [
        "_".join(doc.metadata["id"].split("_")[0:2]).upper() for doc in summary_docs
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
            "leg_name": lambda x: legislative_names[summary_docs.index(x)],
            "full_leg_name": lambda x: full_legislative_names[summary_docs.index(x)],
        }
        | ChatPromptTemplate.from_template(
            'Summarize the following document ({leg_name}):\n\n{doc}. Start with "This document, {leg_name}, or {full_leg_name}), ...".'
        )
        | ChatOpenAI(model="gpt-4o-mini", max_retries=0)
        | StrOutputParser()
    )

    summaries = chain.batch(summary_docs, batch_size=5)
    print("\n\n\nSUMMARIES:\n")
    print(summaries)

    for i in range(len(summary_docs)):
        summary_docs[i] = Document(
            page_content=summaries[i], metadata=summary_docs[i].metadata
        )

    print(f"Indexing {len(summary_docs)} document summaries...")
    for i in range(0, len(summary_docs), 10):
        batch_docs = summary_docs[i : i + 10]
        batch_ids = summary_ids[i : i + 10]
        summary_vector_store.add_documents(documents=batch_docs, ids=batch_ids)
        if i + 10 < len(summary_docs):
            print(
                f"Indexed {i+10}/{len(summary_docs)} summaries, sleeping to respect rate limits..."
            )
            time.sleep(1)

    print(f"Indexing {len(chunk_docs)} document chunks...")
    for i in range(0, len(chunk_docs), 10):
        batch_docs = chunk_docs[i : i + 10]
        batch_ids = chunk_ids[i : i + 10]
        chunk_vector_store.add_documents(documents=batch_docs, ids=batch_ids)
        if i + 10 < len(chunk_docs):
            print(
                f"Indexed {i+10}/{len(chunk_docs)} chunks, sleeping to respect rate limits..."
            )
            time.sleep(1)

    print(
        f"Successfully indexed {len(summary_docs)} documents with {len(chunk_docs)} total chunks"
    )


if __name__ == "__main__":
    index_documents()
