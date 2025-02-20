import os
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, BOOLEAN, KEYWORD
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser

# Define the schema for Whoosh
schema = Schema(
    id=ID(stored=True, unique=True),
    description=TEXT(stored=True),
    impact=TEXT(stored=True),
    severity=KEYWORD(stored=True),
    exploited=BOOLEAN(stored=True)
)

# Create an index directory
index_dir = os.path.join(os.getcwd(), "whoosh_cve_index")

def search_index(query_text, n_results=5):
    """Search the Whoosh index for relevant documents."""
    ix = index.open_dir(index_dir)
    # Use MultiFieldParser to allow querying multiple fields
    qp = QueryParser("description", schema=ix.schema)
    q = qp.parse(query_text)
    with ix.searcher() as searcher:
        results = searcher.search(q, limit=n_results)
        documents = [hit.fields() for hit in results]
        return documents

def main():
    while True:
        query_text = input("query > ")
        if query_text.lower() in ['exit', 'quit']:
            break
        results = search_index(query_text)
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            for key, value in result.items():
                print(f"{key}: {value}")
            print("\n")

if __name__ == "__main__":
    main()
