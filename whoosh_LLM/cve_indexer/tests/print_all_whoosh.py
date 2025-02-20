import os
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, BOOLEAN, KEYWORD
from whoosh.qparser import QueryParser
from whoosh.query import Every

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

def print_all_cves():
    """Print all indexed CVEs from the Whoosh index."""
    if not index.exists_in(index_dir):
        print("No index found. Please create the index first.")
        return

    ix = index.open_dir(index_dir)
    with ix.searcher() as searcher:
        query = Every()
        results = searcher.search(query, limit=None)
        for i, hit in enumerate(results):
            print(f"Result {i+1}:")
            for key, value in hit.items():
                print(f"{key}: {value}")
            print("\n")

if __name__ == "__main__":
    print_all_cves()
