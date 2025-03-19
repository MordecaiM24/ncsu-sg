from retrieval import retrieve
from indexing import index_documents

if __name__ == "__main__":
    # action = input("Enter action (index/retrieve): ")
    action = "retrieve"
    if action == "index":
        index_documents()
    elif action == "retrieve":
        query = input("Enter query: ")
        results = retrieve(query)
        print(results)
    else:
        print("Invalid action")
