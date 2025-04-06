import os
import json
from connection import get_summary_vector_store, get_chunk_vector_store
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import Document
from typing import List, Optional, Dict, Any, Tuple


def retrieve(query: str, k: int = 3, doc_id: Optional[str] = None) -> List[Document]:
    """
    Retrieve documents based on the query.

    Args:
        query: The search query
        k: Number of documents to retrieve
        doc_id: Optional document ID to restrict search to a specific document's chunks

    Returns:
        List of retrieved documents
    """
    if doc_id:
        return retrieve_chunks(query, doc_id, k)
    else:
        return retrieve_summaries(query, k)


def retrieve_summaries(query: str, k: int = 3) -> List[Document]:
    """
    Retrieve document summaries based on the query.

    Args:
        query: The search query
        k: Number of documents to retrieve

    Returns:
        List of retrieved documents
    """
    summary_vector_store = get_summary_vector_store()

    results = summary_vector_store.similarity_search(query, k=k)

    enhanced_results = []
    for doc in results:
        doc_id = doc.metadata["id"]

        file_path = f"cleaned_json/{doc_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                doc_json = json.load(f)
                full_text = doc_json.get("full_text", "")

                doc.metadata["excerpt"] = (
                    full_text[:500] + "..." if len(full_text) > 500 else full_text
                )

        enhanced_results.append(doc)

    return enhanced_results


def retrieve_chunks(query: str, doc_id: str, k: int = 5) -> List[Document]:
    """
    Retrieve chunks from a specific document based on the query.

    Args:
        query: The search query
        doc_id: Document ID to restrict search to
        k: Number of chunks to retrieve

    Returns:
        List of retrieved document chunks
    """
    chunk_vector_store = get_chunk_vector_store()

    filter_dict = {"doc_id": {"$eq": doc_id}}

    results = chunk_vector_store.similarity_search(query, k=k, filter=filter_dict)

    return results


def retrieve_with_reranking(query: str, doc_id: str, k: int = 5) -> List[Document]:
    """
    Retrieve chunks with query-aware reranking.

    Args:
        query: The search query
        doc_id: Document ID to restrict search to
        k: Number of chunks to retrieve

    Returns:
        List of retrieved and reranked document chunks
    """

    initial_k = min(k * 3, 20)
    initial_results = retrieve_chunks(query, doc_id, initial_k)

    if not initial_results:
        return []

    rerank_prompt = ChatPromptTemplate.from_template(
        """Given the following query and document chunk, rate how relevant the chunk is 
        to answering the query on a scale from 1-10, where 10 is highly relevant.
        
        Query: {query}
        
        Document chunk: {chunk}
        
        Rating (1-10):"""
    )

    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    rerank_chain = rerank_prompt | model | StrOutputParser()

    ratings = []
    for doc in initial_results:
        try:
            rating_str = rerank_chain.invoke(
                {"query": query, "chunk": doc.page_content}
            )
            rating = int("".join(filter(str.isdigit, rating_str)))
            ratings.append((doc, rating))
        except Exception as e:
            print(f"Error during reranking: {e}")
            ratings.append((doc, 5))

    sorted_results = [
        doc for doc, _ in sorted(ratings, key=lambda x: x[1], reverse=True)[:k]
    ]

    return sorted_results


def get_document_metadata(doc_id: str) -> Dict[str, Any]:
    """
    Get metadata for a specific document.

    Args:
        doc_id: Document ID

    Returns:
        Document metadata as a dictionary
    """
    file_path = f"cleaned_json/{doc_id}.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            doc_json = json.load(f)
            return {
                "id": doc_json.get("id"),
                "version": doc_json.get("version"),
                "long_title": doc_json.get("long_title"),
                "short_title": doc_json.get("short_title"),
                "sponsors": doc_json.get("sponsors"),
                "secondary_sponsors": doc_json.get("secondary_sponsors"),
                "first_reading": doc_json.get("first_reading"),
                "second_reading": doc_json.get("second_reading"),
                "result": doc_json.get("result"),
                "session": doc_json.get("session"),
            }
    return {}
