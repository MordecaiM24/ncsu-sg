import uuid

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

import os
import json

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

INPUT_DIR = "./cleaned_json"

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
