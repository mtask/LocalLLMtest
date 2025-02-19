import argparse
import os
import feedparser
from langchain_ollama import OllamaLLM
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME, KEYWORD
from whoosh.query import DateRange
from datetime import datetime, timedelta

# Define the LLM model to be used
llm_model = "llama3.2:1b"

class RssFeed:
    def __init__(self):
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

    def create_index(self, url):
        """Create or update a Whoosh index with RSS feed data."""
        feed = feedparser.parse(url)
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
        print(f"RSS feed data from {url} has been indexed into Whoosh")

    def search_index(self, days, n_results=5):
        """Search the Whoosh index for documents published within the given number of days."""
        ix = index.open_dir(self.index_dir)
        date_limit = datetime.now() - timedelta(days=days)
        query = DateRange("published", date_limit, datetime.now())
        with ix.searcher() as searcher:
            results = searcher.search(query, limit=n_results)
            documents = [hit.fields() for hit in results]
            return documents

def query_ollama(prompt, context_size):
    """Send a query to Ollama and retrieve the response."""
    llm = OllamaLLM(model=llm_model, context_size=context_size)
    return llm.invoke(prompt)

# RAG pipeline: Combine Whoosh and Ollama for Retrieval-Augmented Generation
def rag_pipeline(rss_feed, days, ollama_prompt, context_size):
    """Perform Retrieval-Augmented Generation (RAG) by combining Whoosh and Ollama."""
    # Step 1: Retrieve relevant documents from Whoosh
    retrieved_docs = rss_feed.search_index(days, n_results=5)
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
    parser.add_argument('--days', type=int, required=True, help="The number of days for retrieving data from Whoosh.")
    parser.add_argument('--ollama_prompt', type=str, required=True, help="The prompt for Ollama.")
    parser.add_argument('--context_size', type=int, default=2048, help="The context size for Ollama.")
    args = parser.parse_args()
    rss_urls = [
      "https://feeds.feedburner.com/TheHackersNews",
      "https://cvefeed.io/rssfeed/severity/high.xml",
      "https://cvefeed.io/rssfeed/newsroom.xml"]

    rss_feed = RssFeed()
    if args.update:
        for rss_url in rss_urls:
            rss_feed.create_index(rss_url)

    response = rag_pipeline(rss_feed, args.days, args.ollama_prompt, args.context_size)
    print(f"######## Response from LLM for RSS feed ########\n", response)

if __name__ == "__main__":
    main()

