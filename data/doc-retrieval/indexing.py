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

    # process only first 10 docs for testing
    docs = docs[:10]

    chain = (
        {"doc": lambda x: x.page_content}
        | ChatPromptTemplate.from_template("Summarize the following document:\n\n{doc}")
        | ChatOpenAI(model="gpt-4o-mini", max_retries=0)
        | StrOutputParser()
    )

    ids = [doc.metadata["id"] for doc in docs]
    # summaries = chain.batch(docs, batch_size=5)
    summaries = [
        "The document is a resolution from the North Carolina State University Student Senate confirming the appointment of Sharon Chen as an Allocation Official for the 104th Session of Student Government, as proposed by Student Body Treasurer Lanadia Adams.",
        "The document details a funding request from the Sustainable Funding Entrepreneurship Club for $1,200 to cover rental costs for a 3-D printing Makerspace, general supplies, and a pavilion venue. The expenses are anticipated before January 10, 2025. The Student Body Treasurer has verified the organization's eligibility and compliance with budgetary policies. It outlines conditions for funding, including deadlines for submitting receipts and funds, adherence to allocated amounts, and the authority of the Student Body Treasurer regarding amendments and exemptions related to the funding. All expenditures must comply with relevant guidelines from NC State Student Government, the university, and the state of North Carolina.",
        "The North Carolina State University Student Senate has confirmed Jean-Luc Theard as Treasury Official for the 104th Session of Student Government, following his appointment by Student Body Treasurer Lanadia Adams.",
        "The document outlines concerns regarding the current fast-tracking process for legislation within the Student Senate, as stipulated in the Student Body Statutes. It highlights that fast-tracking allows Senators to bypass formal readings and committee discussions, leading to potential issues, such as lack of debate before voting. If legislation fails to pass during the second reading, it cannot be further discussed unless reintroduced. The text emphasizes the importance of thorough review for all legislative actions and initiatives to ensure fair advocacy opportunities within the Senate, both during the current 104th session and in future sessions.",
        "The document recognizes the history and significance of the Future Farmers of America (FFA), highlighting key developments such as the establishment of vocational agriculture courses in 1917, the adoption of the FFA Creed, the iconic blue jacket, and the merger with the New Farmers of America in 1965. It resolves to officially recognize February 15 - 22, 2025, as National FFA Week. Each day of the week is designated for specific activities: SAE Sunday, Day of Service, Alumni Day, Advisor Appreciation Day, Give FFA Day, and Wear Blue Day. Additionally, the North Carolina State University Student Government expresses its support for agricultural education throughout North Carolina and plans to share this legislation with various stakeholders, including the National FFA Advisor and relevant university faculty.",
        "The document outlines the financial regulations and requirements for a student organization receiving funding from Student Government. Key points include:\n\n- The organization must submit receipts and unspent funds to the Student Body Treasurer by March 25, 2025, to be eligible for future funding.\n- The Spending Period for the allocated funds extends from receipt until the aforementioned deadline for submission.\n- Allocated funds must adhere to specified line item descriptions to qualify for future funding.\n- The Student Body Treasurer has exclusive authority to approve changes to line item descriptions and amend certain details related to funding requests after the bill's passage.\n- Exemptions to the Spending Period can be granted solely by the Student Body Treasurer.\n- All expenditures must comply with NC State Student Government, university, and North Carolina state spending guidelines. \n\nThe organization had its status verified and presented a Grant Request, thus enabling the enactment of these provisions.",
        "The North Carolina State University Student Senate has confirmed Samantha Reed as a member of the Board of Elections Commissioner, a position appointed by Student Body President Allison W. Marker. Her term will last until the end of the Spring 2026 semester.",
        "The document outlines the need for establishing a permanent International Affairs Department at NC State University, driven by several key points. It highlights the effectiveness of the Select Department of Student Support for Global Conflicts (SSGC) in raising awareness and supporting students affected by global issues. The document emphasizes the growing presence of international students and the necessity for a robust infrastructure to support them. Establishing a permanent department would enhance the university's mission by providing continuous advocacy and professional development opportunities, ensuring representation of global concerns in decision-making processes.\n\nThe proposed department aims to foster collaboration with international stakeholders, address unique challenges faced by international students, and integrate global perspectives into campus culture. Additionally, it would improve the university's competitiveness on a global scale and position it to tackle various global challenges. The department would also collaborate with existing university initiatives to strengthen partnerships and provide comprehensive support services to international students.\n\nUltimately, the document calls for the NC State University Student Government to enact the establishment of this permanent International Affairs Department, integrating the SSGC's mission to ensure the expansion and continuity of its initiatives.",
        "The document outlines a resolution enacted by the North Carolina State University Student Senate regarding the Appropriations Packet for the Spring Break 2025 to Fall Break 2025 cycle. On November 20, 2024, the Finance Committee approved the timeline and the appropriations process. The Student Body Treasurer and Deputy Treasurer conducted thorough verifications of Registered Student Organizations (RSOs), eligibility, attendance at required Budget Tool Sessions, and compliance of submitted budgets with appropriations policies.\n\nA total of 355 student organizations requested funding amounting to $436,991.00, but 25 organizations were deemed ineligible for various reasons, including failure to attend required sessions or interviews and submission of invalid applications. The Senate allocated $129,988 for the appropriations cycle from existing funds and stipulated guidelines for spending, receipt submission, and return of unspent funds to ensure eligibility for future funding. The Student Body Treasurer is granted authority over amendments and exemptions related to these funds. Any outstanding funds due after the bill's passage are to be incorporated into the allocation.",
        "The document addresses the governance structure of the Student Senate, particularly focusing on the appointment and removal of Chairs for Standing Committees by the Student Senate President. It highlights the lack of internal checks and balances in this process, allowing the President to make decisions without Senate consent, despite the significant influence these Chairs hold. The legislation aims to establish necessary checks by requiring the Senate's consent for such appointments and removals, emphasizing the need to limit the President's absolute power. However, the legislation is not retroactive, meaning it will not affect the current Chairs of the 104th Session of Student Government.",
    ]

    for i in range(len(docs)):
        docs[i] = Document(page_content=summaries[i], metadata=docs[i].metadata)

    vector_store.add_documents(documents=docs, ids=ids)
