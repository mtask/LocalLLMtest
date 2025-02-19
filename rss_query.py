import argparse
import os
import feedparser
from langchain_ollama import OllamaLLM
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME, KEYWORD
from whoosh.qparser import QueryParser
from whoosh.query import Every
from datetime import datetime

# Define the LLM model to be used
llm_model = "llama3.2:1b"

class RssFeed:
    def __init__(self, url="https://feeds.feedburner.com/TheHackersNews"):
        self.url = url
        self.schema = Schema(
            id=ID(stored=True, unique=True),
            title=TEXT(stored=True),
            link=ID(stored=True),
            description=TEXT(stored=True),
            published=DATETIME(stored=True)
        )
        self.index_dir = os.path.join(os.getcwd(), "whoosh_rss_index")
        if not os.path.exists(self.index_dir):
            os.mkdir(self.index_dir)

    def create_index(self):
        """Create or update a Whoosh index with RSS feed data."""
        feed = feedparser.parse(self.url)
        # Check if the index exists
        if index.exists_in(self.index_dir):
            ix = index.open_dir(self.index_dir)
        else:
            ix = index.create_in(self.index_dir, self.schema)
        writer = ix.writer()
        for entry in feed.entries:
            published = datetime(*entry.published_parsed[:6]) if 'published_parsed' in entry else datetime.now()
            writer.update_document(
                id=entry.id,
                title=entry.title,
                link=entry.link,
                description=entry.description,
                published=published
            )
        writer.commit()
        print("RSS feed data has been indexed into Whoosh")

    def search_index(self, query_text, n_results=5):
        """Search the Whoosh index for relevant documents."""
        ix = index.open_dir(self.index_dir)
        
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
    llm = OllamaLLM(model=llm_model, context_size=context_size)
    return llm.invoke(prompt)

# RAG pipeline: Combine Whoosh and Ollama for Retrieval-Augmented Generation
def rag_pipeline(rss_feed, whoosh_query, ollama_prompt, context_size):
    """Perform Retrieval-Augmented Generation (RAG) by combining Whoosh and Ollama."""
    # Step 1: Retrieve relevant documents from Whoosh
    retrieved_docs = rss_feed.search_index(whoosh_query, n_results=None if whoosh_query.lower() == "all" else 5)
    context = " ".join([
        f"ID: {doc['id']}\nTitle: {doc['title']}\nLink: {doc['link']}\nDescription: {doc['description']}\nPublished: {doc['published']}"
        for doc in retrieved_docs
    ]) if retrieved_docs else "No relevant documents found."

    # Step 2: Send the query along with the context to Ollama
    augmented_prompt = f"Context: {context}\n\nQuestion: {ollama_prompt}\nAnswer:"
    print("######## Augmented Prompt ########")
    print(augmented_prompt)

    response = query_ollama(augmented_prompt, context_size)
    return response

def main():
    parser = argparse.ArgumentParser(description="Manage RSS feed data and query Ollama.")
    parser.add_argument('--update', action='store_true', help="Update Whoosh index with new RSS feed data.")
    parser.add_argument('--whoosh_query', type=str, required=True, help="The query for Whoosh.")
    parser.add_argument('--ollama_prompt', type=str, required=True, help="The prompt for Ollama.")
    parser.add_argument('--context_size', type=int, default=2048, help="The context size for Ollama.")
    parser.add_argument('--rss_url', type=str, default="https://feeds.feedburner.com/TheHackersNews", help="The URL of the RSS feed.")
    args = parser.parse_args()

    rss_feed = RssFeed(url=args.rss_url)

    if args.update:
        rss_feed.create_index()

    response = rag_pipeline(rss_feed, args.whoosh_query, args.ollama_prompt, args.context_size)
    print("######## Response from LLM ########\n", response)

if __name__ == "__main__":
    main()
