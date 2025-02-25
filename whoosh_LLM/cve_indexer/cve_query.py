import argparse
import os
from cve_importer import cve
from langchain_ollama import OllamaLLM
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, BOOLEAN, KEYWORD
from whoosh.qparser import QueryParser
from whoosh.query import Every

# Define the LLM model to be used
llm_model = "llama3.2:3b"

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
            description=cve_item['description'].strip(),
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
        qp = QueryParser("description", ix.schema)
        query = qp.parse(query_text)
    
    with ix.searcher() as searcher:
        results = searcher.search(query, limit=n_results)
        documents = [hit.fields() for hit in results]
        return documents

def query_ollama(prompt, context_size):
    """Send a query to Ollama and retrieve the response."""
    llm = OllamaLLM(model=llm_model, num_ctx=context_size)
    return llm.invoke(prompt)

def get_response(whoosh_query, ollama_prompt, context_size):
    retrieved_docs = search_index(whoosh_query, n_results=None if whoosh_query.lower() == "all" else 5)
    context = " ".join([f"ID: {doc['id']}\nDescription: {doc['description']}\nSeverity: {doc['severity']}\nImpact: {doc['impact']}" for doc in retrieved_docs]) if retrieved_docs else "No relevant documents found."
    augmented_prompt = f"Context: {context}\n\nQuestion: {ollama_prompt}\nAnswer:"
    print(augmented_prompt)

    response = query_ollama(augmented_prompt, context_size)
    return response

def main():
    parser = argparse.ArgumentParser(description="Manage CVE data and query Ollama.")
    parser.add_argument('--update', action='store_true', help="Update Whoosh index with new CVE data.")
    parser.add_argument('--whoosh_query', type=str, required=True, help="The query for Whoosh.")
    parser.add_argument('--ollama_prompt', type=str, required=True, help="The prompt for Ollama.")
    parser.add_argument('--context_size', type=int, default=2048, help="The context size for Ollama.")
    args = parser.parse_args()

    if args.update:
        create_index()

    response = get_response(args.whoosh_query, args.ollama_prompt, args.context_size)
    print(response)

if __name__ == "__main__":
    main()
