import argparse
import os
from cve_importer import cve
from langchain_ollama import OllamaLLM
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, BOOLEAN, KEYWORD
from whoosh.qparser import MultifieldParser
from whoosh.query import Every

# Define the LLM model to be used
llm_model = "llama3.2:1b"

# Define the schema for Whoosh
schema = Schema(
    id=ID(stored=True, unique=True),
    description=TEXT(stored=True),
    impact=TEXT(stored=True),
    severity=KEYWORD(stored=True),
    exploited=BOOLEAN(stored=True)
)

# Create an index directory
index_dir = os.path.join(os.getcwd(), "whoosh_index")
if not os.path.exists(index_dir):
    os.mkdir(index_dir)

def create_index():
    """Create or update a Whoosh index with CVE data."""
    cve_data = cve.fetch()
    # Check if the index exists
    if index.exists_in(index_dir):
        ix = index.open_dir(index_dir)
    else:
        ix = index.create_in(index_dir, schema)
    writer = ix.writer()
    for cve_item in cve_data:
        print("writing item")
        writer.update_document(
            id=cve_item['id'],
            description=cve_item['description'],
            impact=cve_item['impact'],
            severity=cve_item['severity'],
            exploited=cve_item['exploited']
        )
    writer.commit()
    print("CVE data has been indexed into Whoosh")

def search_index(query_text, n_results=5):
    """Search the Whoosh index for relevant documents."""
    ix = index.open_dir(index_dir)
    
    if query_text.lower() == "all":
        query = Every()
    else:
        qp = MultifieldParser(["description", "severity", "impact"], ix.schema)
        query = qp.parse(query_text)
    
    with ix.searcher() as searcher:
        results = searcher.search(query, limit=n_results)
        documents = [hit.fields() for hit in results]
        return documents

def query_ollama(prompt):
    """Send a query to Ollama and retrieve the response."""
    llm = OllamaLLM(model=llm_model)
    return llm.invoke(prompt)

# RAG pipeline: Combine Whoosh and Ollama for Retrieval-Augmented Generation
def rag_pipeline(whoosh_query, ollama_prompt):
    """Perform Retrieval-Augmented Generation (RAG) by combining Whoosh and Ollama."""
    # Step 1: Retrieve relevant documents from Whoosh
    retrieved_docs = search_index(whoosh_query, n_results=None if whoosh_query.lower() == "all" else 5)
    context = " ".join([doc['description'] for doc in retrieved_docs]) if retrieved_docs else "No relevant documents found."

    # Step 2: Send the query along with the context to Ollama
    augmented_prompt = f"Context: {context}\n\nQuestion: {ollama_prompt}\nAnswer:"
    print("######## Augmented Prompt ########")
    print(augmented_prompt)

    response = query_ollama(augmented_prompt)
    return response

def main():
    parser = argparse.ArgumentParser(description="Manage CVE data and query Ollama.")
    parser.add_argument('--update', action='store_true', help="Update Whoosh index with new CVE data.")
    parser.add_argument('--whoosh_query', type=str, required=True, help="The query for Whoosh.")
    parser.add_argument('--ollama_prompt', type=str, required=True, help="The prompt for Ollama.")
    args = parser.parse_args()

    if args.update:
        create_index()

    response = rag_pipeline(args.whoosh_query, args.ollama_prompt)
    print("######## Response from LLM ########\n", response)

if __name__ == "__main__":
    main()
