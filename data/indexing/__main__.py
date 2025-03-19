from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.storage import InMemoryByteStore
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.retrievers.multi_vector import MultiVectorRetriever
import chromadb


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

docs = docs[0:10]


chain = (
    {"doc": lambda x: x.page_content}
    | ChatPromptTemplate.from_template("Summarize the following documetn:\n\n{doc}")
    | ChatOpenAI(model="gpt-4o-mini", max_retries=0)
    | StrOutputParser()
)


summaries = chain.batch(docs, batch_size=5)

print(summaries)

# for me not going bankrupt purposes:
# summaries = [
#     "The document is a resolution from the North Carolina State University Student Senate confirming the appointment of Sharon Chen as an Allocation Official for the 104th Session of Student Government, as proposed by Student Body Treasurer Lanadia Adams.",
#     "The document outlines a request from the Sustainable Funding Entrepreneurship Club for $1,200 to cover costs related to a 3-D printing Makerspace rental, general supplies, and pavilion venue rental, with expenses expected before January 10, 2025. It verifies the organization's Registered Student Organization (RSO) status, eligibility, and compliance with budget submissions. The club presented its grant request at a Finance Committee meeting on October 9, 2024. Key enactments include:\n\n1. **Submission Deadline**: Receipts and unspent funds must be submitted by January 10, 2025, at 11:59 PM ET to remain eligible for future funding.\n2. **Spending Period**: Funds can be used from allocation receipt until the submission deadline.\n3. **Line Item Compliance**: Organizations must adhere to specified line item descriptions for future funding eligibility.\n4. **Amendments and Exemptions**: The Student Body Treasurer has the authority to allow changes to line item descriptions, amend grant request details, and grant spending period exemptions.\n5. **Compliance**: All allocations must adhere to NC State Student Government and State spending guidelines at the time of expenditure.",
#     "The document announces that Student Body Treasurer Lanadia Adams has appointed Jean-Luc Theard as a Treasury Official. The North Carolina State University Student Senate confirms this appointment for the 104th Session of Student Government.",
#     "The document outlines concerns regarding the current fast-tracking process for legislation within the Student Senate as specified in Chapter 2, Article 1 of the Student Body Statutes. It highlights that fast-tracking allows legislation to bypass the formal first reading and committee hearing, proceeding directly to a second reading without prior discussion or debate. This process can lead to legislation failing without further opportunity for discussion if it doesn't gain enough affirmative votes. The authors express a desire for a more fair and thorough review of all legislative initiatives during the current and future sessions of the Student Senate.",
#     "The document is a resolution by the North Carolina State University Student Government recognizing February 15 - 22, 2025, as National FFA Week. It highlights the historical significance of vocational education, the FFA Creed, the adoption of the FFA blue jacket, and the merger with the New Farmers of America in 1965, which increased African American participation in the organization. The resolution outlines specific themes for each day of the week, focusing on hands-on agricultural experiences, service, alumni, advisor appreciation, fundraising, and wearing blue. Additionally, it expresses support for agricultural education in North Carolina and states that the resolution will be forwarded to relevant officials and departments.",
# ]

persistent_client = chromadb.PersistentClient(path="./chroma_db")

collection = persistent_client.get_or_create_collection("summaries")


vectorstore = Chroma(
    client=persistent_client,
    collection_name="summaries",
    embedding_function=OllamaEmbeddings(model="nomic-embed-text"),
)

store = InMemoryByteStore()
id_key = "doc_id"

retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    byte_store=store,
    id_key=id_key,
)

doc_ids = [doc.metadata["id"] for doc in docs]

summary_docs = [
    Document(page_content=s, metadata={"id": doc_ids[i]})
    for i, s in enumerate(summaries)
]


retriever.vectorstore.add_documents(summary_docs)
retriever.docstore.mset(list(zip(doc_ids, docs)))


query = "Allocation official"
# search for the summary
sub_docs = vectorstore.similarity_search(query, k=1)

# extract the id from the retrieved summary
retrieved_id = sub_docs[0].metadata["id"]
